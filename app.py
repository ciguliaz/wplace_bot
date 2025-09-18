import json
import os
import time
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import threading
import queue
import tkinter as tk
import cv2

# Import the new DataManager and RegionSelector
from core.data_manager import DataManager
from gui.region_selector import RegionSelector

class PlaceBotGUI:
    """Main GUI application for Place Bot"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Place Bot - Pixel Art Automation")
        self.root.geometry("800x800")
        
        # Initialize data manager
        self.data_manager = DataManager()
        
        # State variables (now delegated to data_manager)
        self.is_running = False
        self.bot_thread = None
        
        # UI variables
        self.color_vars = {}
        self.bought_vars = {}
        self.color_labels = {}
        
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
        self.data_manager.update_preference('color_tolerance', self.tolerance_var.get())
        self.data_manager.update_preference('click_delay', self.delay_var.get())
        self.data_manager.update_preference('pixel_limit', self.pixel_limit_var.get())
        
        # Save color settings from UI
        for color in self.data_manager.color_palette:
            color_id = str(color['id'])
            
            # Save enabled status
            if color['name'] in self.color_vars:
                self.data_manager.set_color_setting(color_id, 'enabled', self.color_vars[color['name']].get())
            
            # Save bought status (only for premium colors)
            if color.get('premium', False) and color['name'] in self.bought_vars:
                self.data_manager.set_color_setting(color_id, 'bought', self.bought_vars[color['name']].get())

    def load_saved_regions(self):
        """Load and display saved regions"""
        if self.data_manager.canvas_region:
            self.canvas_status.config(text=f"Loaded: {self.data_manager.canvas_region}", foreground="blue")
        if self.data_manager.palette_region:
            self.palette_status.config(text=f"Loaded: {self.data_manager.palette_region}", foreground="blue")
        self._check_ready_for_analysis()

    # ==================== UI SETUP ====================
    
    def setup_ui(self):
        """Create the main UI layout"""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.setup_tab = ttk.Frame(notebook)
        self.colors_tab = ttk.Frame(notebook)
        self.preview_tab = ttk.Frame(notebook)
        self.control_tab = ttk.Frame(notebook)
        
        notebook.add(self.setup_tab, text="Setup")
        notebook.add(self.colors_tab, text="Color Control")
        notebook.add(self.preview_tab, text="Preview & Debug")
        notebook.add(self.control_tab, text="Bot Control")
        
        # Create tab content
        self._create_setup_tab()
        self._create_colors_tab()
        self._create_preview_tab()
        self._create_control_tab()
    
    def _create_setup_tab(self):
        """Setup tab for region selection and analysis"""
        # Instructions
        instructions_frame = ttk.LabelFrame(self.setup_tab, text="Instructions", padding=10)
        instructions_frame.pack(fill='x', padx=10, pady=5)
        
        instructions_text = """How to select regions:
1. Click 'Select Canvas' or 'Select Palette' button
2. Your screen will show a dark overlay
3. Click and drag to select the desired region
4. Release mouse to confirm selection
5. Press ESC to cancel selection"""
        
        ttk.Label(instructions_frame, text=instructions_text, justify='left').pack(anchor='w')
        
        # Region Selection
        region_frame = ttk.LabelFrame(self.setup_tab, text="Region Selection", padding=10)
        region_frame.pack(fill='x', padx=10, pady=5)
        
        # Canvas region
        canvas_frame = ttk.Frame(region_frame)
        canvas_frame.pack(fill='x', pady=5)
        ttk.Label(canvas_frame, text="Canvas Region:").pack(side='left')
        self.canvas_status = ttk.Label(canvas_frame, text="Not selected", foreground="red")
        self.canvas_status.pack(side='left', padx=(10, 0))
        ttk.Button(canvas_frame, text="Select Canvas", 
                  command=self._select_canvas_region).pack(side='right')
        
        # Palette region
        palette_frame = ttk.Frame(region_frame)
        palette_frame.pack(fill='x', pady=5)
        ttk.Label(palette_frame, text="Palette Region:").pack(side='left')
        self.palette_status = ttk.Label(palette_frame, text="Not selected", foreground="red")
        self.palette_status.pack(side='left', padx=(10, 0))
        ttk.Button(palette_frame, text="Select Palette", 
                  command=self._select_palette_region).pack(side='right')
        
        # Analysis
        analysis_frame = ttk.LabelFrame(self.setup_tab, text="Analysis", padding=10)
        analysis_frame.pack(fill='x', padx=10, pady=5)
        
        self.analyze_btn = ttk.Button(analysis_frame, text="Analyze Canvas & Palette", 
                                     command=self._analyze_regions, state='disabled')
        self.analyze_btn.pack(pady=5)
        self.analysis_status = ttk.Label(analysis_frame, text="Select regions first")
        self.analysis_status.pack(pady=5)
        
        # Settings
        self._create_settings_frame()
    
    def _create_settings_frame(self):
        """Create settings frame in setup tab"""
        settings_frame = ttk.LabelFrame(self.setup_tab, text="Settings", padding=10)
        settings_frame.pack(fill='x', padx=10, pady=5)
        
        # Load saved settings
        saved_tolerance = self.data_manager.user_settings['preferences']['color_tolerance']
        saved_delay = self.data_manager.user_settings['preferences']['click_delay']
        
        # Tolerance setting
        tolerance_frame = ttk.Frame(settings_frame)
        tolerance_frame.pack(fill='x', pady=2)
        ttk.Label(tolerance_frame, text="Color Tolerance:").pack(side='left')
        self.tolerance_var = tk.IntVar(value=saved_tolerance)
        tolerance_scale = ttk.Scale(tolerance_frame, from_=1, to=20, variable=self.tolerance_var, 
                                   orient='horizontal', command=self._update_tolerance_label)
        tolerance_scale.pack(side='right', fill='x', expand=True, padx=(10, 0))
        self.tolerance_label = ttk.Label(tolerance_frame, text=str(saved_tolerance))
        self.tolerance_label.pack(side='right', padx=(5, 10))
        
        # Click delay setting
        delay_frame = ttk.Frame(settings_frame)
        delay_frame.pack(fill='x', pady=2)
        ttk.Label(delay_frame, text="Click Delay (ms):").pack(side='left')
        self.delay_var = tk.IntVar(value=saved_delay)
        delay_scale = ttk.Scale(delay_frame, from_=10, to=100, variable=self.delay_var, 
                               orient='horizontal', command=self._update_delay_label)
        delay_scale.pack(side='right', fill='x', expand=True, padx=(10, 0))
        self.delay_label = ttk.Label(delay_frame, text=str(saved_delay))
        self.delay_label.pack(side='right', padx=(5, 10))
    
    def _create_colors_tab(self):
        """Color control tab for enabling/disabling colors"""
        # Create scrollable frame
        canvas = tk.Canvas(self.colors_tab)
        scrollbar = ttk.Scrollbar(self.colors_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", 
                            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def on_enter(event):
            canvas.focus_set()
        
        # Bind mouse wheel events
        for widget in [canvas, scrollable_frame, self.colors_tab]:
            widget.bind("<MouseWheel>", on_mousewheel)
        canvas.bind("<Enter>", on_enter)
        
        # Control buttons
        control_frame = ttk.Frame(self.colors_tab)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        buttons = [
            ("Enable All", self._enable_all_colors),
            ("Disable All", self._disable_all_colors),
            ("Free Colors", self._enable_only_free),
            ("Available Colors", self._enable_available_colors)
        ]
        
        for text, command in buttons:
            ttk.Button(control_frame, text=text, command=command).pack(side='left', padx=5)
        
        # Create color checkboxes
        self._create_color_widgets(scrollable_frame, on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_color_widgets(self, parent, mousewheel_handler):
        """Create color control widgets"""
        for color in self.data_manager.color_palette:  # FIXED: Use data_manager
            color_frame = ttk.Frame(parent)
            color_frame.pack(fill='x', padx=10, pady=2)
            color_frame.bind("<MouseWheel>", mousewheel_handler)
            
            # Color preview
            color_canvas = tk.Canvas(color_frame, width=30, height=20)
            color_canvas.pack(side='left', padx=5)
            color_canvas.bind("<MouseWheel>", mousewheel_handler)
            
            rgb = color['rgb']
            hex_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
            color_canvas.create_rectangle(0, 0, 30, 20, fill=hex_color, outline="")
            
            # Load saved state
            color_id = str(color['id'])
            color_settings = self.data_manager.user_settings['colors'].get(color_id, {})  # FIXED: Use data_manager
            is_bought = color_settings.get('bought', False) if color.get('premium', False) else True
            default_enabled = not color.get('premium', False) or is_bought
            is_enabled = color_settings.get('enabled', default_enabled)
            
            # Enable/disable checkbox
            var = tk.BooleanVar(value=is_enabled)
            self.color_vars[color['name']] = var
            checkbox = ttk.Checkbutton(color_frame, variable=var, command=self.save_user_settings)
            checkbox.pack(side='left', padx=5)
            checkbox.bind("<MouseWheel>", mousewheel_handler)
            
            # Color name label
            label_text = f"{color['name']} ({'Premium' if color.get('premium', False) else 'Free'})"
            label_color = "green" if (not color.get('premium', False) or is_bought) else "red"
            
            name_label = ttk.Label(color_frame, text=label_text, foreground=label_color)
            name_label.pack(side='left', padx=5)
            name_label.bind("<MouseWheel>", mousewheel_handler)
            
            # Store label reference for updates
            self.color_labels[color['name']] = name_label
            
            # Bought toggle for premium colors
            if color.get('premium', False):
                bought_var = tk.BooleanVar(value=is_bought)
                self.bought_vars[color['name']] = bought_var
                
                bought_checkbox = ttk.Checkbutton(
                    color_frame, text="Bought", variable=bought_var,
                    command=lambda c=color: self._toggle_bought_status(c)
                )
                bought_checkbox.pack(side='left', padx=10)
                bought_checkbox.bind("<MouseWheel>", mousewheel_handler)
    
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
        
        saved_pixel_limit = self.data_manager.user_settings['preferences'].get('pixel_limit', 50)  # FIXED: Use data_manager
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

    # ==================== EVENT HANDLERS ====================
    
    def _update_tolerance_label(self, value):
        """Update tolerance value display and save"""
        self.tolerance_label.config(text=f"{int(float(value))}")
        self.save_user_settings()

    def _update_delay_label(self, value):
        """Update delay value display and save"""
        self.delay_label.config(text=f"{int(float(value))}")
        self.save_user_settings()
    
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

    # ==================== REGION SELECTION ====================
    
    def _select_canvas_region(self):
        """Start canvas region selection"""
        self.root.withdraw()
        RegionSelector(self._on_canvas_region_selected)
    
    def _select_palette_region(self):
        """Start palette region selection"""
        self.root.withdraw()
        RegionSelector(self._on_palette_region_selected)
    
    def _on_canvas_region_selected(self, region):
        """Handle canvas region selection"""
        self.root.deiconify()
        if region:
            self.data_manager.set_canvas_region(region)  # FIXED: Use data_manager
            self.canvas_status.config(text=f"Selected: {region}", foreground="green")
        else:
            self._log_message("Canvas region selection cancelled")
        self._check_ready_for_analysis()
    
    def _on_palette_region_selected(self, region):
        """Handle palette region selection"""
        self.root.deiconify()
        if region:
            self.data_manager.set_palette_region(region)  # FIXED: Use data_manager
            self.palette_status.config(text=f"Selected: {region}", foreground="green")
        else:
            self._log_message("Palette region selection cancelled")
        self._check_ready_for_analysis()
    
    def _check_ready_for_analysis(self):
        """Enable analysis button if both regions are selected"""
        if self.data_manager.canvas_region and self.data_manager.palette_region:  # FIXED: Use data_manager
            self.analyze_btn.config(state='normal')

    # ==================== ANALYSIS AND BOT ====================
    
    def _analyze_regions(self):
        """Run analysis in a separate thread"""
        self.analyze_btn.config(state='disabled', text="Analyzing...")
        self.analysis_status.config(text="Running analysis...")
        self._log_message("Starting analysis...")
        
        thread = threading.Thread(target=self._analyze_worker)
        thread.daemon = True
        thread.start()
    
    def _analyze_worker(self):
        """Worker function for analysis (runs in separate thread)"""
        try:
            from main import (get_screen, estimate_pixel_size, get_preview_positions_from_estimation,
                            build_pixel_map, detect_palette_colors, save_palette_debug_image)
            
            # Take screenshots using data_manager regions
            palette_img_rgb = get_screen(self.data_manager.palette_region)  # FIXED: Use data_manager
            canvas_img_rgb = get_screen(self.data_manager.canvas_region)    # FIXED: Use data_manager
            canvas_img_bgr = cv2.cvtColor(canvas_img_rgb, cv2.COLOR_RGB2BGR)
            
            # Analyze
            pixel_size = estimate_pixel_size(canvas_img_bgr)
            preview_positions = get_preview_positions_from_estimation(canvas_img_bgr, pixel_size)
            pixel_map = build_pixel_map(canvas_img_bgr, pixel_size, preview_positions)
            color_position_map = detect_palette_colors(
                palette_img_rgb, self.data_manager.palette_region, self.data_manager.color_palette  # FIXED: Use data_manager
            )
            save_palette_debug_image(palette_img_rgb, color_position_map, self.data_manager.palette_region)  # FIXED: Use data_manager
            
            # Store results in data_manager
            self.data_manager.set_analysis_results(pixel_size, pixel_map, color_position_map)  # FIXED: Use data_manager
            
            self.message_queue.put({
                'type': 'analysis_complete',
                'pixel_size': pixel_size,
                'pixel_count': len(pixel_map),
                'colors_found': len(color_position_map)
            })
            
        except Exception as e:
            self.message_queue.put({'type': 'analysis_error', 'error': str(e)})
    
    def _start_bot(self):
        """Start the painting bot"""
        if not self.data_manager.has_analysis_data():  # FIXED: Use data_manager
            messagebox.showerror("Error", "Please run analysis first!")
            return
        
        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(text="Painting...")
        self._log_message("Starting painting bot...")
        
        self.bot_thread = threading.Thread(target=self._bot_worker)
        self.bot_thread.daemon = True
        self.bot_thread.start()
    
    def _bot_worker(self):
        """Bot worker function (runs in separate thread)"""
        try:
            from main import find_pixels_to_paint_from_map
            import pyautogui
            
            # Get enabled colors
            enabled_colors = self._get_enabled_colors()
            total_pixels_painted = 0
            pixel_limit = self.pixel_limit_var.get()
            
            self.message_queue.put({
                'type': 'log',
                'message': f"Starting bot with pixel limit: {pixel_limit}"
            })
            
            for color in enabled_colors:
                if not self.is_running or total_pixels_painted >= pixel_limit:
                    break
                
                total_pixels_painted = self._paint_color(color, total_pixels_painted, pixel_limit)
            
            self.message_queue.put({
                'type': 'bot_complete',
                'total_painted': total_pixels_painted,
                'limit_reached': total_pixels_painted >= pixel_limit
            })
            
        except Exception as e:
            self.message_queue.put({'type': 'bot_error', 'error': str(e)})
    
    def _get_enabled_colors(self):
        """Get list of enabled colors"""
        enabled_colors = []
        for color in self.data_manager.color_palette:  # FIXED: Use data_manager
            color_id = str(color['id'])
            color_settings = self.data_manager.user_settings['colors'].get(color_id, {})  # FIXED: Use data_manager
            is_enabled = color_settings.get('enabled', True)
            
            if is_enabled and color['name'] in self.color_vars and self.color_vars[color['name']].get():
                enabled_colors.append(color)
        return enabled_colors
    
    def _paint_color(self, color, total_pixels_painted, pixel_limit):
        """Paint a specific color and return updated pixel count"""
        from main import find_pixels_to_paint_from_map
        import pyautogui
        
        target_rgb = tuple(color["rgb"])
        if target_rgb not in self.data_manager.color_position_map:  # FIXED: Use data_manager
            return total_pixels_painted
        
        # Find pixels to paint
        target_bgr = target_rgb[::-1]
        positions = find_pixels_to_paint_from_map(
            self.data_manager.pixel_map, target_bgr, tolerance=self.tolerance_var.get()  # FIXED: Use data_manager
        )
        
        if not positions:
            return total_pixels_painted
        
        # Limit positions to not exceed pixel limit
        remaining_pixels = pixel_limit - total_pixels_painted
        if len(positions) > remaining_pixels:
            positions = positions[:remaining_pixels]
        
        self.message_queue.put({
            'type': 'log',
            'message': f"Painting {len(positions)} pixels with {color['name']} "
                      f"(Total: {total_pixels_painted + len(positions)}/{pixel_limit})"
        })
        
        # Click color in palette
        px, py = self.data_manager.color_position_map[target_rgb]  # FIXED: Use data_manager
        pyautogui.click(px, py)
        time.sleep(0.2)
        
        # Paint positions
        for pos_i, (x, y) in enumerate(positions):
            if not self.is_running:
                break
            
            pyautogui.click(x + self.data_manager.canvas_region[0], y + self.data_manager.canvas_region[1])  # FIXED: Use data_manager
            time.sleep(self.delay_var.get() / 1000.0)
            total_pixels_painted += 1
            
            # Update progress every 10 pixels
            if pos_i % 10 == 0 or pos_i == len(positions) - 1:
                progress = (total_pixels_painted / pixel_limit) * 100
                self.message_queue.put({
                    'type': 'progress',
                    'progress': min(progress, 100),
                    'status': f"Painting {color['name']} ({total_pixels_painted}/{pixel_limit} pixels)"
                })
            
            if total_pixels_painted >= pixel_limit:
                break
        
        return total_pixels_painted
    
    def _stop_bot(self):
        """Stop the painting bot"""
        self.is_running = False
        self.status_label.config(text="Stopping...")
        self._log_message("Stopping bot...")

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
        if not self.data_manager.has_analysis_data():  # FIXED: Use data_manager
            return
        
        stats = f"""Analysis Results:
        
Pixel Size: {self.data_manager.pixel_size}x{self.data_manager.pixel_size}
Total Pixels Detected: {len(self.data_manager.pixel_map)}
Colors Found in Palette: {len(self.data_manager.color_position_map)}

Enabled Colors: {sum(1 for var in self.color_vars.values() if var.get())}
Total Colors: {len(self.color_vars)}

Settings:
Color Tolerance: {self.tolerance_var.get()}
Click Delay: {self.delay_var.get()}ms
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
                    self.analyze_btn.config(state='normal', text="Analyze Canvas & Palette")
                    self.analysis_status.config(
                        text=f"Analysis complete! Pixel size: {message['pixel_size']}, "
                             f"Pixels: {message['pixel_count']}, Colors: {message['colors_found']}"
                    )
                    self.start_btn.config(state='normal')
                    self._update_stats()
                    self._log_message(
                        f"Analysis completed successfully. Found {message['pixel_count']} pixels "
                        f"and {message['colors_found']} colors."
                    )
                    
                elif message['type'] == 'analysis_error':
                    self.analyze_btn.config(state='normal', text="Analyze Canvas & Palette")
                    self.analysis_status.config(text=f"Analysis failed: {message['error']}")
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