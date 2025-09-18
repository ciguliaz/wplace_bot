import json
import os
import time
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import threading
import queue
import tkinter as tk
import cv2

# Add these imports at the top
from core.data_manager import DataManager
from core.analysis_worker import AnalysisWorker
from core.bot_worker import BotWorker
from gui.region_selector import RegionSelector
from gui.tabs.setup_tab import SetupTab
from gui.tabs.colors_tab import ColorsTab

class PlaceBotGUI:
    """Main GUI application for Place Bot"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Place Bot - Pixel Art Automation")
        self.root.geometry("800x800")
        
        # Initialize core components
        self.data_manager = DataManager()
        self.analysis_worker = AnalysisWorker(self.data_manager)
        self.bot_worker = BotWorker(self.data_manager)
        
        # State variables
        self.is_running = False
        
        # UI variables
        # Add reference to colors tab
        self.colors_tab_obj = None
        
        # Thread communication
        self.message_queue = queue.Queue()
        
        # Add reference to setup tab
        self.setup_tab_obj = None
        
        # Setup UI and start processing
        self.setup_ui()
        self.load_saved_regions()
        self.process_queue()

    # ==================== DATA MANAGEMENT (delegated to DataManager) ====================
    
    def save_user_settings(self):
        """Save user settings including UI state"""
        # Update preferences from UI
        if self.setup_tab_obj:
            self.data_manager.update_preference('color_tolerance', self.setup_tab_obj.tolerance_var.get())
            self.data_manager.update_preference('click_delay', self.setup_tab_obj.delay_var.get())
        self.data_manager.update_preference('pixel_limit', self.pixel_limit_var.get())
        
        # Save color settings from colors tab
        if self.colors_tab_obj:
            for color in self.data_manager.color_palette:
                color_id = str(color['id'])
                
                # Save enabled status
                if color['name'] in self.colors_tab_obj.color_vars:
                    self.data_manager.set_color_setting(color_id, 'enabled', self.colors_tab_obj.color_vars[color['name']].get())
                
                # Save bought status (only for premium colors)
                if color.get('premium', False) and color['name'] in self.colors_tab_obj.bought_vars:
                    self.data_manager.set_color_setting(color_id, 'bought', self.colors_tab_obj.bought_vars[color['name']].get())

    def load_saved_regions(self):
        """Load and display saved regions - delegated to setup tab"""
        if self.setup_tab_obj:
            self.setup_tab_obj._load_saved_regions()

    # ==================== UI SETUP ====================
    
    def setup_ui(self):
        """Create the main UI layout"""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create setup tab using the new class
        self.setup_tab_obj = SetupTab(notebook, self)
        notebook.add(self.setup_tab_obj.frame, text="Setup")
        
        # Create colors tab using the new class
        self.colors_tab_obj = ColorsTab(notebook, self)
        notebook.add(self.colors_tab_obj.frame, text="Color Control")
        
        # Create other tabs (keep existing for now)
        self.preview_tab = ttk.Frame(notebook)
        self.control_tab = ttk.Frame(notebook)
        
        notebook.add(self.preview_tab, text="Preview & Debug")
        notebook.add(self.control_tab, text="Bot Control")
        
        # Create tab content
        self._create_preview_tab()
        self._create_control_tab()

    # Remove these methods (now in ColorsTab):
    # - _create_colors_tab()
    # - _create_color_widgets()
    # - _toggle_bought_status()
    # - _update_color_label()
    # - _enable_all_colors()
    # - _disable_all_colors()
    # - _enable_only_free()
    # - _enable_available_colors()

    def _create_preview_tab(self):
        """Preview tab for showing debug images and analysis results"""
        # Image display
        image_frame = ttk.LabelFrame(self.preview_tab, text="Debug Images", padding=10)
        image_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Image selection
        img_select_frame = ttk.Frame(image_frame)
        img_select_frame.pack(fill='x', pady=5)
        
        self.image_var = tk.StringVar()
        image_combo = ttk.Combobox(img_select_frame, textvariable=self.image_var,
                                  values=["Size Estimation", "Palette Detection"],
                                  state="readonly")
        image_combo.pack(side='left', padx=5)
        image_combo.bind('<<ComboboxSelected>>', self._load_debug_image)
        
        ttk.Button(img_select_frame, text="Refresh", 
                  command=self._refresh_debug_images).pack(side='left', padx=5)
        
        self.image_label = ttk.Label(image_frame, text="No image selected")
        self.image_label.pack(expand=True)
        
        # Statistics
        stats_frame = ttk.LabelFrame(self.preview_tab, text="Analysis Results", padding=10)
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=8, state='disabled')
        stats_scrollbar = ttk.Scrollbar(stats_frame, command=self.stats_text.yview)
        self.stats_text.config(yscrollcommand=stats_scrollbar.set)
        
        self.stats_text.pack(side='left', fill='both', expand=True)
        stats_scrollbar.pack(side='right', fill='y')

    def _create_control_tab(self):
        """Control tab for running the bot"""
        # Status
        status_frame = ttk.LabelFrame(self.control_tab, text="Status", padding=10)
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
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="Stop", 
                                  command=self._stop_bot, state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        # Bot Settings
        self._create_bot_settings()
        
        # Log
        log_frame = ttk.LabelFrame(self.control_tab, text="Log", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, state='disabled')
        log_scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        log_scrollbar.pack(side='right', fill='y')

    def _create_bot_settings(self):
        """Create bot settings frame"""
        bot_settings_frame = ttk.LabelFrame(self.control_tab, text="Bot Settings", padding=10)
        bot_settings_frame.pack(fill='x', padx=10, pady=5)
        
        # Pixel limit setting
        limit_frame = ttk.Frame(bot_settings_frame)
        limit_frame.pack(fill='x', pady=5)
        
        ttk.Label(limit_frame, text="Pixel Limit (stop after painting):").pack(side='left')
        
        saved_pixel_limit = self.data_manager.user_settings['preferences'].get('pixel_limit', 50)
        self.pixel_limit_var = tk.IntVar(value=saved_pixel_limit)
        
        self.pixel_limit_entry = ttk.Entry(limit_frame, textvariable=self.pixel_limit_var, width=8)
        self.pixel_limit_entry.pack(side='right', padx=(5, 0))
        self.pixel_limit_entry.bind('<KeyRelease>', self._on_pixel_limit_entry_change)
        self.pixel_limit_entry.bind('<FocusOut>', self._on_pixel_limit_entry_change)
        
        ttk.Label(limit_frame, text="pixels").pack(side='right', padx=(5, 5))
        
        # Pixel limit slider
        slider_frame = ttk.Frame(bot_settings_frame)
        slider_frame.pack(fill='x', pady=2)
        
        ttk.Label(slider_frame, text="Quick Select:").pack(side='left')
        self.pixel_limit_scale = ttk.Scale(slider_frame, from_=1, to=1000, 
                                          variable=self.pixel_limit_var, orient='horizontal',
                                          command=self._update_pixel_limit_from_slider)
        self.pixel_limit_scale.pack(side='right', fill='x', expand=True, padx=(10, 0))

    def _update_pixel_limit_from_slider(self, value):
        """Update pixel limit when slider changes"""
        new_value = int(float(value))
        self.pixel_limit_var.set(new_value)
        self.save_user_settings()

    def _on_pixel_limit_entry_change(self, event=None):
        """Handle manual entry changes for pixel limit"""
        try:
            new_value = self.pixel_limit_var.get()
            new_value = max(1, min(1000, new_value))  # Clamp to valid range
            self.pixel_limit_var.set(new_value)
            self.pixel_limit_scale.set(new_value)
            self.save_user_settings()
        except tk.TclError:
            pass  # Invalid input, ignore

    # Remove the entire _create_setup_tab method (and all its helper methods):
    # - _create_setup_tab()
    # - _create_settings_frame()
    # - _update_tolerance_label()
    # - _update_delay_label()
    # - _select_canvas_region()
    # - _select_palette_region() 
    # - _on_canvas_region_selected()
    # - _on_palette_region_selected()
    # - _check_ready_for_analysis()
    # - _analyze_regions()

    # ==================== EVENT HANDLERS ====================
    
    def _toggle_bought_status(self, color):
        """Toggle bought status and save to user_settings.json"""
        try:
            color_name = color['name']
            color_id = str(color['id'])
            new_bought_status = self.bought_vars[color_name].get()
            
            # Update using data_manager
            self.data_manager.set_color_setting(color_id, 'bought', new_bought_status)  # FIXED: Use data_manager
            self._update_color_label(color, new_bought_status)
            
        except Exception as e:
            print(f"Failed to toggle bought status: {e}")

    def _update_color_label(self, color, is_bought):
        """Update specific color label using stored reference"""
        color_name = color['name']
        
        if color_name in self.color_labels:
            label_widget = self.color_labels[color_name]
            label_text = f"{color_name} ({'Premium' if color.get('premium', False) else 'Free'})"
            label_color = "green" if (not color.get('premium', False) or is_bought) else "red"
            label_widget.config(text=label_text, foreground=label_color)

    # ==================== COLOR MANAGEMENT ====================
    
    def _enable_all_colors(self):
        """Enable all colors"""
        for var in self.color_vars.values():
            var.set(True)
        self.save_user_settings()

    def _disable_all_colors(self):
        """Disable all colors"""
        for var in self.color_vars.values():
            var.set(False)
        self.save_user_settings()

    def _enable_only_free(self):
        """Enable only free colors"""
        for color in self.data_manager.color_palette:  # FIXED: Use data_manager
            is_free = not color.get('premium', False)
            if color['name'] in self.color_vars:
                self.color_vars[color['name']].set(is_free)
        self.save_user_settings()

    def _enable_available_colors(self):
        """Enable all available colors (free + bought premium colors)"""
        for color in self.data_manager.color_palette:  # FIXED: Use data_manager
            color_id = str(color['id'])
            color_settings = self.data_manager.user_settings['colors'].get(color_id, {})  # FIXED: Use data_manager
            is_bought = color_settings.get('bought', False) if color.get('premium', False) else True
            is_available = not color.get('premium', False) or is_bought
            
            if color['name'] in self.color_vars:
                self.color_vars[color['name']].set(is_available)
        self.save_user_settings()

    # ==================== ANALYSIS AND BOT ====================
    
    def _start_bot(self):
        """Start the painting bot"""
        if not self.data_manager.has_analysis_data():
            messagebox.showerror("Error", "Please run analysis first!")
            return
        
        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(text="Painting...")
        self._log_message("Starting painting bot...")
        
        # Get enabled colors and settings
        enabled_colors = self._get_enabled_colors()
        settings = {
            'pixel_limit': self.pixel_limit_var.get(),
            'tolerance': self.setup_tab_obj.tolerance_var.get(),  # Get from setup tab
            'delay': self.setup_tab_obj.delay_var.get()          # Get from setup tab
        }
        
        # Use the bot worker
        self.bot_worker.start_bot(self.message_queue, enabled_colors, settings)

    def _stop_bot(self):
        """Stop the painting bot"""
        self.is_running = False
        self.bot_worker.stop_bot()
        self.status_label.config(text="Stopping...")
        self._log_message("Stopping bot...")

    def _get_enabled_colors(self):
        """Get list of enabled colors from colors tab"""
        if self.colors_tab_obj:
            return self.colors_tab_obj.get_enabled_colors()
        return []
    
    # Remove these methods (they're now in the worker classes):
    # - _analyze_worker (moved to AnalysisWorker)
    # - _bot_worker (moved to BotWorker)  
    # - _paint_color (moved to BotWorker)
    
    # ==================== UI HELPERS ====================
    
    def _log_message(self, message):
        """Add message to log"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
    
    def _load_debug_image(self, event=None):
        """Load and display debug image"""
        image_type = self.image_var.get()
        filename_map = {
            "Size Estimation": "debug_size_estimation.png",
            "Palette Detection": "debug_palette.png"
        }
        
        filename = filename_map.get(image_type)
        if filename and os.path.exists(filename):
            try:
                img = Image.open(filename)
                img.thumbnail((600, 400), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.image_label.config(image=photo, text="")
                self.image_label.image = photo
            except Exception as e:
                self.image_label.config(text=f"Error loading image: {e}")
        else:
            self.image_label.config(text="Image not found. Run analysis first.")
    
    def _refresh_debug_images(self):
        """Refresh debug image list"""
        self._load_debug_image()
    
    def _update_stats(self):
        """Update statistics display"""
        if not self.data_manager.has_analysis_data():
            return
        
        # Get tolerance and delay from setup tab
        tolerance = self.setup_tab_obj.tolerance_var.get() if self.setup_tab_obj else 5
        delay = self.setup_tab_obj.delay_var.get() if self.setup_tab_obj else 20
        
        # Get enabled colors count from colors tab
        enabled_count = len(self.colors_tab_obj.color_vars) if self.colors_tab_obj else 0
        total_count = len(self.data_manager.color_palette)
        
        stats = f"""Analysis Results:
        
Pixel Size: {self.data_manager.pixel_size}x{self.data_manager.pixel_size}
Total Pixels Detected: {len(self.data_manager.pixel_map)}
Colors Found in Palette: {len(self.data_manager.color_position_map)}

Enabled Colors: {enabled_count}
Total Colors: {total_count}

Settings:
Color Tolerance: {tolerance}
Click Delay: {delay}ms
Pixel Limit: {self.pixel_limit_var.get()}
"""
        
        self.stats_text.config(state='normal')
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats)
        self.stats_text.config(state='disabled')

    # ==================== MESSAGE PROCESSING ====================
    
    def process_queue(self):
        """Process messages from worker threads"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                
                if message['type'] == 'log':
                    self._log_message(message['message'])
                
                elif message['type'] == 'analysis_complete':
                    self.setup_tab_obj.on_analysis_complete(message)
                    self.start_btn.config(state='normal')
                    self._update_stats()
                    self._log_message(
                        f"Analysis completed successfully. Found {message['pixel_count']} pixels "
                        f"and {message['colors_found']} colors."
                    )
                    
                elif message['type'] == 'analysis_error':
                    self.setup_tab_obj.on_analysis_error(message)
                    self._log_message(f"Analysis failed: {message['error']}")
                    
                elif message['type'] == 'progress':
                    self.progress_var.set(message['progress'])
                    self.status_label.config(text=message['status'])
                    
                elif message['type'] == 'bot_complete':
                    self.is_running = False
                    self.start_btn.config(state='normal')
                    self.stop_btn.config(state='disabled')
                    total_painted = message.get('total_painted', 0)
                    limit_reached = message.get('limit_reached', False)
                    
                    if limit_reached:
                        self.status_label.config(text=f"Pixel limit reached! ({total_painted} pixels)")
                        self._log_message(f"Bot stopped - pixel limit reached! Total pixels painted: {total_painted}")
                    else:
                        self.status_label.config(text=f"Painting complete! ({total_painted} pixels)")
                        self._log_message(f"Painting completed successfully! Total pixels painted: {total_painted}")
                    
                elif message['type'] == 'bot_error':
                    self.is_running = False
                    self.start_btn.config(state='normal')
                    self.stop_btn.config(state='disabled')
                    self.status_label.config(text=f"Error: {message['error']}")
                    self._log_message(f"Bot error: {message['error']}")
                
        except queue.Empty:
            pass
        
        self.root.after(100, self.process_queue)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = PlaceBotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()