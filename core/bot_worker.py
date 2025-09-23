import threading
import time
import pyautogui
from .pixel_mapping import find_pixels_to_paint_from_map

class BotWorker:
    """Handles bot painting logic in separate thread"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.is_running = False
        self.thread = None
    
    def start_bot(self, message_queue, enabled_colors, settings):
        """Start the painting bot"""
        self.is_running = True
        self.thread = threading.Thread(
            target=self._bot_worker, 
            args=(message_queue, enabled_colors, settings)
        )
        self.thread.daemon = True
        self.thread.start()
    
    def stop_bot(self):
        """Stop the painting bot"""
        self.is_running = False
    
    def _bot_worker(self, message_queue, enabled_colors, settings):
        """Bot worker function (runs in separate thread)"""
        try:
            total_pixels_painted = 0
            pixel_limit = settings['pixel_limit']
            tolerance = settings['tolerance']
            delay = settings['delay']
            
            message_queue.put({
                'type': 'log',
                'message': f"Starting bot with pixel limit: {pixel_limit}"
            })
            
            for color in enabled_colors:
                if not self.is_running or total_pixels_painted >= pixel_limit:
                    break
                
                total_pixels_painted = self._paint_color(
                    color, total_pixels_painted, pixel_limit, 
                    tolerance, delay, message_queue
                )
            
            message_queue.put({
                'type': 'bot_complete',
                'total_painted': total_pixels_painted,
                'limit_reached': total_pixels_painted >= pixel_limit
            })
            
        except Exception as e:
            message_queue.put({'type': 'bot_error', 'error': str(e)})
    
    def _paint_color(self, color, total_pixels_painted, pixel_limit, tolerance, delay, message_queue):
        """Paint a specific color and return updated pixel count"""
        target_rgb = tuple(color["rgb"])
        if target_rgb not in self.data_manager.color_position_map:
            return total_pixels_painted
        
        # Find pixels to paint
        target_bgr = target_rgb[::-1]
        positions = find_pixels_to_paint_from_map(
            self.data_manager.pixel_map, target_bgr, tolerance=tolerance
        )
        
        if not positions:
            return total_pixels_painted
        
        # Limit positions to not exceed pixel limit
        remaining_pixels = pixel_limit - total_pixels_painted
        if len(positions) > remaining_pixels:
            positions = positions[:remaining_pixels]
        
        message_queue.put({
            'type': 'log',
            'message': f"Painting {len(positions)} pixels with {color['name']} "
                      f"(Total: {total_pixels_painted + len(positions)}/{pixel_limit})"
        })
        
        # Click color in palette
        px, py = self.data_manager.color_position_map[target_rgb]
        pyautogui.click(px, py)
        time.sleep(0.2)
        
        # Paint positions
        for pos_i, (x, y) in enumerate(positions):
            if not self.is_running:
                break
            
            pyautogui.click(x + self.data_manager.canvas_region[0], y + self.data_manager.canvas_region[1])
            time.sleep(delay / 1000.0)
            total_pixels_painted += 1
            
            # Update progress every 10 pixels
            if pos_i % 10 == 0 or pos_i == len(positions) - 1:
                progress = (total_pixels_painted / pixel_limit) * 100
                message_queue.put({
                    'type': 'progress',
                    'progress': min(progress, 100),
                    'status': f"Painting {color['name']} ({total_pixels_painted}/{pixel_limit} pixels)"
                })
            
            if total_pixels_painted >= pixel_limit:
                break
        
        return total_pixels_painted