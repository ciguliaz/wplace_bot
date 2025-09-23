import pyautogui
import numpy as np
from PIL import Image, ImageDraw
import time
import keyboard
import math
import cv2
import statistics
import json
import os


# MOVED TO core/screen_capture.py
# def get_screen(region=None):
#     screenshot = pyautogui.screenshot(region=region)
#     return np.array(screenshot)


def select_region():
    print("Move your mouse to the TOP-LEFT corner of the browser window and press Enter.")
    input()
    x1, y1 = pyautogui.position()
    print(f"Top-left corner: ({x1}, {y1})")
    print(        "Now move your mouse to the BOTTOM-RIGHT corner of the browser window and press Enter."    )
    input()
    x2, y2 = pyautogui.position()
    print(f"Bottom-right corner: ({x2}, {y2})")
    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    print(f"Selected region: left={left}, top={top}, width={width}, height={height}")
    return (left, top, width, height)


def select_palette_region():
    print("Move your mouse to the TOP-LEFT corner of the palette and press Enter.")
    input()
    x1, y1 = pyautogui.position()
    print(f"Palette top-left: ({x1}, {y1})")
    print("Now move your mouse to the BOTTOM-RIGHT corner of the palette and press Enter.")
    input()
    x2, y2 = pyautogui.position()
    print(f"Palette bottom-right: ({x2}, {y2})")
    left = min(x1, x2)
    top = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    print(f"Palette region: left={left}, top={top}, width={width}, height={height}")
    return (left, top, width, height)


def get_palette_positions(palette_region, num_colors):
    left, top, width, height = palette_region
    box_width = width // num_colors
    positions = []
    for i in range(num_colors):
        cx = left + box_width * i + box_width // 2
        cy = top + height // 2
        positions.append((cx, cy))
    return positions


def find_color_positions(img, target_color, tolerance=1, grid_size=1000):
    matches = []
    h, w = img.shape[:2]
    for y in range(0, h, grid_size):
        for x in range(0, w, grid_size):
            sample = img[y, x][:3]
            if all(abs(sample[i] - target_color[i]) <= tolerance for i in range(3)):
                matches.append((x, y))
    return matches


# MOVED TO core/color_detection.py
# def detect_palette_colors(palette_img_rgb, palette_region, known_colors, tolerance=3):


# MOVED TO core/image_analysis.py
# def estimate_pixel_size(img, min_size=5, max_size=50, debug_filename="debug_size_estimation.png"):


# MOVED TO core/image_analysis.py
# def find_pixels_to_paint(img, target_color_bgr, pixel_size, tolerance=1, debug_filename=None):


# MOVED TO core/automation.py
# def auto_click_positions(positions, offset=(0, 0)):


# MOVED TO core/color_detection.py
# def save_palette_debug_image(palette_img_rgb, color_map, palette_region, filename="debug_palette.png"):


def build_pixel_map(img, pixel_size, preview_positions):
    """
    Builds a map of all pixel positions with their preview and pixel colors.
    Returns a dictionary: {(x, y): {'preview_color': bgr, 'pixel_color': bgr}}
    """
    pixel_map = {}

    for preview_x, preview_y in preview_positions:
        # Calculate the pixel container position from preview position
        pixel_x = preview_x - pixel_size // 2
        pixel_y = preview_y - pixel_size // 2

        # Make sure we're within image bounds
        if (
            pixel_y + 2 < img.shape[0] and pixel_x + 2 < img.shape[1]
            and pixel_y >= 0 and pixel_x >= 0
            and preview_y >= 0 and preview_x >= 0
            and preview_y < img.shape[0] and preview_x < img.shape[1]
        ):
            # Sample both preview color (center) and pixel color (container)
            preview_color = img[preview_y, preview_x]
            pixel_color = img[pixel_y + 2, pixel_x + 2]

            pixel_map[(preview_x, preview_y)] = {
                "preview_color": tuple(preview_color),
                "pixel_color": tuple(pixel_color),
            }

    return pixel_map


def get_preview_positions_from_estimation(img, pixel_size):
    """
    Extract all preview positions from the size estimation process.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 0, 0, apertureSize=3)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    preview_positions = []

    # Use same logic as estimate_pixel_size to find previews
    square_sizes = []
    square_contours = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        is_square_like = 0.8 <= w / h <= 1.2
        is_right_size = 5 < w < 50 and 5 < h < 50

        if is_square_like and is_right_size:
            square_sizes.append(w)
            square_contours.append((cnt, w, h))

    if len(square_sizes) < 10:
        return []

    sorted_sizes = sorted(square_sizes)
    preview_count = max(1, len(sorted_sizes) // 4)
    potential_previews = sorted_sizes[:preview_count]
    preview_median = statistics.median(potential_previews)

    for cnt, w, h in square_contours:
        if w <= preview_median * 1.5:  # This is a preview
            x, y, _, _ = cv2.boundingRect(cnt)
            center_x = x + w // 2
            center_y = y + h // 2
            preview_positions.append((center_x, center_y))

    return preview_positions


def find_pixels_to_paint_from_map(pixel_map, target_bgr, tolerance=5):
    """
    Uses the pre-built pixel map to find pixels that need painting.
    Only paints pixels where:
    1. The preview shows the target color (indicating intention to paint this color)
    2. The actual pixel container is NOT yet the target color
    """
    matches = []

    for (preview_x, preview_y), colors in pixel_map.items():
        preview_color = colors["preview_color"]
        pixel_color = colors["pixel_color"]

        # Check if preview shows the target color (user wants to paint this color here)
        preview_matches_target = all(
            abs(int(preview_color[i]) - target_bgr[i]) <= tolerance for i in range(3)
        )

        # Check if pixel is already the correct color
        pixel_already_correct = all(
            abs(int(pixel_color[i]) - target_bgr[i]) <= tolerance for i in range(3)
        )

        # Only paint if preview shows target color but pixel isn't painted yet
        if preview_matches_target and not pixel_already_correct:
            matches.append((preview_x, preview_y))

    return matches


def load_color_palette():
    """Load color palette from JSON file"""
    try:
        with open('colors.json', 'r') as f:
            data = json.load(f)
            return data['color_palette']
    except Exception as e:
        print(f"Failed to load colors.json: {e}")
        return []


def load_user_settings():
    """Load user settings to get bought status"""
    try:
        if os.path.exists('user_settings.json'):
            with open('user_settings.json', 'r') as f:
                return json.load(f)
        return {"colors": {}}
    except Exception as e:
        print(f"Failed to load user settings: {e}")
        return {"colors": {}}


def is_color_bought(color, user_settings):
    """Check if a premium color is bought"""
    if not color.get('premium', False):
        return True  # Free colors are always "bought"
    
    color_id = str(color['id'])
    return user_settings.get('colors', {}).get(color_id, {}).get('bought', False)


def main():
    color_palette = load_color_palette()
    user_settings = load_user_settings()

    print("Focus the browser window. Press Enter to continue...")
    input()
    canvas_region = select_region()
    palette_region = select_palette_region()

    # Take screenshots for analysis
    from core import get_screen, estimate_pixel_size, detect_palette_colors, save_palette_debug_image, auto_click_positions
    palette_img_rgb = get_screen(palette_region)
    canvas_img_rgb = get_screen(canvas_region)

    # Convert to BGR format for OpenCV functions
    palette_img_bgr = cv2.cvtColor(palette_img_rgb, cv2.COLOR_RGB2BGR)
    canvas_img_bgr = cv2.cvtColor(canvas_img_rgb, cv2.COLOR_RGB2BGR)

    # --- DYNAMIC PIXEL SIZE ESTIMATION ---
    print("Estimating pixel size from canvas...")
    pixel_size = estimate_pixel_size(canvas_img_bgr)
    print(f"Estimated pixel size: {pixel_size}x{pixel_size}")

    print("Building pixel map...")
    preview_positions = get_preview_positions_from_estimation(
        canvas_img_bgr, pixel_size
    )
    pixel_map = build_pixel_map(canvas_img_bgr, pixel_size, preview_positions)
    print(f"Built pixel map with {len(pixel_map)} pixels")

    # Detect colors and their positions from the selected palette region
    color_position_map = detect_palette_colors(
        palette_img_rgb, palette_region, color_palette
    )
    print(f"Detected {len(color_position_map)} colors in the selected palette region.")
    save_palette_debug_image(palette_img_rgb, color_position_map, palette_region)

    print("\nReview the debug images (debug_size_estimation.png, debug_palette.png).")
    print("Press ENTER to start painting or ESC to cancel.")
    while True:
        if keyboard.is_pressed("enter"):
            print("Starting...")
            break
        if keyboard.is_pressed("esc"):
            print("Cancelled by user. Exiting.")
            return
        time.sleep(0.05)

    is_first_color = True
    for color in color_palette:
        if keyboard.is_pressed("esc"):
            print("Stopped by user.")
            break

        # Check bought status from user_settings.json ONLY
        if not is_color_bought(color, user_settings):
            print(f"Skipping {color['name']} - not bought")
            continue

        target_rgb = tuple(color["rgb"])
        if target_rgb in color_position_map:
            target_bgr = target_rgb[::-1]
            positions = find_pixels_to_paint_from_map(pixel_map, target_bgr)
            print(f"Found {len(positions)} spots to paint for {color['name']}")

            if positions:
                px, py = color_position_map[target_rgb]
                pyautogui.click(px, py)
                time.sleep(0.2)
                auto_click_positions(
                    positions, offset=(canvas_region[0], canvas_region[1])
                )
            # time.sleep(0.5)


if __name__ == "__main__":
    main()