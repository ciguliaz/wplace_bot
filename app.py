import queue
import tkinter as tk
from tkinter import ttk

# Import core components
from core.data_manager import DataManager
from core.analysis_worker import AnalysisWorker
from core.bot_worker import BotWorker

# Import tab classes
from gui.tabs.setup_tab import SetupTab
from gui.tabs.colors_tab import ColorsTab
from gui.tabs.control_tab import ControlTab
from gui.tabs.preview_tab import PreviewTab

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
        
        # Tab references
        self.setup_tab_obj = None
        self.colors_tab_obj = None
        self.control_tab_obj = None
        self.preview_tab_obj = None
        
        # Thread communication
        self.message_queue = queue.Queue()
        
        # Setup UI and start processing
        self.setup_ui()
        self.load_saved_regions()
        self.process_queue()

    def setup_ui(self):
        """Create the main UI layout"""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create all tabs using the new classes
        self.setup_tab_obj = SetupTab(notebook, self)
        self.colors_tab_obj = ColorsTab(notebook, self)
        self.preview_tab_obj = PreviewTab(notebook, self)
        self.control_tab_obj = ControlTab(notebook, self)
        
        notebook.add(self.setup_tab_obj.frame, text="Setup")
        notebook.add(self.colors_tab_obj.frame, text="Color Control")
        notebook.add(self.preview_tab_obj.frame, text="Preview & Debug")
        notebook.add(self.control_tab_obj.frame, text="Bot Control")

    def save_user_settings(self):
        """Save user settings including UI state"""
        # Update preferences from UI
        if self.setup_tab_obj:
            self.data_manager.update_preference('color_tolerance', self.setup_tab_obj.tolerance_var.get())
            self.data_manager.update_preference('click_delay', self.setup_tab_obj.delay_var.get())
        
        if self.control_tab_obj:
            self.data_manager.update_preference('pixel_limit', self.control_tab_obj.pixel_limit_var.get())
        
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

    def _get_enabled_colors(self):
        """Get list of enabled colors from colors tab"""
        if self.colors_tab_obj:
            return self.colors_tab_obj.get_enabled_colors()
        return []
    
    def _log_message(self, message):
        """Delegate to control tab"""
        if self.control_tab_obj:
            self.control_tab_obj.log_message(message)

    def process_queue(self):
        """Process messages from worker threads"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                
                if message['type'] == 'log':
                    self._log_message(message['message'])
                
                elif message['type'] == 'analysis_complete':
                    self.setup_tab_obj.on_analysis_complete(message)
                    self.control_tab_obj.enable_start_button()
                    self.preview_tab_obj.update_stats()
                    self._log_message(
                        f"Analysis completed successfully. Found {message['pixel_count']} pixels "
                        f"and {message['colors_found']} colors."
                    )
                    
                elif message['type'] == 'analysis_error':
                    self.setup_tab_obj.on_analysis_error(message)
                    self._log_message(f"Analysis failed: {message['error']}")
                    
                elif message['type'] == 'progress':
                    self.control_tab_obj.update_progress(message['progress'], message['status'])
                    
                elif message['type'] == 'bot_complete':
                    total_painted = message.get('total_painted', 0)
                    limit_reached = message.get('limit_reached', False)
                    self.control_tab_obj.on_bot_complete(total_painted, limit_reached)
                    
                elif message['type'] == 'bot_error':
                    self.control_tab_obj.on_bot_error(message['error'])
                
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