import tkinter as tk
from tkinter import ttk, messagebox

class ControlTab:
    """Control tab for running the bot"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.data_manager = main_window.data_manager
        self.bot_worker = main_window.bot_worker
        self.message_queue = main_window.message_queue
        
        # Create the tab frame
        self.frame = ttk.Frame(parent)
        
        # UI elements that need to be accessed from main window
        self.status_label = None
        self.progress_var = None
        self.progress_bar = None
        self.start_btn = None
        self.log_text = None
        self.pixel_limit_var = None
        self.pixel_limit_entry = None
        self.pixel_limit_scale = None
        self.reanalyze_var = None
        
        # Create the UI
        self._create_ui()
    
    def _create_ui(self):
        """Create control tab UI"""
        self._create_status_frame()
        self._create_bot_settings()
        self._create_log_frame()
    
    def _create_status_frame(self):
        """Create status frame"""
        status_frame = ttk.LabelFrame(self.frame, text="Status", padding=10)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Ready", font=('Arial', 12, 'bold'))
        self.status_label.pack(pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill='x', pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(status_frame)
        button_frame.pack(pady=10)
        
        self.start_btn = ttk.Button(button_frame, text="Start Painting", 
                                   command=self._start_bot, state='disabled')
        self.start_btn.pack(pady=5)
        
        # Mouse movement cancellation info
        cancel_info = ttk.Label(status_frame, text="Move mouse to cancel bot", 
                               foreground='blue', font=('Arial', 9, 'italic'))
        cancel_info.pack(pady=(5, 0))
    
    def _create_bot_settings(self):
        """Create bot settings frame"""
        bot_settings_frame = ttk.LabelFrame(self.frame, text="Bot Settings", padding=10)
        bot_settings_frame.pack(fill='x', padx=10, pady=5)
        
        # Pixel limit setting
        limit_frame = ttk.Frame(bot_settings_frame)
        limit_frame.pack(fill='x', pady=5)
        
        ttk.Label(limit_frame, text="Pixel Limit (stop after painting):").pack(side='left')
        
        saved_pixel_limit = self.data_manager.user_settings['preferences'].get('pixel_limit', 50)
        self.pixel_limit_var = tk.IntVar(value=saved_pixel_limit)
        
        # Register validation function
        vcmd = (self.parent.register(self._validate_digit_input), '%P')
        
        self.pixel_limit_entry = ttk.Entry(limit_frame, textvariable=self.pixel_limit_var, width=8,
                                          validate='key', validatecommand=vcmd)
        self.pixel_limit_entry.pack(side='right', padx=(5, 0))
        self.pixel_limit_entry.bind('<KeyRelease>', self._on_pixel_limit_entry_change)
        self.pixel_limit_entry.bind('<FocusOut>', self._on_pixel_limit_entry_change)
        
        # Setup validation styles
        self._setup_validation_styles()
        
        ttk.Label(limit_frame, text="pixels").pack(side='right', padx=(5, 5))
        
        # Pixel limit slider
        slider_frame = ttk.Frame(bot_settings_frame)
        slider_frame.pack(fill='x', pady=2)
        
        ttk.Label(slider_frame, text="Quick Select:").pack(side='left')
        self.pixel_limit_scale = ttk.Scale(slider_frame, from_=1, to=1000, 
                                          variable=self.pixel_limit_var, orient='horizontal',
                                          command=self._update_pixel_limit_from_slider)
        self.pixel_limit_scale.pack(side='right', fill='x', expand=True, padx=(10, 0))
        
        # Start options
        options_frame = ttk.Frame(bot_settings_frame)
        options_frame.pack(fill='x', pady=(10, 0))
        
        saved_reanalyze = self.data_manager.user_settings['preferences'].get('reanalyze_before_start', True)
        self.reanalyze_var = tk.BooleanVar(value=saved_reanalyze)
        
        reanalyze_cb = ttk.Checkbutton(options_frame, text="Reanalyze before starting", 
                                      variable=self.reanalyze_var, 
                                      command=self._on_reanalyze_change)
        reanalyze_cb.pack(side='left')
        
        # Update button state after creating checkbox
        self._update_start_button_state()
    
    def _create_log_frame(self):
        """Create log frame"""
        log_frame = ttk.LabelFrame(self.frame, text="Log", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, state='disabled')
        log_scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        log_scrollbar.pack(side='right', fill='y')
    
    def _update_pixel_limit_from_slider(self, value):
        """Update pixel limit when slider changes"""
        new_value = int(float(value))
        self.pixel_limit_var.set(new_value)
        
        # Update field styling when slider changes
        if 1 <= new_value <= 1000:
            self.pixel_limit_entry.config(style='TEntry')
        else:
            self.pixel_limit_entry.config(style='Warning.TEntry')
        
        self._debounced_save()
    
    def _validate_digit_input(self, value):
        """Validate that input contains only digits"""
        if value == "":
            return True  # Allow empty string
        return value.isdigit()
    
    def _debounced_save(self):
        """Save settings with debouncing to prevent UI freezing"""
        if hasattr(self, '_save_timer'):
            self.main_window.root.after_cancel(self._save_timer)
        self._save_timer = self.main_window.root.after(500, self.main_window.save_user_settings)
    
    def _on_pixel_limit_entry_change(self, event=None):
        """Handle manual entry changes for pixel limit with validation"""
        try:
            new_value = self.pixel_limit_var.get()
            if 1 <= new_value <= 1000:
                # Valid input - normal styling
                self.pixel_limit_entry.config(style='TEntry')
                self.pixel_limit_scale.set(new_value)
                self._debounced_save()
            else:
                # Out of range - warning styling
                self.pixel_limit_entry.config(style='Warning.TEntry')
        except tk.TclError:
            # This shouldn't happen with digit validation, but just in case
            self.pixel_limit_entry.config(style='Error.TEntry')
    
    def _start_bot(self):
        """Start the painting bot"""
        # Force immediate save of any pending changes before starting
        if hasattr(self, '_save_timer'):
            self.main_window.root.after_cancel(self._save_timer)
            self.main_window.save_user_settings()
        
        if self.reanalyze_var.get():
            self.log_message("Starting reanalysis before painting...")
            if self.main_window.setup_tab and hasattr(self.main_window.setup_tab, '_analyze_regions'):
                self._prepare_bot_start()
                self.main_window.setup_tab._analyze_regions()
            else:
                from tkinter import messagebox
                messagebox.showerror(
                    "Analysis Error", 
                    "Cannot perform reanalysis.\n\n"
                    "Possible solutions:\n"
                    "• Go to Setup tab and run analysis manually\n"
                    "• Uncheck 'Reanalyze before starting' option\n"
                    "• Restart the application"
                )
        else:
            if not self.data_manager.has_analysis_data():
                from tkinter import messagebox
                messagebox.showerror(
                    "No Analysis Data", 
                    "Analysis is required before starting the bot.\n\n"
                    "Please choose one of these options:\n\n"
                    "1. Check 'Reanalyze before starting' (recommended)\n"
                    "2. Go to Setup tab → Select regions → Run analysis\n\n"
                    "The bot needs to know where to paint and what colors are available."
                )
                return
            self._prepare_bot_start()
            self._execute_bot_start()
    
    def _prepare_bot_start(self):
        """Prepare UI for bot start"""
        self.main_window.is_running = True
        self.start_btn.config(state='disabled')
        self.status_label.config(text="Painting... (move mouse to cancel)")
        self.log_message("Starting painting bot... Move mouse to cancel.")
    
    def _execute_bot_start(self):
        """Execute the actual bot start"""
        enabled_colors = self.main_window.get_enabled_colors()
        
        # Check if pixel limit is valid before starting
        try:
            pixel_limit = self.pixel_limit_var.get()
            if not (1 <= pixel_limit <= 1000):
                from tkinter import messagebox
                messagebox.showerror(
                    "Invalid Pixel Limit", 
                    f"Pixel limit must be between 1 and 1000.\n\n"
                    f"Current value: {pixel_limit}\n\n"
                    f"Please adjust the value and try again."
                )
                self.pixel_limit_entry.focus_set()  # Focus the field for easy editing
                return
        except tk.TclError:
            from tkinter import messagebox
            messagebox.showerror(
                "Invalid Input", 
                "Please enter a valid number for pixel limit.\n\n"
                "• Only numbers are allowed (1-1000)\n"
                "• Clear the field and enter a new value\n"
                "• Use the slider for quick selection"
            )
            self.pixel_limit_entry.focus_set()
            return
        
        settings = {
            'pixel_limit': pixel_limit,
            'tolerance': self.main_window.setup_tab.tolerance_var.get(),
            'delay': self.main_window.setup_tab.delay_var.get()
        }
        self.bot_worker.start_bot(self.message_queue, enabled_colors, settings)
    
    def _on_reanalyze_change(self):
        """Handle reanalyze checkbox change"""
        self._debounced_save()
        self._update_start_button_state()
    
    def _update_start_button_state(self):
        """Update start button state based on analysis data and reanalyze checkbox"""
        # Enable if we have analysis data OR reanalyze is checked
        should_enable = self.data_manager.has_analysis_data() or self.reanalyze_var.get()
        self.start_btn.config(state='normal' if should_enable else 'disabled')
    

    
    def log_message(self, message):
        """Add message to log"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
    
    def update_progress(self, progress, status_text):
        """Update progress bar and status"""
        self.progress_var.set(progress)
        self.status_label.config(text=status_text)
    
    def on_bot_complete(self, total_painted, limit_reached):
        """Handle bot completion"""
        self.main_window.is_running = False
        self.start_btn.config(state='normal')
        
        if limit_reached:
            self.status_label.config(text=f"Pixel limit reached! ({total_painted} pixels)")
            self.log_message(f"Bot stopped - pixel limit reached! Total pixels painted: {total_painted}")
        else:
            self.status_label.config(text=f"Painting complete! ({total_painted} pixels)")
            self.log_message(f"Painting completed successfully! Total pixels painted: {total_painted}")
    
    def on_bot_error(self, error_message):
        """Handle bot error"""
        self.main_window.is_running = False
        self.start_btn.config(state='normal')
        self.status_label.config(text=f"Error: {error_message}")
        self.log_message(f"Bot error: {error_message}")
    
    def _setup_validation_styles(self):
        """Setup validation styles for input fields"""
        style = ttk.Style()
        style.configure('Warning.TEntry', fieldbackground='#fff3cd', bordercolor='#ffc107')
        style.configure('Error.TEntry', fieldbackground='#f8d7da', bordercolor='#dc3545')
    
    def enable_start_button(self):
        """Enable the start button (called after successful analysis)"""
        # Always enable the button after analysis
        self.start_btn.config(state='normal')
        
        # If this was triggered by reanalyze option, start the bot
        if self.main_window.is_running:
            self._execute_bot_start()