import queue
import tkinter as tk
from tkinter import ttk

# Import core components
from core import DataManager, AnalysisWorker, BotWorker

# Import tab classes
from gui.tabs import SetupTab, ColorsTab, ControlTab, PreviewTab

# Constants
MAX_MESSAGES_PER_CYCLE = 10
QUEUE_PROCESS_INTERVAL = 100  # milliseconds
DEFAULT_WINDOW_SIZE = "800x800"

class PlaceBotGUI:
    """Main GUI application for Place Bot"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Place Bot - Pixel Art Automation")
        self.root.geometry(DEFAULT_WINDOW_SIZE)
        
        # Initialize core components
        self.data_manager = DataManager()
        self.analysis_worker = AnalysisWorker(self.data_manager)
        self.bot_worker = BotWorker(self.data_manager)
        
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
        self.process_queue()
    
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
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        self._create_tabs(notebook)

    def _save_preferences(self):
        """Save UI preferences to data manager"""
        if self.setup_tab:
            self.data_manager.update_preference('color_tolerance', self.setup_tab.tolerance_var.get())
            self.data_manager.update_preference('click_delay', self.setup_tab.delay_var.get())
        
        if self.control_tab:
            self.data_manager.update_preference('pixel_limit', self.control_tab.pixel_limit_var.get())
    
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
        """Load and display saved regions - delegated to setup tab"""
        if self.setup_tab:
            self.setup_tab._load_saved_regions()

    def get_enabled_colors(self):
        """Get list of enabled colors from colors tab"""
        if self.colors_tab:
            return self.colors_tab.get_enabled_colors()
        return []
    
    def log_message(self, message):
        """Delegate to control tab"""
        if self.control_tab:
            self.control_tab.log_message(message)

    def _handle_log_message(self, message):
        """Handle log message"""
        self.log_message(message['message'])
    
    def _handle_analysis_complete(self, message):
        """Handle analysis complete message"""
        if self.setup_tab:
            self.setup_tab.on_analysis_complete(message)
        if self.control_tab:
            self.control_tab.enable_start_button()
        if self.preview_tab:
            self.preview_tab.update_stats()
        self.log_message(
            f"Analysis completed successfully. Found {message['pixel_count']} pixels "
            f"and {message['colors_found']} colors."
        )
    
    def _handle_analysis_error(self, message):
        """Handle analysis error message"""
        if self.setup_tab:
            self.setup_tab.on_analysis_error(message)
        self.log_message(f"Analysis failed: {message['error']}")
    
    def _handle_progress(self, message):
        """Handle progress message"""
        if self.control_tab:
            self.control_tab.update_progress(message['progress'], message['status'])
    
    def _handle_bot_complete(self, message):
        """Handle bot complete message"""
        total_painted = message.get('total_painted', 0)
        limit_reached = message.get('limit_reached', False)
        if self.control_tab:
            self.control_tab.on_bot_complete(total_painted, limit_reached)
    
    def _handle_bot_error(self, message):
        """Handle bot error message"""
        if self.control_tab:
            self.control_tab.on_bot_error(message['error'])
    
    def process_queue(self):
        """Process messages from worker threads"""
        message_handlers = {
            'log': self._handle_log_message,
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
        print(f"Failed to start GUI application: {e}")
        print("Please ensure tkinter is properly installed and display is available.")
        return 1
    return 0


if __name__ == "__main__":
    main()