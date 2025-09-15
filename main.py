import pyautogui
import numpy as np
from PIL import Image, ImageDraw
import time
import keyboard
import math
import cv2
import statistics

color_palette = [
    # {"id": 0, "premium": False, "name": "Transparent", "rgb": [0, 0, 0]},
    {"id": 1, "premium": False, "name": "Black", "rgb": [0, 0, 0]},
    {"id": 2, "premium": False, "name": "Dark Gray", "rgb": [60, 60, 60]},
    {"id": 3, "premium": False, "name": "Gray", "rgb": [120, 120, 120]},
    {"id": 4, "premium": False, "name": "Light Gray", "rgb": [210, 210, 210]},
    # {"id": 5, "premium": False, "name": "White", "rgb": [255, 255, 255]},
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
    {"id": 33, "premium": True, "name": "Dark Red", "rgb": [165, 14, 30], "bought": False},
    {"id": 34, "premium": True, "name": "Light Red", "rgb": [250, 128, 114]},
    {"id": 35, "premium": True, "name": "Dark Orange", "rgb": [228, 92, 26], "bought": False},
    {"id": 36, "premium": True, "name": "Light Tan", "rgb": [214, 181, 148]},
    {"id": 37, "premium": True, "name": "Dark Goldenrod", "rgb": [156, 132, 49], "bought": False},
    {"id": 38, "premium": True, "name": "Goldenrod", "rgb": [197, 173, 49], "bought": False},
    {"id": 39, "premium": True, "name": "Light Goldenrod", "rgb": [232, 212, 95], "bought": False},
    {"id": 40, "premium": True, "name": "Dark Olive", "rgb": [74, 107, 58], "bought": False},
    {"id": 41, "premium": True, "name": "Olive", "rgb": [90, 148, 74], "bought": False},
    {"id": 42, "premium": True, "name": "Light Olive", "rgb": [132, 197, 115], "bought": False},
    {"id": 43, "premium": True, "name": "Dark Cyan", "rgb": [15, 121, 159], "bought": False},
    {"id": 44, "premium": True, "name": "Light Cyan", "rgb": [187, 250, 242], "bought": False},
    {"id": 45, "premium": True, "name": "Light Blue", "rgb": [125, 199, 255], "bought": False},
    {"id": 46, "premium": True, "name": "Dark Indigo", "rgb": [77, 49, 184], "bought": False},
    {"id": 47, "premium": True, "name": "Dark Slate Blue", "rgb": [74, 66, 132]},
    {"id": 48, "premium": True, "name": "Slate Blue", "rgb": [122, 113, 196]},
    {"id": 49, "premium": True, "name": "Light Slate Blue", "rgb": [181, 174, 241]},
    {"id": 50, "premium": True, "name": "Light Brown", "rgb": [219, 164, 99], "bought": False},
    {"id": 51, "premium": True, "name": "Dark Beige", "rgb": [209, 128, 81], "bought": False},
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

def find_color_positions(img, target_color, tolerance=1, grid_size=1000):
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
    Detects color swatches by searching for each known color individually.
    Returns a dictionary mapping color tuple -> screen coordinates.
    """
    color_map = {}
    
    for color_data in known_colors:
        target_rgb = color_data['rgb']
        
        # Define the lower and upper bounds for the color search
        lower_bound = np.array([max(0, c - tolerance) for c in target_rgb])
        upper_bound = np.array([min(255, c + tolerance) for c in target_rgb])
        
        # Create a mask that isolates pixels matching the target color
        mask = cv2.inRange(palette_img, lower_bound, upper_bound)
        
        # Find contours on the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find the largest contour, which should be the color swatch
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest_contour) > 100: # Filter noise
                # Get the center of the swatch
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    # Map the known color to its absolute screen coordinates
                    screen_x = palette_region[0] + cx
                    screen_y = palette_region[1] + cy
                    color_map[tuple(target_rgb)] = (screen_x, screen_y)

    return color_map

def estimate_pixel_size(img, min_size=5, max_size=50):
    """
    Estimates the grid pixel size from a canvas image using edge detection.
    """
    # Convert to grayscale and find edges
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # Find contours of the squares
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    sizes = []
    for cnt in contours:
        # Get bounding box for each contour
        x, y, w, h = cv2.boundingRect(cnt)
        
        # Filter for contours that are likely our grid pixels
        # They should be roughly square and within a reasonable size range
        is_square_like = 0.8 <= w / h <= 1.2
        is_right_size = min_size < w < max_size and min_size < h < max_size
        
        if is_square_like and is_right_size:
            sizes.append(w)
            sizes.append(h)
            
    if not sizes:
        print("Warning: Could not determine pixel size automatically. Falling back to default (15).")
        return 15

    # Return the most common size (mode)
    return round(statistics.mode(sizes))


def find_pixels_to_paint(img, target_color, pixel_size, tolerance=5):
    """
    Finds pixels that need to be painted with the dynamically determined pixel_size.
    """
    h, w = img.shape[:2]
    preview_size = max(1, pixel_size // 3) # Ensure preview is at least 1 pixel
    matches = []

    # Iterate over the grid using the estimated pixel_size
    for y in range(0, h - pixel_size + 1, pixel_size):
        for x in range(0, w - pixel_size + 1, pixel_size):
            # Get center of pixel for preview sampling
            cx = x + pixel_size // 2
            cy = y + pixel_size // 2

            # Sample preview color (center)
            preview_color = img[cy, cx][:3]

            is_preview_match = all(abs(int(preview_color[i]) - target_color[i]) <= tolerance for i in range(3))

            if is_preview_match:
                # Sample outer pixel color to see if it's already painted
                pixel_color = img[y + 2, x + 2][:3]
                is_pixel_match = all(abs(int(pixel_color[i]) - target_color[i]) <= tolerance for i in range(3))

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

    # --- DYNAMIC PIXEL SIZE ESTIMATION ---
    print("Estimating pixel size from canvas...")
    canvas_img_for_estimate = get_screen(canvas_region)
    pixel_size = estimate_pixel_size(canvas_img_for_estimate)
    print(f"Estimated pixel size: {pixel_size}x{pixel_size}")
    # --- END ESTIMATION ---

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
        # print(f"Checking color {color['name']} ({color['rgb']}), premium={color['premium']}, bought={color.get('bought')}")
        if color['premium'] == True and color.get('bought') == False:
            # print(f"Skipping premium color {color['name']} as it is not bought.")
            continue # Skip not bought premium colors

        target_rgb = tuple(color['rgb'])
        if target_rgb in color_position_map:
            # print(f"Processing color {color['name']} ({color['rgb']})")
            # Click the color in the palette to select it
            px, py = color_position_map[target_rgb]
            pyautogui.click(px, py)
            time.sleep(0.2)

            # Scan canvas for pixels that need painting with this color
            img = get_screen(canvas_region)
            # Pass the dynamically found pixel_size to the function
            positions = find_pixels_to_paint(img, target_rgb, pixel_size)
            print(f"Found {len(positions)} spots to paint for {color['name']}")

            if positions:
                auto_click_positions(positions, offset=(canvas_region[0], canvas_region[1]))
            time.sleep(0.5)
        else:
            # This color was not found in the user-selected palette region
            pass

if __name__ == "__main__":
    main()