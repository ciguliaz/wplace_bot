import tkinter as tk
from tkinter import ttk

class ColorsTab:
    """Color control tab for enabling/disabling colors"""
    
    def __init__(self, parent, main_window):
        self.parent = parent
        self.main_window = main_window
        self.data_manager = main_window.data_manager
        
        # Create the tab frame
        self.frame = ttk.Frame(parent)
        
        # UI variables
        self.color_vars = {}
        self.bought_vars = {}
        self.color_labels = {}
        self.color_widgets = []
        
        # Create the UI
        self._create_ui()
    
    def _create_ui(self):
        """Create colors tab UI"""
        self._create_scrollable_frame()
        self._create_control_buttons()
        self._create_color_widgets()
    
    def _create_scrollable_frame(self):
        """Create scrollable frame for color widgets"""
        # Create scrollable frame
        self.canvas = tk.Canvas(self.frame)
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind("<Configure>", 
                                 lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def on_enter(event):
            self.canvas.focus_set()
        
        # Store the mousewheel handler for use in widgets
        self.on_mousewheel = on_mousewheel
        
        # Bind mouse wheel events
        for widget in [self.canvas, self.scrollable_frame, self.frame]:
            widget.bind("<MouseWheel>", on_mousewheel)
        self.canvas.bind("<Enter>", on_enter)
    
    def _create_control_buttons(self):
        """Create control buttons"""
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        buttons = [
            ("Enable All", self.enable_all_colors),
            ("Disable All", self.disable_all_colors),
            ("Free Colors", self.enable_only_free),
            ("Available Colors", self.enable_available_colors)
        ]
        
        for text, command in buttons:
            ttk.Button(control_frame, text=text, command=command).pack(side='left', padx=5)
    
    def _create_color_widgets(self):
        """Create color control widgets"""
        for color in self.data_manager.color_palette:
            self._create_single_color_widget(color)
        
        # Pack canvas and scrollbar after all widgets are created
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
    
    def _create_single_color_widget(self, color):
        """Create a single color widget"""
        color_frame = ttk.Frame(self.scrollable_frame)
        color_frame.pack(fill='x', padx=10, pady=2)
        color_frame.bind("<MouseWheel>", self.on_mousewheel)
        
        # Color preview
        color_canvas = tk.Canvas(color_frame, width=30, height=20)
        color_canvas.pack(side='left', padx=5)
        color_canvas.bind("<MouseWheel>", self.on_mousewheel)
        
        rgb = color['rgb']
        hex_color = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        color_canvas.create_rectangle(0, 0, 30, 20, fill=hex_color, outline="")
        
        # Load saved state
        color_id = str(color['id'])
        color_settings = self.data_manager.user_settings['colors'].get(color_id, {})
        is_bought = color_settings.get('bought', False) if color.get('premium', False) else True
        default_enabled = not color.get('premium', False) or is_bought
        is_enabled = color_settings.get('enabled', default_enabled)
        
        # Enable/disable checkbox
        var = tk.BooleanVar(value=is_enabled)
        self.color_vars[color['name']] = var
        checkbox = ttk.Checkbutton(color_frame, variable=var, command=self._on_color_setting_change)
        checkbox.pack(side='left', padx=5)
        checkbox.bind("<MouseWheel>", self.on_mousewheel)
        
        # Color name label
        label_text = f"{color['name']} ({'Premium' if color.get('premium', False) else 'Free'})"
        label_color = "green" if (not color.get('premium', False) or is_bought) else "red"
        
        name_label = ttk.Label(color_frame, text=label_text, foreground=label_color)
        name_label.pack(side='left', padx=5)
        name_label.bind("<MouseWheel>", self.on_mousewheel)
        
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
            bought_checkbox.bind("<MouseWheel>", self.on_mousewheel)
    
    def _on_color_setting_change(self):
        """Handle color setting changes with debouncing"""
        # Use a delayed save to avoid too frequent saves
        if hasattr(self, '_save_timer'):
            self.main_window.root.after_cancel(self._save_timer)
        self._save_timer = self.main_window.root.after(500, self.main_window.save_user_settings)
    
    def _toggle_bought_status(self, color):
        """Toggle bought status and save"""
        try:
            color_name = color['name']
            color_id = str(color['id'])
            new_bought_status = self.bought_vars[color_name].get()
            
            # Update using data_manager
            self.data_manager.set_color_setting(color_id, 'bought', new_bought_status)
            self._update_color_label(color, new_bought_status)
            
        except Exception as e:
            print(f"Failed to toggle bought status: {e}")
    
    def _update_color_label(self, color, is_bought):
        """Update specific color label"""
        color_name = color['name']
        
        if color_name in self.color_labels:
            label_widget = self.color_labels[color_name]
            label_text = f"{color_name} ({'Premium' if color.get('premium', False) else 'Free'})"
            label_color = "green" if (not color.get('premium', False) or is_bought) else "red"
            label_widget.config(text=label_text, foreground=label_color)
    
    def enable_all_colors(self):
        """Enable all colors"""
        for var in self.color_vars.values():
            var.set(True)
        self.main_window.save_user_settings()
    
    def disable_all_colors(self):
        """Disable all colors"""
        for var in self.color_vars.values():
            var.set(False)
        self.main_window.save_user_settings()
    
    def enable_only_free(self):
        """Enable only free colors"""
        for color in self.data_manager.color_palette:
            is_free = not color.get('premium', False)
            if color['name'] in self.color_vars:
                self.color_vars[color['name']].set(is_free)
        self.main_window.save_user_settings()
    
    def enable_available_colors(self):
        """Enable all available colors (free + bought premium colors)"""
        for color in self.data_manager.color_palette:
            color_id = str(color['id'])
            color_settings = self.data_manager.user_settings['colors'].get(color_id, {})
            is_bought = color_settings.get('bought', False) if color.get('premium', False) else True
            is_available = not color.get('premium', False) or is_bought
            
            if color['name'] in self.color_vars:
                self.color_vars[color['name']].set(is_available)
        self.main_window.save_user_settings()
    
    def get_enabled_colors(self):
        """Get list of enabled colors"""
        enabled_colors = []
        for color in self.data_manager.color_palette:
            color_id = str(color['id'])
            color_settings = self.data_manager.user_settings['colors'].get(color_id, {})
            is_enabled = color_settings.get('enabled', True)
            
            if is_enabled and color['name'] in self.color_vars and self.color_vars[color['name']].get():
                enabled_colors.append(color)
        return enabled_colors