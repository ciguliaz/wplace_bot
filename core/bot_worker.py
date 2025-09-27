import threading
import time
import pyautogui
from .pixel_mapping import find_pixels_to_paint_from_map
from .logger import get_logger

class BotWorker:
    """Handles bot painting logic in separate thread"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.is_running = False
        self.thread = None
        self.logger = get_logger()
        self.last_bot_mouse_pos = None
        self.mouse_moved = False
    
    def start_bot(self, message_queue, enabled_colors, settings):
        """Start the painting bot"""
        self.is_running = True
        self.mouse_moved = False
        self.last_bot_mouse_pos = pyautogui.position()
        self.thread = threading.Thread(
            target=self._bot_worker, 
            args=(message_queue, enabled_colors, settings)
        )
        self.thread.daemon = True
        self.thread.start()
    
    def stop_bot(self):
        """Stop the painting bot"""
        self.is_running = False
    
    def _check_mouse_movement(self):
        """Check if mouse has moved from last bot position (user movement)"""
        if self.last_bot_mouse_pos is None:
            return False
        
        current_pos = pyautogui.position()
        # Check if mouse moved from where bot last placed it
        moved = abs(current_pos.x - self.last_bot_mouse_pos.x) > 10 or abs(current_pos.y - self.last_bot_mouse_pos.y) > 10
        
        if moved and not self.mouse_moved:
            self.mouse_moved = True
            self.logger.info("User mouse movement detected - cancelling bot")
        
        return moved
    
    def _bot_click(self, x, y):
        """Bot click that updates last known position"""
        pyautogui.click(x, y)
        self.last_bot_mouse_pos = pyautogui.position()
    
    def _bot_worker(self, message_queue, enabled_colors, settings):
        """Bot worker function (runs in separate thread)"""
        try:
            total_pixels_painted = 0
            pixel_limit = settings['pixel_limit']
            tolerance = settings['tolerance']
            delay = settings['delay']
            
            self.logger.bot_start(pixel_limit)
            
            for color in enabled_colors:
                if not self.is_running or total_pixels_painted >= pixel_limit or self._check_mouse_movement():
                    break
                
                total_pixels_painted = self._paint_color(
                    color, total_pixels_painted, pixel_limit, 
                    tolerance, delay, message_queue
                )
            
            # Determine completion reason
            limit_reached = total_pixels_painted >= pixel_limit
            cancelled_by_mouse = self.mouse_moved
            
            message_queue.put({
                'type': 'bot_complete',
                'total_painted': total_pixels_painted,
                'limit_reached': limit_reached,
                'cancelled_by_mouse': cancelled_by_mouse
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
        
        self.logger.debug(f"Painting {len(positions)} pixels with {color['name']} "
                         f"(Total: {total_pixels_painted + len(positions)}/{pixel_limit})")
        
        # Click color in palette
        px, py = self.data_manager.color_position_map[target_rgb]
        self._bot_click(px, py)
        time.sleep(0.2)
        
        # Paint positions
        for pos_i, (x, y) in enumerate(positions):
            if not self.is_running or self._check_mouse_movement():
                break
            
            self._bot_click(x + self.data_manager.canvas_region[0], y + self.data_manager.canvas_region[1])
            time.sleep(delay / 1000.0)
            total_pixels_painted += 1
            
            # Update progress every 10 pixels
            if pos_i % 10 == 0 or pos_i == len(positions) - 1:
                progress = (total_pixels_painted / pixel_limit) * 100
                self.logger.bot_progress(total_pixels_painted, pixel_limit, color['name'])
                message_queue.put({
                    'type': 'progress',
                    'progress': min(progress, 100),
                    'status': f"Painting {color['name']} ({total_pixels_painted}/{pixel_limit} pixels)"
                })
            
            if total_pixels_painted >= pixel_limit:
                break
        
        return total_pixels_painted