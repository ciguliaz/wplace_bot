import threading
import cv2

class AnalysisWorker:
    """Handles analysis logic in separate thread"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.thread = None
    
    def start_analysis(self, message_queue):
        """Start analysis in a separate thread"""
        self.thread = threading.Thread(
            target=self._analyze_worker, 
            args=(message_queue,)
        )
        self.thread.daemon = True
        self.thread.start()
    
    def _analyze_worker(self, message_queue):
        """Worker function for analysis (runs in separate thread)"""
        try:
            from core import get_screen, estimate_pixel_size, detect_palette_colors, save_palette_debug_image, build_pixel_map, get_preview_positions_from_estimation
            
            # Take screenshots using data_manager regions
            palette_img_rgb = get_screen(self.data_manager.palette_region)
            canvas_img_rgb = get_screen(self.data_manager.canvas_region)
            canvas_img_bgr = cv2.cvtColor(canvas_img_rgb, cv2.COLOR_RGB2BGR)
            
            # Analyze
            pixel_size = estimate_pixel_size(canvas_img_bgr)
            preview_positions = get_preview_positions_from_estimation(canvas_img_bgr, pixel_size)
            pixel_map = build_pixel_map(canvas_img_bgr, pixel_size, preview_positions)
            color_position_map = detect_palette_colors(
                palette_img_rgb, self.data_manager.palette_region, self.data_manager.color_palette
            )
            save_palette_debug_image(palette_img_rgb, color_position_map, self.data_manager.palette_region)
            
            # Store results in data_manager
            self.data_manager.set_analysis_results(pixel_size, pixel_map, color_position_map)
            
            message_queue.put({
                'type': 'analysis_complete',
                'pixel_size': pixel_size,
                'pixel_count': len(pixel_map),
                'colors_found': len(color_position_map)
            })
            
        except Exception as e:
            message_queue.put({'type': 'analysis_error', 'error': str(e)})