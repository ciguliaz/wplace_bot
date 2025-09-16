import json
import os
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import threading
import queue
import tkinter as tk
import cv2

class RegionSelector:
    """Overlay window for drag-to-select region functionality"""
    def __init__(self, callback):
        self.callback = callback
        self.start_x = None
        self.start_y = None
        self.rect_id = None
        
        # Create fullscreen transparent overlay
        self.overlay = tk.Toplevel()
        self.overlay.attributes('-fullscreen', True)
        self.overlay.attributes('-alpha', 0.3)  # Semi-transparent
        self.overlay.attributes('-topmost', True)
        self.overlay.configure(bg='black')
        
        # Create canvas for drawing selection rectangle
        self.canvas = tk.Canvas(self.overlay, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.configure(bg='black')
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        
        # Bind escape key to cancel
        self.overlay.bind('<Escape>', self.cancel)
        self.overlay.focus_set()
        
        # Instructions
        instruction_text = "Drag to select region. Press ESC to cancel."
        self.canvas.create_text(
            self.overlay.winfo_screenwidth() // 2, 50,
            text=instruction_text,
            fill='white',
            font=('Arial', 16, 'bold')
        )
    
    def on_click(self, event):
        """Start selection"""
        self.start_x = event.x
        self.start_y = event.y
        
        # Remove previous rectangle if exists
        if self.rect_id:
            self.canvas.delete(self.rect_id)
    
    def on_drag(self, event):
        """Update selection rectangle while dragging"""
        if self.start_x is not None and self.start_y is not None:
            # Remove previous rectangle
            if self.rect_id:
                self.canvas.delete(self.rect_id)
            
            # Draw new rectangle
            self.rect_id = self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y,
                outline='red', width=2, fill='', stipple='gray25'
            )
    
    def on_release(self, event):
        """Finish selection and return coordinates"""
        if self.start_x is not None and self.start_y is not None:
            # Calculate region coordinates
            left = min(self.start_x, event.x)
            top = min(self.start_y, event.y)
            width = abs(event.x - self.start_x)
            height = abs(event.y - self.start_y)
            
            # Minimum size check
            if width > 10 and height > 10:
                region = (left, top, width, height)
                self.close()
                self.callback(region)
            else:
                # Too small, show message and continue
                self.canvas.create_text(
                    event.x, event.y - 20,
                    text="Region too small! Try again.",
                    fill='yellow',
                    font=('Arial', 12, 'bold')
                )
                self.start_x = None
                self.start_y = None
                if self.rect_id:
                    self.canvas.delete(self.rect_id)
                    self.rect_id = None
    
    def cancel(self, event=None):
        """Cancel selection"""
        self.close()
        self.callback(None)
    
    def close(self):
        """Close the overlay"""
        self.overlay.destroy()


class PlaceBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Place Bot - Pixel Art Automation")
        self.root.geometry("800x800")
        
        # Load data
        self.color_palette = self.load_color_palette()
        self.user_settings = self.load_user_settings()
        
        # State variables
        self.canvas_region = self.user_settings.get('preferences', {}).get('last_canvas_region')
        self.palette_region = self.user_settings.get('preferences', {}).get('last_palette_region')
        self.pixel_map = None
        self.color_position_map = None
        self.pixel_size = None
        self.is_running = False
        self.bot_thread = None
        
        # Message queue for thread communication
        self.message_queue = queue.Queue()
        
        self.setup_ui()
        self.process_queue()
        
        # Load saved regions if they exist
        self.load_saved_regions()

    def load_color_palette(self):
        """Load color palette from JSON file"""
        try:
            with open('colors.json', 'r') as f:
                data = json.load(f)
                return data['color_palette']
        except FileNotFoundError:
            messagebox.showerror("Error", "colors.json not found! Please create the color palette file.")
            return []
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load colors.json: {e}")
            return []

    def load_user_settings(self):
        """Load user settings from JSON file"""
        default_settings = {
            "bought_colors": {},
            "preferences": {
                "color_tolerance": 5,
                "click_delay": 20,
                "auto_save_regions": True
            },
            "enabled_colors": {}
        }
        
        try:
            if os.path.exists('user_settings.json'):
                with open('user_settings.json', 'r') as f:
                    settings = json.load(f)
                    # Merge with defaults to handle missing keys
                    for key in default_settings:
                        if key not in settings:
                            settings[key] = default_settings[key]
                    return settings
            else:
                return default_settings
        except Exception as e:
            print(f"Failed to load user settings: {e}")
            return default_settings

    def save_user_settings(self):
        """Save user settings to JSON file"""
        try:
            # Update settings with current values
            self.user_settings['preferences']['color_tolerance'] = self.tolerance_var.get()
            self.user_settings['preferences']['click_delay'] = self.delay_var.get()
            
            # Save current regions
            if self.canvas_region:
                self.user_settings['preferences']['last_canvas_region'] = self.canvas_region
            if self.palette_region:
                self.user_settings['preferences']['last_palette_region'] = self.palette_region
            
            # Save enabled colors
            for color in self.color_palette:
                if color['name'] in self.color_vars:
                    self.user_settings['enabled_colors'][color['name']] = self.color_vars[color['name']].get()
            
            # Save bought colors
            for color in self.color_palette:
                if color.get('premium', False) and color['name'] in self.bought_vars:
                    self.user_settings['bought_colors'][color['name']] = self.bought_vars[color['name']].get()
            
            with open('user_settings.json', 'w') as f:
                json.dump(self.user_settings, f, indent=2)
                
        except Exception as e:
            print(f"Failed to save user settings: {e}")

    def load_saved_regions(self):
        """Load and display saved regions"""
        if self.canvas_region:
            self.canvas_status.config(text=f"Loaded: {self.canvas_region}", foreground="blue")
        if self.palette_region:
            self.palette_status.config(text=f"Loaded: {self.palette_region}", foreground="blue")
        self.check_ready_for_analysis()

    def setup_ui(self):
        """Create the main UI layout"""
        # Create main container with tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Setup
        self.setup_tab = ttk.Frame(notebook)
        notebook.add(self.setup_tab, text="Setup")
        self.create_setup_tab()
        
        # Tab 2: Colors
        self.colors_tab = ttk.Frame(notebook)
        notebook.add(self.colors_tab, text="Color Control")
        self.create_colors_tab()
        
        # Tab 3: Preview
        self.preview_tab = ttk.Frame(notebook)
        notebook.add(self.preview_tab, text="Preview & Debug")
        self.create_preview_tab()
        
        # Tab 4: Control
        self.control_tab = ttk.Frame(notebook)
        notebook.add(self.control_tab, text="Bot Control")
        self.create_control_tab()
    
    def create_setup_tab(self):
        """Setup tab for region selection and analysis"""
        # Instructions frame
        instructions_frame = ttk.LabelFrame(self.setup_tab, text="Instructions", padding=10)
        instructions_frame.pack(fill='x', padx=10, pady=5)
        
        instructions_text = """How to select regions:
1. Click 'Select Canvas' or 'Select Palette' button
2. Your screen will show a dark overlay
3. Click and drag to select the desired region
4. Release mouse to confirm selection
5. Press ESC to cancel selection"""
        
        ttk.Label(instructions_frame, text=instructions_text, justify='left').pack(anchor='w')
        
        # Region Selection Frame
        region_frame = ttk.LabelFrame(self.setup_tab, text="Region Selection", padding=10)
        region_frame.pack(fill='x', padx=10, pady=5)
        
        # Canvas region
        canvas_frame = ttk.Frame(region_frame)
        canvas_frame.pack(fill='x', pady=5)
        
        ttk.Label(canvas_frame, text="Canvas Region:").pack(side='left')
        self.canvas_status = ttk.Label(canvas_frame, text="Not selected", foreground="red")
        self.canvas_status.pack(side='left', padx=(10, 0))
        
        ttk.Button(canvas_frame, text="Select Canvas", 
                  command=self.select_canvas_region).pack(side='right')
        
        # Palette region
        palette_frame = ttk.Frame(region_frame)
        palette_frame.pack(fill='x', pady=5)
        
        ttk.Label(palette_frame, text="Palette Region:").pack(side='left')
        self.palette_status = ttk.Label(palette_frame, text="Not selected", foreground="red")
        self.palette_status.pack(side='left', padx=(10, 0))
        
        ttk.Button(palette_frame, text="Select Palette", 
                  command=self.select_palette_region).pack(side='right')
        
        # Analysis Frame
        analysis_frame = ttk.LabelFrame(self.setup_tab, text="Analysis", padding=10)
        analysis_frame.pack(fill='x', padx=10, pady=5)
        
        self.analyze_btn = ttk.Button(analysis_frame, text="Analyze Canvas & Palette", 
                                     command=self.analyze_regions, state='disabled')
        self.analyze_btn.pack(pady=5)
        
        self.analysis_status = ttk.Label(analysis_frame, text="Select regions first")
        self.analysis_status.pack(pady=5)
        
        # Settings Frame
        settings_frame = ttk.LabelFrame(self.setup_tab, text="Settings", padding=10)
        settings_frame.pack(fill='x', padx=10, pady=5)
        
        # Load saved settings
        saved_tolerance = self.user_settings['preferences']['color_tolerance']
        saved_delay = self.user_settings['preferences']['click_delay']
        
        # Tolerance setting
        tolerance_frame = ttk.Frame(settings_frame)
        tolerance_frame.pack(fill='x', pady=2)
        ttk.Label(tolerance_frame, text="Color Tolerance:").pack(side='left')
        self.tolerance_var = tk.IntVar(value=saved_tolerance)
        tolerance_scale = ttk.Scale(tolerance_frame, from_=1, to=20, variable=self.tolerance_var, 
                                   orient='horizontal')
        tolerance_scale.pack(side='right', fill='x', expand=True, padx=(10, 0))
        
        # Tolerance value display
        self.tolerance_label = ttk.Label(tolerance_frame, text=str(saved_tolerance))
        self.tolerance_label.pack(side='right', padx=(5, 10))
        tolerance_scale.configure(command=self.update_tolerance_label)
        
        # Click delay setting
        delay_frame = ttk.Frame(settings_frame)
        delay_frame.pack(fill='x', pady=2)
        ttk.Label(delay_frame, text="Click Delay (ms):").pack(side='left')
        self.delay_var = tk.IntVar(value=saved_delay)
        delay_scale = ttk.Scale(delay_frame, from_=10, to=100, variable=self.delay_var, 
                               orient='horizontal')
        delay_scale.pack(side='right', fill='x', expand=True, padx=(10, 0))
        
        # Delay value display
        self.delay_label = ttk.Label(delay_frame, text=str(saved_delay))
        self.delay_label.pack(side='right', padx=(5, 10))
        delay_scale.configure(command=self.update_delay_label)
    
    def update_tolerance_label(self, value):
        """Update tolerance value display and save"""
        self.tolerance_label.config(text=f"{int(float(value))}")
        self.save_user_settings()

    def update_delay_label(self, value):
        """Update delay value display and save"""
        self.delay_label.config(text=f"{int(float(value))}")
        self.save_user_settings()
    
    def create_colors_tab(self):
        """Color control tab for enabling/disabling colors"""
        # Create scrollable frame for colors
        canvas = tk.Canvas(self.colors_tab)
        scrollbar = ttk.Scrollbar(self.colors_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Control buttons
        control_frame = ttk.Frame(self.colors_tab)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(control_frame, text="Enable All", 
                  command=self.enable_all_colors).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Disable All", 
                  command=self.disable_all_colors).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Only Free Colors", 
                  command=self.enable_only_free).pack(side='left', padx=5)
        ttk.Button(control_frame, text="Available Colors (Free + Bought)", 
                  command=self.enable_available_colors).pack(side='left', padx=5)
        
        # Create color checkboxes
        self.color_vars = {}
        self.bought_vars = {}
        
        for color in self.color_palette:
            color_frame = ttk.Frame(scrollable_frame)
            color_frame.pack(fill='x', padx=10, pady=2)
            
            # Color preview
            color_canvas = tk.Canvas(color_frame, width=30, height=20)
            color_canvas.pack(side='left', padx=5)
            
            rgb = color['rgb']
            hex_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
            color_canvas.create_rectangle(0, 0, 30, 20, fill=hex_color, outline="")
            
            # Load saved state
            is_bought = self.user_settings['bought_colors'].get(color['name'], False)
            is_enabled = self.user_settings['enabled_colors'].get(color['name'], 
                        not color.get('premium', False) or is_bought)
            
            # Enable/disable checkbox
            var = tk.BooleanVar(value=is_enabled)
            self.color_vars[color['name']] = var
            
            checkbox = ttk.Checkbutton(color_frame, variable=var, command=self.save_user_settings)
            checkbox.pack(side='left', padx=5)
            
            # Color name label
            label_text = color['name']
            if color.get('premium', False):
                if is_bought:
                    label_text += " (Premium - Bought)"
                    label_color = "green"
                else:
                    label_text += " (Premium - Not Bought)"
                    label_color = "red"
            else:
                label_text += " (Free)"
                label_color = "blue"
            
            name_label = ttk.Label(color_frame, text=label_text, foreground=label_color)
            name_label.pack(side='left', padx=5)
            
            # Bought status toggle (only for premium colors)
            if color.get('premium', False):
                bought_var = tk.BooleanVar(value=is_bought)
                self.bought_vars[color['name']] = bought_var
                
                bought_checkbox = ttk.Checkbutton(
                    color_frame, 
                    text="Bought", 
                    variable=bought_var,
                    command=lambda c=color: self.toggle_bought_status(c)
                )
                bought_checkbox.pack(side='left', padx=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def toggle_bought_status(self, color):
        """Toggle bought status and save settings"""
        self.save_user_settings()
        self.refresh_colors_tab()

    def refresh_colors_tab(self):
        """Refresh the colors tab to show updated bought status"""
        for widget in self.colors_tab.winfo_children():
            widget.destroy()
        self.create_colors_tab()

    def enable_available_colors(self):
        """Enable all available colors (free + bought premium colors)"""
        for color in self.color_palette:
            is_bought = self.user_settings['bought_colors'].get(color['name'], False)
            is_available = not color.get('premium', False) or is_bought
            if color['name'] in self.color_vars:
                self.color_vars[color['name']].set(is_available)
        self.save_user_settings()

    def enable_only_free(self):
        """Enable only free colors"""
        for color in self.color_palette:
            is_free = not color.get('premium', False)
            if color['name'] in self.color_vars:
                self.color_vars[color['name']].set(is_free)
        self.save_user_settings()

    def enable_all_colors(self):
        for var in self.color_vars.values():
            var.set(True)
        self.save_user_settings()

    def disable_all_colors(self):
        for var in self.color_vars.values():
            var.set(False)
        self.save_user_settings()

    def create_preview_tab(self):
        """Preview tab for showing debug images and analysis results"""
        # Image display frame
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
        image_combo.bind('<<ComboboxSelected>>', self.load_debug_image)
        
        ttk.Button(img_select_frame, text="Refresh", 
                  command=self.refresh_debug_images).pack(side='left', padx=5)
        
        # Image display
        self.image_label = ttk.Label(image_frame, text="No image selected")
        self.image_label.pack(expand=True)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(self.preview_tab, text="Analysis Results", padding=10)
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=8, state='disabled')
        stats_scrollbar = ttk.Scrollbar(stats_frame, command=self.stats_text.yview)
        self.stats_text.config(yscrollcommand=stats_scrollbar.set)
        
        self.stats_text.pack(side='left', fill='both', expand=True)
        stats_scrollbar.pack(side='right', fill='y')
    
    def create_control_tab(self):
        """Control tab for running the bot"""
        # Status frame
        status_frame = ttk.LabelFrame(self.control_tab, text="Status", padding=10)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Ready", font=('Arial', 12, 'bold'))
        self.status_label.pack(pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                           maximum=100)
        self.progress_bar.pack(fill='x', pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(status_frame)
        button_frame.pack(pady=10)
        
        self.start_btn = ttk.Button(button_frame, text="Start Painting", 
                                   command=self.start_bot, state='disabled')
        self.start_btn.pack(side='left', padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="Stop", 
                                  command=self.stop_bot, state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        # Log frame
        log_frame = ttk.LabelFrame(self.control_tab, text="Log", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, state='disabled')
        log_scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        log_scrollbar.pack(side='right', fill='y')
    
    def select_canvas_region(self):
        """Start canvas region selection with drag functionality"""
        self.root.withdraw()  # Hide main window
        RegionSelector(self.on_canvas_region_selected)
    
    def select_palette_region(self):
        """Start palette region selection with drag functionality"""
        self.root.withdraw()  # Hide main window
        RegionSelector(self.on_palette_region_selected)
    
    def on_canvas_region_selected(self, region):
        """Callback when canvas region is selected"""
        self.root.deiconify()  # Show main window
        if region:
            self.canvas_region = region
            self.canvas_status.config(text=f"Selected: {region}", foreground="green")
            self.save_user_settings()  # Save the new region
        else:
            self.log_message("Canvas region selection cancelled")
        self.check_ready_for_analysis()
    
    def on_palette_region_selected(self, region):
        """Callback when palette region is selected"""
        self.root.deiconify()  # Show main window
        if region:
            self.palette_region = region
            self.palette_status.config(text=f"Selected: {region}", foreground="green")
            self.save_user_settings()  # Save the new region
        else:
            self.log_message("Palette region selection cancelled")
        self.check_ready_for_analysis()
    
    def log_message(self, message):
        """Add message to log"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
    
    def check_ready_for_analysis(self):
        """Enable analysis button if both regions are selected"""
        if self.canvas_region and self.palette_region:
            self.analyze_btn.config(state='normal')
    
    def analyze_regions(self):
        """Run analysis in a separate thread"""
        self.analyze_btn.config(state='disabled', text="Analyzing...")
        self.analysis_status.config(text="Running analysis...")
        self.log_message("Starting analysis...")
        
        # Run in thread to avoid freezing UI
        thread = threading.Thread(target=self._analyze_worker)
        thread.daemon = True
        thread.start()
    
    def _analyze_worker(self):
        """Worker function for analysis (runs in separate thread)"""
        try:
            # Import your existing functions here
            from main import (get_screen, estimate_pixel_size, get_preview_positions_from_estimation,
                            build_pixel_map, detect_palette_colors, save_palette_debug_image)
            
            # Take screenshots
            palette_img_rgb = get_screen(self.palette_region)
            canvas_img_rgb = get_screen(self.canvas_region)
            canvas_img_bgr = cv2.cvtColor(canvas_img_rgb, cv2.COLOR_RGB2BGR)
            
            # Analyze
            self.pixel_size = estimate_pixel_size(canvas_img_bgr)
            preview_positions = get_preview_positions_from_estimation(canvas_img_bgr, self.pixel_size)
            self.pixel_map = build_pixel_map(canvas_img_bgr, self.pixel_size, preview_positions)
            
            self.color_position_map = detect_palette_colors(
                palette_img_rgb, self.palette_region, color_palette
            )
            save_palette_debug_image(palette_img_rgb, self.color_position_map, self.palette_region)
            
            # Send results back to main thread
            self.message_queue.put({
                'type': 'analysis_complete',
                'pixel_size': self.pixel_size,
                'pixel_count': len(self.pixel_map),
                'colors_found': len(self.color_position_map)
            })
            
        except Exception as e:
            self.message_queue.put({
                'type': 'analysis_error',
                'error': str(e)
            })
    
    def start_bot(self):
        """Start the painting bot"""
        if not self.pixel_map or not self.color_position_map:
            messagebox.showerror("Error", "Please run analysis first!")
            return
        
        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(text="Painting...")
        self.log_message("Starting painting bot...")
        
        # Start bot in separate thread
        self.bot_thread = threading.Thread(target=self._bot_worker)
        self.bot_thread.daemon = True
        self.bot_thread.start()
    
    def _bot_worker(self):
        """Bot worker function (runs in separate thread)"""
        try:
            # Import your bot functions
            from main import find_pixels_to_paint_from_map
            import pyautogui
            import time
            
            enabled_colors = [
                color for color in color_palette 
                if self.color_vars[color['name']].get()
            ]
            
            total_colors = len(enabled_colors)
            
            for i, color in enumerate(enabled_colors):
                if not self.is_running:
                    break
                
                target_rgb = tuple(color["rgb"])
                if target_rgb not in self.color_position_map:
                    continue
                
                # Find pixels to paint
                target_bgr = target_rgb[::-1]
                positions = find_pixels_to_paint_from_map(self.pixel_map, target_bgr, 
                                                        tolerance=self.tolerance_var.get())
                
                if positions:
                    # Click color in palette
                    px, py = self.color_position_map[target_rgb]
                    pyautogui.click(px, py)
                    time.sleep(0.2)
                    
                    # Paint positions
                    for pos_i, (x, y) in enumerate(positions):
                        if not self.is_running:
                            break
                        
                        pyautogui.click(
                            x + self.canvas_region[0], 
                            y + self.canvas_region[1]
                        )
                        time.sleep(self.delay_var.get() / 1000.0)
                        
                        # Update progress
                        progress = ((i + pos_i/len(positions)) / total_colors) * 100
                        self.message_queue.put({
                            'type': 'progress',
                            'progress': progress,
                            'status': f"Painting {color['name']} ({pos_i+1}/{len(positions)})"
                        })
                
                # Update progress for completed color
                progress = ((i + 1) / total_colors) * 100
                self.message_queue.put({
                    'type': 'progress',
                    'progress': progress,
                    'status': f"Completed {color['name']}"
                })
            
            self.message_queue.put({'type': 'bot_complete'})
            
        except Exception as e:
            self.message_queue.put({
                'type': 'bot_error',
                'error': str(e)
            })
    
    def stop_bot(self):
        """Stop the painting bot"""
        self.is_running = False
        self.status_label.config(text="Stopping...")
        self.log_message("Stopping bot...")
    
    def process_queue(self):
        """Process messages from worker threads"""
        try:
            while True:
                message = self.message_queue.get_nowait()
                
                if message['type'] == 'analysis_complete':
                    self.analyze_btn.config(state='normal', text="Analyze Canvas & Palette")
                    self.analysis_status.config(text=f"Analysis complete! "
                                              f"Pixel size: {message['pixel_size']}, "
                                              f"Pixels: {message['pixel_count']}, "
                                              f"Colors: {message['colors_found']}")
                    self.start_btn.config(state='normal')
                    self.update_stats()
                    self.log_message(f"Analysis completed successfully. Found {message['pixel_count']} pixels and {message['colors_found']} colors.")
                    
                elif message['type'] == 'analysis_error':
                    self.analyze_btn.config(state='normal', text="Analyze Canvas & Palette")
                    self.analysis_status.config(text=f"Analysis failed: {message['error']}")
                    self.log_message(f"Analysis failed: {message['error']}")
                    
                elif message['type'] == 'progress':
                    self.progress_var.set(message['progress'])
                    self.status_label.config(text=message['status'])
                    
                elif message['type'] == 'bot_complete':
                    self.is_running = False
                    self.start_btn.config(state='normal')
                    self.stop_btn.config(state='disabled')
                    self.status_label.config(text="Painting complete!")
                    self.log_message("Painting completed successfully!")
                    
                elif message['type'] == 'bot_error':
                    self.is_running = False
                    self.start_btn.config(state='normal')
                    self.stop_btn.config(state='disabled')
                    self.status_label.config(text=f"Error: {message['error']}")
                    self.log_message(f"Bot error: {message['error']}")
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.process_queue)
    
    def enable_all_colors(self):
        for var in self.color_vars.values():
            var.set(True)
        self.save_user_settings()

    def disable_all_colors(self):
        for var in self.color_vars.values():
            var.set(False)
        self.save_user_settings()

    def enable_only_free(self):
        """Enable only free colors"""
        for color in self.color_palette:
            is_free = not color.get('premium', False)
            if color['name'] in self.color_vars:
                self.color_vars[color['name']].set(is_free)
        self.save_user_settings()

    def load_debug_image(self, event=None):
        """Load and display debug image"""
        image_type = self.image_var.get()
        
        filename_map = {
            "Size Estimation": "debug_size_estimation.png",
            "Palette Detection": "debug_palette.png"
        }
        
        filename = filename_map.get(image_type)
        if filename and os.path.exists(filename):
            try:
                # Load and resize image to fit in UI
                img = Image.open(filename)
                img.thumbnail((600, 400), Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(img)
                self.image_label.config(image=photo, text="")
                self.image_label.image = photo  # Keep a reference
            except Exception as e:
                self.image_label.config(text=f"Error loading image: {e}")
        else:
            self.image_label.config(text="Image not found. Run analysis first.")
    
    def refresh_debug_images(self):
        """Refresh debug image list"""
        self.load_debug_image()
    
    def update_stats(self):
        """Update statistics display"""
        if not self.pixel_map or not self.color_position_map:
            return
        
        stats = f"""Analysis Results:
        
Pixel Size: {self.pixel_size}x{self.pixel_size}
Total Pixels Detected: {len(self.pixel_map)}
Colors Found in Palette: {len(self.color_position_map)}

Enabled Colors: {sum(1 for var in self.color_vars.values() if var.get())}
Total Colors: {len(self.color_vars)}

Settings:
Color Tolerance: {self.tolerance_var.get()}
Click Delay: {self.delay_var.get()}ms
"""
        
        self.stats_text.config(state='normal')
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats)
        self.stats_text.config(state='disabled')


def main():
    root = tk.Tk()
    app = PlaceBotGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()