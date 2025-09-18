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
        
        # UI variables
        # Add references to all tabs
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

    # ==================== DATA MANAGEMENT (delegated to DataManager) ====================
    
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

    # ==================== UI SETUP ====================
    
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

    # Remove these methods (now in respective tab classes):
    # - _create_preview_tab()
    # - _create_control_tab()
    # - _create_bot_settings()
    # - _update_pixel_limit_from_slider()
    # - _on_pixel_limit_entry_change()
    # - _start_bot()
    # - _stop_bot()
    # - _log_message()
    # - _load_debug_image()
    # - _refresh_debug_images()
    # - _update_stats()

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
        """Delegate to control tab"""
        if self.control_tab_obj:
            self.control_tab_obj.log_message(message)

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