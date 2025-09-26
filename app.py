import queue
import tkinter as tk
from tkinter import ttk

# Import core components
from core import DataManager, AnalysisWorker, BotWorker, get_logger, get_config

# Import tab classes
from gui.tabs import SetupTab, ColorsTab, ControlTab, PreviewTab

# Load configuration
config = get_config()

# Constants
MAX_MESSAGES_PER_CYCLE = 10
QUEUE_PROCESS_INTERVAL = 100  # milliseconds

class PlaceBotGUI:
    """Main GUI application for Place Bot"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Place Bot - Pixel Art Automation")
        self.root.geometry(config.get('ui.window_size', '900x700'))
        self.root.minsize(700, 550)
        
        # Professional window styling
        try:
            self.root.tk.call('tk', 'scaling', 1.0)  # Ensure consistent scaling
        except:
            pass
        
        # Center window on screen
        self._center_window()
        
        # Initialize core components first
        self.data_manager = DataManager()
        self.analysis_worker = AnalysisWorker(self.data_manager)
        self.bot_worker = BotWorker(self.data_manager)
        self.logger = get_logger()
        self.logger.set_gui_callback(self._gui_log_callback)
        
        # Font scaling (load from settings, default to Extra Large 125%)
        self.font_scale = self.data_manager.user_settings['preferences'].get('font_scale', 1.25)
        
        # Configure modern styling
        self._setup_styling()
        
        # State variables
        self.is_running = False
        
        # Tab references
        self.setup_tab = None
        self.colors_tab = None
        self.control_tab = None
        self.preview_tab = None
        
        # Thread communication
        self.message_queue = queue.Queue()
        
        # Setup UI and start processing
        self.setup_ui()
        self.load_saved_regions()
        self._setup_cleanup()
        self._setup_keyboard_shortcuts()
        self.process_queue()
    
    def _center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _setup_styling(self):
        """Setup modern UI styling"""
        style = ttk.Style()
        
        # Use modern theme
        try:
            style.theme_use('vista')  # Windows modern theme
        except:
            try:
                style.theme_use('clam')  # Cross-platform modern theme
            except:
                style.theme_use('default')
        
        # Professional fonts with scaling
        base_title_size = int(12 * self.font_scale)
        base_body_size = int(9 * self.font_scale)
        base_small_size = int(8 * self.font_scale)
        
        title_font = ('Segoe UI', base_title_size, 'bold')
        body_font = ('Segoe UI', base_body_size)
        small_font = ('Segoe UI', base_small_size)
        
        # Modern color palette
        colors = {
            'primary': '#0078d4',
            'success': '#107c10', 
            'error': '#d13438',
            'warning': '#ff8c00',
            'info': '#0078d4',
            'text': '#323130',
            'bg': '#faf9f8'
        }
        
        # Configure professional styles
        style.configure('Title.TLabel', font=title_font, foreground=colors['text'])
        style.configure('Success.TLabel', foreground=colors['success'], font=(body_font[0], body_font[1], 'bold'))
        style.configure('Error.TLabel', foreground=colors['error'], font=(body_font[0], body_font[1], 'bold'))
        style.configure('Warning.TLabel', foreground=colors['warning'], font=(body_font[0], body_font[1], 'bold'))
        style.configure('Info.TLabel', foreground=colors['info'], font=body_font)
        
        # Enhanced button styling
        style.configure('TButton', font=body_font, padding=(12, 6))
        style.map('TButton', 
                 background=[('active', colors['primary']),
                           ('pressed', '#106ebe')],
                 foreground=[('active', 'white')])
        
        # Professional notebook styling
        style.configure('TNotebook', background=colors['bg'])
        style.configure('TNotebook.Tab', font=body_font, padding=(12, 8))
        
        # Enhanced frame styling
        style.configure('TLabelframe', font=body_font)
        style.configure('TLabelframe.Label', font=(body_font[0], body_font[1], 'bold'))
        
        # All other label styles
        style.configure('TLabel', font=body_font)
        style.configure('TCheckbutton', font=body_font)
        style.configure('TRadiobutton', font=body_font)
        style.configure('TCombobox', font=body_font)
        style.configure('TEntry', font=body_font)
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Only Ctrl+S works reliably when app has focus
        self.root.bind('<Control-s>', lambda e: self.save_user_settings())
    
    def _setup_cleanup(self):
        """Setup cleanup handlers"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _on_closing(self):
        """Handle application closing"""
        # Stop any running operations
        if self.is_running:
            self.bot_worker.stop_bot()
        
        # Save settings before closing
        self.save_user_settings()
        config.save()
        
        # Close the application
        self.root.destroy()

    def _create_tabs(self, notebook):
        """Create and add all tabs to notebook"""
        tabs = [
            (SetupTab, "Setup", "setup_tab"),
            (ColorsTab, "Color Control", "colors_tab"),
            (PreviewTab, "Preview & Debug", "preview_tab"),
            (ControlTab, "Bot Control", "control_tab")
        ]
        
        for tab_class, title, attr_name in tabs:
            tab = tab_class(notebook, self)
            setattr(self, attr_name, tab)
            notebook.add(tab.frame, text=title)
    
    def setup_ui(self):
        """Create the main UI layout"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Menu bar
        self._create_menu_bar()
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        self._create_tabs(notebook)
        
        # Status bar
        self._create_status_bar(main_frame)
    
    def _create_status_bar(self, parent):
        """Create status bar at bottom"""
        self.status_frame = ttk.Frame(parent)
        self.status_frame.pack(fill='x', pady=(5, 0))
        
        # Status label with initial styling
        self.status_label = ttk.Label(self.status_frame, text="Ready", style='Info.TLabel')
        self.status_label.pack(side='left')
        
        # Separator
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=(2, 0))
    
    def _create_menu_bar(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Settings", command=self.save_user_settings, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Font size submenu
        font_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Font Size", menu=font_menu)
        font_menu.add_command(label="Tiny (80%)", command=lambda: self._change_font_size(0.8))
        font_menu.add_command(label="Small (90%)", command=lambda: self._change_font_size(0.9))
        font_menu.add_command(label="Normal (100%)", command=lambda: self._change_font_size(1.0))
        font_menu.add_command(label="Large (120%)", command=lambda: self._change_font_size(1.2))
        font_menu.add_command(label="Extra Large (125%)", command=lambda: self._change_font_size(1.25))
        font_menu.add_command(label="Huge (150%)", command=lambda: self._change_font_size(1.5))
        font_menu.add_command(label="Giant (200%)", command=lambda: self._change_font_size(2.0))
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Open Log File", command=self._open_log_file)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Keyboard Shortcuts", command=self._show_shortcuts)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _open_log_file(self):
        """Open log file in default editor"""
        import os
        import subprocess
        from datetime import datetime
        
        log_file = f"placebot_{datetime.now().strftime('%Y%m%d')}.log"
        if os.path.exists(log_file):
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(log_file)
                else:  # macOS and Linux
                    subprocess.call(['open' if os.name == 'posix' else 'xdg-open', log_file])
            except Exception as e:
                self.logger.error(f"Could not open log file: {e}")
        else:
            self.update_status("Log file not found", 'warning')
    
    def _show_shortcuts(self):
        """Show keyboard shortcuts dialog"""
        from tkinter import messagebox
        shortcuts = (
            "Keyboard Shortcuts:\n\n"
            "Ctrl+S - Save Settings\n\n"
            "Mouse Movement Cancellation:\n\n"
            "Move mouse to cancel bot while running"
        )
        messagebox.showinfo("Keyboard Shortcuts", shortcuts)
    
    def _show_about(self):
        """Show about dialog"""
        from tkinter import messagebox
        about_text = (
            "Place Bot v1.6.2\n\n"
            "Pixel Art Automation Tool for Wplace.live\n\n"
            "A Python GUI application for automating\n"
            "pixel art creation on wplace.live canvases."
        )
        messagebox.showinfo("About Place Bot", about_text)
    
    def _change_font_size(self, scale):
        """Change font size scaling"""
        self.font_scale = scale
        self._setup_styling()
        
        # Notify all tabs to refresh their fonts
        for tab in [self.setup_tab, self.colors_tab, self.control_tab, self.preview_tab]:
            if tab and hasattr(tab, 'refresh_fonts'):
                tab.refresh_fonts()
        
        # Save the font scale setting
        self.save_user_settings()
        self.update_status(f"Font size changed to {int(scale * 100)}%", 'info')
    
    def get_scaled_font(self, base_size, weight='normal'):
        """Get scaled font for tabs to use"""
        scaled_size = int(base_size * self.font_scale)
        return ('Segoe UI', scaled_size, weight)
    
    def update_status(self, message, status_type='info'):
        """Update status bar message"""
        if hasattr(self, 'status_label'):
            style_map = {
                'info': 'Info.TLabel',
                'success': 'Success.TLabel', 
                'error': 'Error.TLabel',
                'warning': 'Warning.TLabel'
            }
            self.status_label.config(text=message, style=style_map.get(status_type, 'TLabel'))

    def _save_preferences(self):
        """Save UI preferences to data manager"""
        if self.setup_tab:
            self.data_manager.update_preference('color_tolerance', self.setup_tab.tolerance_var.get())
            self.data_manager.update_preference('click_delay', self.setup_tab.delay_var.get())
        
        if self.control_tab:
            self.data_manager.update_preference('pixel_limit', self.control_tab.pixel_limit_var.get())
            self.data_manager.update_preference('reanalyze_before_start', self.control_tab.reanalyze_var.get())
        
        # Save font scale
        self.data_manager.update_preference('font_scale', self.font_scale)
    
    def _save_color_settings(self):
        """Save color settings from colors tab"""
        if not self.colors_tab:
            return
            
        for color in self.data_manager.color_palette:
            color_id = str(color['id'])
            
            # Save enabled status
            if color['name'] in self.colors_tab.color_vars:
                self.data_manager.set_color_setting(
                    color_id, 'enabled', 
                    self.colors_tab.color_vars[color['name']].get()
                )
            
            # Save bought status (only for premium colors)
            if color.get('premium', False) and color['name'] in self.colors_tab.bought_vars:
                self.data_manager.set_color_setting(
                    color_id, 'bought', 
                    self.colors_tab.bought_vars[color['name']].get()
                )
    
    def save_user_settings(self):
        """Save user settings including UI state"""
        self._save_preferences()
        self._save_color_settings()

    def load_saved_regions(self):
        """Load and display saved regions"""
        if self.setup_tab:
            self.setup_tab._load_saved_regions()

    def get_enabled_colors(self):
        """Get list of enabled colors from colors tab"""
        if self.colors_tab:
            return self.colors_tab.get_enabled_colors()
        return []
    
    def _gui_log_callback(self, message):
        """Callback for logger to display messages in GUI"""
        if self.control_tab:
            self.control_tab.log_message(message)


    def _handle_analysis_complete(self, message):
        """Handle analysis complete message"""
        if self.setup_tab:
            self.setup_tab.on_analysis_complete(message)
        if self.control_tab:
            self.control_tab.enable_start_button()
        if self.preview_tab:
            self.preview_tab.update_stats()
        self.logger.analysis_complete(message['pixel_count'], message['colors_found'])
        self.update_status(f"Analysis complete: {message['pixel_count']} pixels, {message['colors_found']} colors", 'success')
    
    def _handle_analysis_error(self, message):
        """Handle analysis error message"""
        if self.setup_tab:
            self.setup_tab.on_analysis_error(message)
        self.logger.analysis_error(message['error'])
        self.update_status(f"Analysis failed: {message['error']}", 'error')
    
    def _handle_progress(self, message):
        """Handle progress message"""
        if self.control_tab:
            self.control_tab.update_progress(message['progress'], message['status'])
    
    def _handle_bot_complete(self, message):
        """Handle bot complete message"""
        total_painted = message.get('total_painted', 0)
        limit_reached = message.get('limit_reached', False)
        cancelled_by_mouse = message.get('cancelled_by_mouse', False)
        
        if self.control_tab:
            self.control_tab.on_bot_complete(total_painted, limit_reached)
        
        self.logger.bot_complete(total_painted, limit_reached)
        
        if cancelled_by_mouse:
            status_msg = f"Bot cancelled by mouse movement: {total_painted} pixels painted"
            self.update_status(status_msg, 'warning')
        else:
            status_msg = f"Painting complete: {total_painted} pixels" + (" (limit reached)" if limit_reached else "")
            self.update_status(status_msg, 'success')
    
    def _handle_bot_error(self, message):
        """Handle bot error message"""
        if self.control_tab:
            self.control_tab.on_bot_error(message['error'])
        self.logger.bot_error(message['error'])
        self.update_status(f"Bot error: {message['error']}", 'error')
    
    def process_queue(self):
        """Process messages from worker threads"""
        message_handlers = {
            'analysis_complete': self._handle_analysis_complete,
            'analysis_error': self._handle_analysis_error,
            'progress': self._handle_progress,
            'bot_complete': self._handle_bot_complete,
            'bot_error': self._handle_bot_error
        }
        
        try:
            # Process max messages per call to prevent GUI blocking
            for _ in range(MAX_MESSAGES_PER_CYCLE):
                message = self.message_queue.get_nowait()
                handler = message_handlers.get(message['type'])
                if handler:
                    handler(message)
                
        except queue.Empty:
            pass
        
        self.root.after(QUEUE_PROCESS_INTERVAL, self.process_queue)


def main():
    """Main entry point"""
    try:
        root = tk.Tk()
        app = PlaceBotGUI(root)
        root.mainloop()
    except Exception as e:
        logger = get_logger()
        logger.critical(f"Failed to start GUI application: {e}")
        logger.error("Please ensure tkinter is properly installed and display is available.")
        return 1
    return 0


if __name__ == "__main__":
    main()