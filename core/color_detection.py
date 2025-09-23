import cv2
import numpy as np


def detect_palette_colors(palette_img_rgb, palette_region, known_colors, tolerance=3):
    """
    Detects color swatches by searching for each known color individually.
    Expects an RGB image.
    Returns a dictionary mapping color tuple -> screen coordinates.
    """
    color_map = {}
    palette_img_bgr = cv2.cvtColor(palette_img_rgb, cv2.COLOR_RGB2BGR)

    for color_data in known_colors:
        target_rgb = tuple(color_data["rgb"])
        target_bgr = target_rgb[::-1]

        lower_bound = np.array([max(0, c - tolerance) for c in target_bgr])
        upper_bound = np.array([min(255, c + tolerance) for c in target_bgr])

        mask = cv2.inRange(palette_img_bgr, lower_bound, upper_bound)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest_contour) > 100:
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])

                    screen_x = palette_region[0] + cx
                    screen_y = palette_region[1] + cy
                    color_map[target_rgb] = (screen_x, screen_y)

    return color_map


def save_palette_debug_image(palette_img_rgb, color_map, palette_region, filename="debug_palette.png"):
    """Save debug image showing detected palette colors."""
    debug_img = cv2.cvtColor(palette_img_rgb, cv2.COLOR_RGB2BGR)
    box_size = 10
    for color_rgb, screen_coords in color_map.items():
        img_x = screen_coords[0] - palette_region[0]
        img_y = screen_coords[1] - palette_region[1]
        cv2.rectangle(
            debug_img,
            (img_x - box_size // 2, img_y - box_size // 2),
            (img_x + box_size // 2, img_y + box_size // 2),
            (0, 255, 0),
            2,
        )
    cv2.imwrite(filename, debug_img)
    print(f"Palette debug image saved: {filename}")