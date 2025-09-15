import pyautogui
import numpy as np
from PIL import Image, ImageDraw
import time
import keyboard
import math
import cv2

color_palette = [
    # {"id": 0, "premium": False, "name": "Transparent", "rgb": [0, 0, 0]},
    {"id": 1, "premium": False, "name": "Black", "rgb": [0, 0, 0]},
    {"id": 2, "premium": False, "name": "Dark Gray", "rgb": [60, 60, 60]},
    {"id": 3, "premium": False, "name": "Gray", "rgb": [120, 120, 120]},
    {"id": 4, "premium": False, "name": "Light Gray", "rgb": [210, 210, 210]},
    {"id": 5, "premium": False, "name": "White", "rgb": [255, 255, 255]},
    {"id": 6, "premium": False, "name": "Deep Red", "rgb": [96, 0, 24]},
    {"id": 7, "premium": False, "name": "Red", "rgb": [237, 28, 36]},
    {"id": 8, "premium": False, "name": "Orange", "rgb": [255, 127, 39]},
    {"id": 9, "premium": False, "name": "Gold", "rgb": [246, 170, 9]},
    {"id": 10, "premium": False, "name": "Yellow", "rgb": [249, 221, 59]},
    {"id": 11, "premium": False, "name": "Light Yellow", "rgb": [255, 250, 188]},
    {"id": 12, "premium": False, "name": "Dark Green", "rgb": [14, 185, 104]},
    {"id": 13, "premium": False, "name": "Green", "rgb": [19, 230, 123]},
    {"id": 14, "premium": False, "name": "Light Green", "rgb": [135, 255, 94]},
    {"id": 15, "premium": False, "name": "Dark Teal", "rgb": [12, 129, 110]},
    {"id": 16, "premium": False, "name": "Teal", "rgb": [16, 174, 166]},
    {"id": 17, "premium": False, "name": "Light Teal", "rgb": [19, 225, 190]},
    {"id": 18, "premium": False, "name": "Dark Blue", "rgb": [40, 80, 158]},
    {"id": 19, "premium": False, "name": "Blue", "rgb": [64, 147, 228]},
    {"id": 20, "premium": False, "name": "Cyan", "rgb": [96, 247, 242]},
    {"id": 21, "premium": False, "name": "Indigo", "rgb": [107, 80, 246]},
    {"id": 22, "premium": False, "name": "Light Indigo", "rgb": [153, 177, 251]},
    {"id": 23, "premium": False, "name": "Dark Purple", "rgb": [120, 12, 153]},
    {"id": 24, "premium": False, "name": "Purple", "rgb": [170, 56, 185]},
    {"id": 25, "premium": False, "name": "Light Purple", "rgb": [224, 159, 249]},
    {"id": 26, "premium": False, "name": "Dark Pink", "rgb": [203, 0, 122]},
    {"id": 27, "premium": False, "name": "Pink", "rgb": [236, 31, 128]},
    {"id": 28, "premium": False, "name": "Light Pink", "rgb": [243, 141, 169]},
    {"id": 29, "premium": False, "name": "Dark Brown", "rgb": [104, 70, 52]},
    {"id": 30, "premium": False, "name": "Brown", "rgb": [149, 104, 42]},
    {"id": 31, "premium": False, "name": "Beige", "rgb": [248, 178, 119]},
    {"id": 32, "premium": True, "name": "Medium Gray", "rgb": [170, 170, 170]},
    {"id": 33, "premium": True, "name": "Dark Red", "rgb": [165, 14, 30]},
    {"id": 34, "premium": True, "name": "Light Red", "rgb": [250, 128, 114]},
    {"id": 35, "premium": True, "name": "Dark Orange", "rgb": [228, 92, 26]},
    {"id": 36, "premium": True, "name": "Light Tan", "rgb": [214, 181, 148]},
    {"id": 37, "premium": True, "name": "Dark Goldenrod", "rgb": [156, 132, 49]},
    {"id": 38, "premium": True, "name": "Goldenrod", "rgb": [197, 173, 49]},
    {"id": 39, "premium": True, "name": "Light Goldenrod", "rgb": [232, 212, 95]},
    {"id": 40, "premium": True, "name": "Dark Olive", "rgb": [74, 107, 58]},
    {"id": 41, "premium": True, "name": "Olive", "rgb": [90, 148, 74]},
    {"id": 42, "premium": True, "name": "Light Olive", "rgb": [132, 197, 115]},
    {"id": 43, "premium": True, "name": "Dark Cyan", "rgb": [15, 121, 159]},
    {"id": 44, "premium": True, "name": "Light Cyan", "rgb": [187, 250, 242]},
    {"id": 45, "premium": True, "name": "Light Blue", "rgb": [125, 199, 255]},
    {"id": 46, "premium": True, "name": "Dark Indigo", "rgb": [77, 49, 184]},
    {"id": 47, "premium": True, "name": "Dark Slate Blue", "rgb": [74, 66, 132]},
    {"id": 48, "premium": True, "name": "Slate Blue", "rgb": [122, 113, 196]},
    {"id": 49, "premium": True, "name": "Light Slate Blue", "rgb": [181, 174, 241]},
    {"id": 50, "premium": True, "name": "Light Brown", "rgb": [219, 164, 99]},
    {"id": 51, "premium": True, "name": "Dark Beige", "rgb": [209, 128, 81]},
    {"id": 52, "premium": True, "name": "Light Beige", "rgb": [255, 197, 165]},
    {"id": 53, "premium": True, "name": "Dark Peach", "rgb": [155, 82, 73]},
    {"id": 54, "premium": True, "name": "Peach", "rgb": [209, 128, 120]},
    {"id": 55, "premium": True, "name": "Light Peach", "rgb": [250, 182, 164]},
    {"id": 56, "premium": True, "name": "Dark Tan", "rgb": [123, 99, 82]},
    {"id": 57, "premium": True, "name": "Tan", "rgb": [156, 132, 107]},
    {"id": 58, "premium": True, "name": "Dark Slate", "rgb": [51, 57, 65]},
    {"id": 59, "premium": True, "name": "Slate", "rgb": [109, 117, 141]},
    {"id": 60, "premium": True, "name": "Light Slate", "rgb": [179, 185, 209]},
    {"id": 61, "premium": True, "name": "Dark Stone", "rgb": [109, 100, 63]},
    {"id": 62, "premium": True, "name": "Stone", "rgb": [148, 140, 107]},
    {"id": 63, "premium": True, "name": "Light Stone", "rgb": [205, 197, 158]}
]

def get_screen(region=None):
    screenshot = pyautogui.screenshot(region=region)
    return np.array(screenshot)

def select_region():
    print("Move your mouse to the TOP-LEFT corner of the browser window and press Enter.")
    input()
    x1, y1 = pyautogui.position()
    print(f"Top-left corner: ({x1}, {y1})")
    print("Now move your mouse to the BOTTOM-RIGHT corner of the browser window and press Enter.")
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

def find_color_positions(img, target_color, tolerance=0, grid_size=10):
    matches = []
    h, w = img.shape[:2]
    for y in range(0, h, grid_size):
        for x in range(0, w, grid_size):
            sample = img[y, x][:3]
            if all(abs(sample[i] - target_color[i]) <= tolerance for i in range(3)):
                matches.append((x, y))
    return matches

def detect_palette_colors(palette_img, palette_region, known_colors, tolerance=15):
    """
    Detects color swatches in a region, finds their center, and maps them to known colors.
    Returns a dictionary mapping color tuple -> screen coordinates.
    """
    # Convert to grayscale and threshold to find shapes. Lowered threshold to catch lighter colors.
    gray = cv2.cvtColor(palette_img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY_INV)

    # Find contours of the color swatches
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    color_map = {}
    known_color_tuples = {tuple(c['rgb']): c for c in known_colors}

    for cnt in contours:
        if cv2.contourArea(cnt) < 100:
            continue

        x, y, w, h = cv2.boundingRect(cnt)
        cx = x + w // 2
        cy = y + h // 2

        # Sample a small area around the center and average the color
        # This is more robust against icons or anti-aliasing
        sample_size = 5
        y1, y2 = max(0, cy - sample_size//2), min(palette_img.shape[0], cy + sample_size//2)
        x1, x2 = max(0, cx - sample_size//2), min(palette_img.shape[1], cx + sample_size//2)
        swatch_area = palette_img[y1:y2, x1:x2]
        
        if swatch_area.size == 0:
            continue

        # Calculate the mean color of the BGR channels
        avg_color = tuple(np.mean(swatch_area, axis=(0, 1)).astype(int))

        for known_rgb in known_color_tuples:
            if all(abs(avg_color[i] - known_rgb[i]) <= tolerance for i in range(3)):
                screen_x = palette_region[0] + cx
                screen_y = palette_region[1] + cy
                color_map[known_rgb] = (screen_x, screen_y)
                break

    return color_map

def find_pixels_to_paint(img, target_color, tolerance=5):
    """
    Finds pixels where the preview (center) matches the target color,
    but the surrounding pixel does not.
    """
    h, w = img.shape[:2]
    # This pixel size estimation is a placeholder. A more robust method may be needed.
    pixel_size = 15 # A common size, adjust if needed
    preview_size = pixel_size // 3
    matches = []

    for y in range(0, h - pixel_size + 1, pixel_size):
        for x in range(0, w - pixel_size + 1, pixel_size):
            # Get center of pixel for preview sampling
            cx = x + pixel_size // 2
            cy = y + pixel_size // 2

            # Sample preview color (center)
            preview_color = img[cy, cx][:3]

            # Check if preview matches the target color
            is_preview_match = all(abs(int(preview_color[i]) - target_color[i]) <= tolerance for i in range(3))

            if is_preview_match:
                # Sample outer pixel color to see if it's already painted
                # Take a corner sample, assuming it's not part of the preview
                pixel_color = img[y + 2, x + 2][:3]
                is_pixel_match = all(abs(int(pixel_color[i]) - target_color[i]) <= tolerance for i in range(3))

                # If preview matches but the pixel itself doesn't, we need to paint it
                if not is_pixel_match:
                    matches.append((cx, cy))
    return matches


def auto_click_positions(positions, offset=(0,0)):
    print("Press ESC to stop at any time.")
    for x, y in positions:
        if keyboard.is_pressed('esc'):
            print("Stopped by user.")
            break
        pyautogui.click(x + offset[0], y + offset[1])
        time.sleep(0.02)

def save_palette_debug_image(palette_img, color_map, palette_region, filename="debug_palette.png"):
    debug_img = Image.fromarray(palette_img.copy())
    draw = ImageDraw.Draw(debug_img)
    box_size = 10
    for color_rgb, screen_coords in color_map.items():
        # Convert screen coords back to image coords for drawing
        img_x = screen_coords[0] - palette_region[0]
        img_y = screen_coords[1] - palette_region[1]
        draw.rectangle([img_x - box_size//2, img_y - box_size//2, img_x + box_size//2, img_y + box_size//2], outline="lime", width=3)
    debug_img.save(filename)
    print(f"Palette debug image saved: {filename}")

def main():
    print("Focus the browser window. Press Enter to continue...")
    input()
    canvas_region = select_region()
    palette_region = select_palette_region()
    palette_img = get_screen(palette_region)

    # Detect colors and their positions from the selected palette region
    color_position_map = detect_palette_colors(palette_img, palette_region, color_palette)
    print(f"Detected {len(color_position_map)} colors in the selected palette region.")
    save_palette_debug_image(palette_img, color_position_map, palette_region)

    # --- ADDED CONFIRMATION STEP ---
    print("\nReview the debug_palette.png file.")
    print("Press ENTER to start painting or ESC to cancel.")
    while True:
        if keyboard.is_pressed('enter'):
            print("Starting...")
            break
        if keyboard.is_pressed('esc'):
            print("Cancelled by user. Exiting.")
            return
        time.sleep(0.05)
    # --- END CONFIRMATION ---

    for color in color_palette:
        if keyboard.is_pressed('esc'):
            print("Stopped by user.")
            break

        # if color['premium']:
        #     continue # Skip premium colors

        target_rgb = tuple(color['rgb'])
        if target_rgb in color_position_map:
            print(f"Processing color {color['name']} ({color['rgb']})")
            # Click the color in the palette to select it
            px, py = color_position_map[target_rgb]
            pyautogui.click(px, py)
            time.sleep(0.2)

            # Scan canvas for pixels that need painting with this color
            img = get_screen(canvas_region)
            positions = find_pixels_to_paint(img, target_rgb)
            print(f"Found {len(positions)} spots to paint for {color['name']}")

            if positions:
                auto_click_positions(positions, offset=(canvas_region[0], canvas_region[1]))
            time.sleep(0.5)
        else:
            # This color was not found in the user-selected palette region
            pass

if __name__ == "__main__":
    main()