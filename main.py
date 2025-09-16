import pyautogui
import numpy as np
from PIL import Image, ImageDraw
import time
import keyboard
import math
import cv2
import statistics
from data import color_palette


def get_screen(region=None):
    screenshot = pyautogui.screenshot(region=region)
    return np.array(screenshot)


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


def detect_palette_colors(palette_img_rgb, palette_region, known_colors, tolerance=15):
    """
    Detects color swatches by searching for each known color individually.
    Expects an RGB image.
    Returns a dictionary mapping color tuple -> screen coordinates.
    """
    color_map = {}
    # Convert the input RGB image to BGR for OpenCV processing
    palette_img_bgr = cv2.cvtColor(palette_img_rgb, cv2.COLOR_RGB2BGR)

    for color_data in known_colors:
        target_rgb = tuple(color_data["rgb"])
        target_bgr = target_rgb[::-1]

        lower_bound = np.array([max(0, c - tolerance) for c in target_bgr])
        upper_bound = np.array([min(255, c + tolerance) for c in target_bgr])

        # Use the BGR image for color masking
        mask = cv2.inRange(palette_img_bgr, lower_bound, upper_bound)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest_contour) > 100:  # Filter noise
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])

                    screen_x = palette_region[0] + cx
                    screen_y = palette_region[1] + cy
                    color_map[target_rgb] = (screen_x, screen_y)

    return color_map


def estimate_pixel_size(img, min_size=5, max_size=50, debug_filename="debug_size_estimation.png"):
    """
    Estimates the grid pixel size and saves a debug image showing the process.
    """
    # Create a copy for drawing
    debug_img = img.copy()

    # Convert to grayscale and find edges with very sensitive settings
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 0, 0, apertureSize=3)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Collect all valid square sizes
    square_sizes = []
    square_contours = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        is_square_like = 0.8 <= w / h <= 1.2
        is_right_size = min_size < w < max_size and min_size < h < max_size

        if is_square_like and is_right_size:
            square_sizes.append(w)
            square_contours.append((cnt, w, h))

    if len(square_sizes) < 10:
        print("Warning: Could not find enough squares. Falling back to default (22).")
        return 22

    sorted_sizes = sorted(square_sizes)

    # Find the smallest group (these should be preview squares)
    # Take the first 25% of sizes as potential previews
    preview_count = max(1, len(sorted_sizes) // 4)
    potential_previews = sorted_sizes[:preview_count]

    # Get median size of the smallest squares (preview squares)
    preview_median = statistics.median(potential_previews)

    # Calculate expected pixel size (preview * 3)
    expected_pixel_size = preview_median * 3

    # Set tolerance for what we consider valid single pixels
    pixel_min = expected_pixel_size * 0.8
    pixel_max = expected_pixel_size * 1.2

    # print(f"Debug: Preview median={preview_median}, Expected pixel={expected_pixel_size}")
    # print(f"Debug: Accepting pixels between {pixel_min} and {pixel_max}")

    pixel_sizes = []
    preview_sizes = []
    filtered_out = 0

    for cnt, w, h in square_contours:
        x, y, _, _ = cv2.boundingRect(cnt)

        if w <= preview_median * 1.5:  # Definitely a preview
            cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 1)  # Green
            preview_sizes.append(w)
        elif pixel_min <= w <= pixel_max:  # Valid single pixel
            cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 0, 255), 1)  # Red
            pixel_sizes.append(w)
        else:  # Too big - probably 2x2, 3x3, etc.
            cv2.rectangle(
                debug_img, (x, y), (x + w, y + h), (128, 128, 128), 1
            )  # Gray (filtered out)
            filtered_out += 1

    if not pixel_sizes:
        print("Warning: Could not find valid single pixel squares. Using calculated size.")
        estimated_size = round(expected_pixel_size)
    else:
        estimated_size = round(statistics.median(pixel_sizes))

    # print(f"Debug: Found {len(preview_sizes)} previews, {len(pixel_sizes)} pixels, {filtered_out} filtered out")

    # Add text to the debug image
    text = f"Estimated Pixel Size: {estimated_size}"
    cv2.putText(debug_img, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.imwrite(debug_filename, debug_img)
    print(f"Size estimation debug image saved: {debug_filename}")

    return estimated_size


def find_pixels_to_paint(img, target_color_bgr, pixel_size, tolerance=5, debug_filename=None):
    """
    Finds pixels to paint. Expects a BGR image and a BGR target color.
    """
    h, w, _ = img.shape
    matches = []

    debug_img = img.copy() if debug_filename else None
    debug_counter = 0
    max_debug_items = 50  # Limit how many debug markers we draw

    # Iterate over the grid using the estimated pixel_size
    step = pixel_size + 1  # Assuming 1px gap
    for y in range(0, h - pixel_size, step):
        for x in range(0, w - pixel_size, step):
            cx = x + pixel_size // 2
            cy = y + pixel_size // 2

            preview_color = img[cy, cx]
            is_preview_match = all(
                abs(int(preview_color[i]) - target_color_bgr[i]) <= tolerance
                for i in range(3)
            )

            decision = "SKIP"
            if is_preview_match:
                pixel_color = img[y + 2, x + 2]
                is_pixel_match = all(
                    abs(int(pixel_color[i]) - target_color_bgr[i]) <= tolerance
                    for i in range(3)
                )

                if not is_pixel_match:
                    matches.append((cx, cy))
                    decision = "PAINT"

            # Draw debug info if enabled
            if debug_img is not None and debug_counter < max_debug_items:
                # Draw grid cell
                cv2.rectangle(
                    debug_img,
                    (x, y),
                    (x + pixel_size, y + pixel_size),
                    (255, 255, 0),
                    1,
                )
                # Draw preview sample point (blue)
                cv2.circle(debug_img, (cx, cy), 2, (255, 0, 0), -1)
                # Draw container sample point (red)
                cv2.circle(debug_img, (x + 2, y + 2), 2, (0, 0, 255), -1)
                # Write decision
                if decision == "PAINT":
                    cv2.putText(
                        debug_img,
                        decision,
                        (x, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (0, 255, 0),
                        1,
                    )
                    debug_counter += 1
                # Optionally draw skip decisions for clarity
                # else:
                #     cv2.putText(debug_img, decision, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)

    if debug_img is not None:
        cv2.imwrite(debug_filename, debug_img)
        print(f"Painting scan debug image saved: {debug_filename}")

    return matches


def auto_click_positions(positions, offset=(0, 0)):
    print("Press ESC to stop at any time.")
    for x, y in positions:
        if keyboard.is_pressed("esc"):
            print("Stopped by user.")
            break
        pyautogui.click(x + offset[0], y + offset[1])
        time.sleep(0.02)


def save_palette_debug_image(palette_img_rgb, color_map, palette_region, filename="debug_palette.png"):
    # Convert to BGR for OpenCV drawing
    debug_img = cv2.cvtColor(palette_img_rgb, cv2.COLOR_RGB2BGR)
    box_size = 10
    for color_rgb, screen_coords in color_map.items():
        img_x = screen_coords[0] - palette_region[0]
        img_y = screen_coords[1] - palette_region[1]
        # Draw a green square marker
        cv2.rectangle(
            debug_img,
            (img_x - box_size // 2, img_y - box_size // 2),
            (img_x + box_size // 2, img_y + box_size // 2),
            (0, 255, 0),
            2,
        )
    cv2.imwrite(filename, debug_img)
    print(f"Palette debug image saved: {filename}")


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


def main():
    print("Focus the browser window. Press Enter to continue...")
    input()
    canvas_region = select_region()
    palette_region = select_palette_region()

    # Take screenshots for analysis
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

        if color["premium"] == True and color.get("bought") == False:
            continue  # Skip not bought premium colors

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