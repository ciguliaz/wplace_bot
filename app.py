import queue
import tkinter as tk
from tkinter import ttk

# Import core components
from core import DataManager, AnalysisWorker, BotWorker

# Import tab classes
from gui.tabs import SetupTab, ColorsTab, ControlTab, PreviewTab

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
        self.setup_tab = None
        self.colors_tab = None
        self.control_tab = None
        self.preview_tab = None
        
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
        self.setup_tab = SetupTab(notebook, self)
        self.colors_tab = ColorsTab(notebook, self)
        self.preview_tab = PreviewTab(notebook, self)
        self.control_tab = ControlTab(notebook, self)
        
        notebook.add(self.setup_tab.frame, text="Setup")
        notebook.add(self.colors_tab.frame, text="Color Control")
        notebook.add(self.preview_tab.frame, text="Preview & Debug")
        notebook.add(self.control_tab.frame, text="Bot Control")

    def save_user_settings(self):
        """Save user settings including UI state"""
        # Update preferences from UI
        if self.setup_tab:
            self.data_manager.update_preference('color_tolerance', self.setup_tab.tolerance_var.get())
            self.data_manager.update_preference('click_delay', self.setup_tab.delay_var.get())
        
        if self.control_tab:
            self.data_manager.update_preference('pixel_limit', self.control_tab.pixel_limit_var.get())
        
        # Save color settings from colors tab
        if self.colors_tab:
            for color in self.data_manager.color_palette:
                color_id = str(color['id'])
                
                # Save enabled status
                if color['name'] in self.colors_tab.color_vars:
                    self.data_manager.set_color_setting(color_id, 'enabled', self.colors_tab.color_vars[color['name']].get())
                
                # Save bought status (only for premium colors)
                if color.get('premium', False) and color['name'] in self.colors_tab.bought_vars:
                    self.data_manager.set_color_setting(color_id, 'bought', self.colors_tab.bought_vars[color['name']].get())

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

    def process_queue(self):
        """Process messages from worker threads"""
        try:
            # Process max 10 messages per call to prevent GUI blocking
            for _ in range(10):
                message = self.message_queue.get_nowait()
                
                if message['type'] == 'log':
                    self.log_message(message['message'])
                
                elif message['type'] == 'analysis_complete':
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
                    
                elif message['type'] == 'analysis_error':
                    if self.setup_tab:
                        self.setup_tab.on_analysis_error(message)
                    self.log_message(f"Analysis failed: {message['error']}")
                    
                elif message['type'] == 'progress':
                    if self.control_tab:
                        self.control_tab.update_progress(message['progress'], message['status'])
                    
                elif message['type'] == 'bot_complete':
                    total_painted = message.get('total_painted', 0)
                    limit_reached = message.get('limit_reached', False)
                    if self.control_tab:
                        self.control_tab.on_bot_complete(total_painted, limit_reached)
                    
                elif message['type'] == 'bot_error':
                    if self.control_tab:
                        self.control_tab.on_bot_error(message['error'])
                
        except queue.Empty:
            pass
        
        self.root.after(100, self.process_queue)


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