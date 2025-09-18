import tkinter as tk
from tkinter import ttk
from gui.region_selector import RegionSelector

class SetupTab:
    """Setup tab for region selection and analysis"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.data_manager = main_window.data_manager
        self.analysis_worker = main_window.analysis_worker
        self.message_queue = main_window.message_queue
        
        # Create the tab frame
        self.frame = ttk.Frame(parent)
        
        # UI elements that need to be accessed from main window
        self.canvas_status = None
        self.palette_status = None
        self.analyze_btn = None
        self.analysis_status = None
        self.tolerance_var = None
        self.delay_var = None
        self.tolerance_label = None
        self.delay_label = None
        
        # Create the UI
        self._create_ui()
        self._load_saved_regions()
    
    def _create_ui(self):
        """Create setup tab UI"""
        self._create_instructions()
        self._create_region_selection()
        self._create_analysis_frame()
        self._create_settings_frame()
    
    def _create_instructions(self):
        """Create instructions frame"""
        instructions_frame = ttk.LabelFrame(self.frame, text="Instructions", padding=10)
        instructions_frame.pack(fill='x', padx=10, pady=5)
        
        instructions_text = """How to select regions:
1. Click 'Select Canvas' or 'Select Palette' button
2. Your screen will show a dark overlay
3. Click and drag to select the desired region
4. Release mouse to confirm selection
5. Press ESC to cancel selection"""
        
        ttk.Label(instructions_frame, text=instructions_text, justify='left').pack(anchor='w')
    
    def _create_region_selection(self):
        """Create region selection frame"""
        region_frame = ttk.LabelFrame(self.frame, text="Region Selection", padding=10)
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
    
    def _create_analysis_frame(self):
        """Create analysis frame"""
        analysis_frame = ttk.LabelFrame(self.frame, text="Analysis", padding=10)
        analysis_frame.pack(fill='x', padx=10, pady=5)
        
        self.analyze_btn = ttk.Button(analysis_frame, text="Analyze Canvas & Palette", 
                                     command=self._analyze_regions, state='disabled')
        self.analyze_btn.pack(pady=5)
        self.analysis_status = ttk.Label(analysis_frame, text="Select regions first")
        self.analysis_status.pack(pady=5)
    
    def _create_settings_frame(self):
        """Create settings frame"""
        settings_frame = ttk.LabelFrame(self.frame, text="Settings", padding=10)
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
    
    def _load_saved_regions(self):
        """Load and display saved regions"""
        if self.data_manager.canvas_region:
            self.canvas_status.config(text=f"Loaded: {self.data_manager.canvas_region}", foreground="blue")
        if self.data_manager.palette_region:
            self.palette_status.config(text=f"Loaded: {self.data_manager.palette_region}", foreground="blue")
        self._check_ready_for_analysis()
    
    def _select_canvas_region(self):
        """Start canvas region selection"""
        self.main_window.root.withdraw()
        RegionSelector(self._on_canvas_region_selected)
    
    def _select_palette_region(self):
        """Start palette region selection"""
        self.main_window.root.withdraw()
        RegionSelector(self._on_palette_region_selected)
    
    def _on_canvas_region_selected(self, region):
        """Handle canvas region selection"""
        self.main_window.root.deiconify()
        if region:
            self.data_manager.set_canvas_region(region)
            self.canvas_status.config(text=f"Selected: {region}", foreground="green")
        else:
            self.main_window._log_message("Canvas region selection cancelled")
        self._check_ready_for_analysis()
    
    def _on_palette_region_selected(self, region):
        """Handle palette region selection"""
        self.main_window.root.deiconify()
        if region:
            self.data_manager.set_palette_region(region)
            self.palette_status.config(text=f"Selected: {region}", foreground="green")
        else:
            self.main_window._log_message("Palette region selection cancelled")
        self._check_ready_for_analysis()
    
    def _check_ready_for_analysis(self):
        """Enable analysis button if both regions are selected"""
        if self.data_manager.canvas_region and self.data_manager.palette_region:
            self.analyze_btn.config(state='normal')
    
    def _analyze_regions(self):
        """Run analysis in a separate thread"""
        self.analyze_btn.config(state='disabled', text="Analyzing...")
        self.analysis_status.config(text="Running analysis...")
        self.main_window._log_message("Starting analysis...")
        
        # Use the analysis worker
        self.analysis_worker.start_analysis(self.message_queue)
    
    def _update_tolerance_label(self, value):
        """Update tolerance value display and save"""
        self.tolerance_label.config(text=f"{int(float(value))}")
        self.main_window.save_user_settings()

    def _update_delay_label(self, value):
        """Update delay value display and save"""
        self.delay_label.config(text=f"{int(float(value))}")
        self.main_window.save_user_settings()
    
    def on_analysis_complete(self, message):
        """Handle analysis completion from main window"""
        self.analyze_btn.config(state='normal', text="Analyze Canvas & Palette")
        self.analysis_status.config(
            text=f"Analysis complete! Pixel size: {message['pixel_size']}, "
                 f"Pixels: {message['pixel_count']}, Colors: {message['colors_found']}"
        )
    
    def on_analysis_error(self, message):
        """Handle analysis error from main window"""
        self.analyze_btn.config(state='normal', text="Analyze Canvas & Palette")
        self.analysis_status.config(text=f"Analysis failed: {message['error']}")