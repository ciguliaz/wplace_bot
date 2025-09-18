import tkinter as tk

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
        self.overlay.attributes('-alpha', 0.3)
        self.overlay.attributes('-topmost', True)
        self.overlay.configure(bg='black')
        
        # Create canvas for drawing selection rectangle
        self.canvas = tk.Canvas(self.overlay, highlightthickness=0, bg='black')
        self.canvas.pack(fill='both', expand=True)
        
        # Bind events
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.overlay.bind('<Escape>', self.cancel)
        self.overlay.focus_set()
        
        # Instructions
        self.canvas.create_text(
            self.overlay.winfo_screenwidth() // 2, 50,
            text="Drag to select region. Press ESC to cancel.",
            fill='white', font=('Arial', 16, 'bold')
        )
    
    def on_click(self, event):
        """Start selection"""
        self.start_x = event.x
        self.start_y = event.y
        if self.rect_id:
            self.canvas.delete(self.rect_id)
    
    def on_drag(self, event):
        """Update selection rectangle while dragging"""
        if self.start_x is not None and self.start_y is not None:
            if self.rect_id:
                self.canvas.delete(self.rect_id)
            
            self.rect_id = self.canvas.create_rectangle(
                self.start_x, self.start_y, event.x, event.y,
                outline='red', width=2, fill='', stipple='gray25'
            )
    
    def on_release(self, event):
        """Finish selection and return coordinates"""
        if self.start_x is not None and self.start_y is not None:
            left = min(self.start_x, event.x)
            top = min(self.start_y, event.y)
            width = abs(event.x - self.start_x)
            height = abs(event.y - self.start_y)
            
            if width > 10 and height > 10:
                region = (left, top, width, height)
                self.close()
                self.callback(region)
            else:
                self.canvas.create_text(
                    event.x, event.y - 20,
                    text="Region too small! Try again.",
                    fill='yellow', font=('Arial', 12, 'bold')
                )
                self._reset_selection()
    
    def _reset_selection(self):
        """Reset selection state"""
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