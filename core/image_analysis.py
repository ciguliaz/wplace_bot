import cv2
import statistics


def estimate_pixel_size(img, min_size=5, max_size=50, debug_filename="debug_size_estimation.png"):
    """
    Estimates the grid pixel size and saves a debug image showing the process.
    """
    debug_img = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 0, 0, apertureSize=3)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

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
    preview_count = max(1, len(sorted_sizes) // 4)
    potential_previews = sorted_sizes[:preview_count]
    preview_median = statistics.median(potential_previews)
    expected_pixel_size = preview_median * 3
    pixel_min = expected_pixel_size * 0.8
    pixel_max = expected_pixel_size * 1.2

    pixel_sizes = []
    for cnt, w, h in square_contours:
        x, y, _, _ = cv2.boundingRect(cnt)

        if w <= preview_median * 1.5:
            cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 0), 1)
        elif pixel_min <= w <= pixel_max:
            cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 0, 255), 1)
            pixel_sizes.append(w)
        else:
            cv2.rectangle(debug_img, (x, y), (x + w, y + h), (128, 128, 128), 1)

    if not pixel_sizes:
        print("Warning: Could not find valid single pixel squares. Using calculated size.")
        estimated_size = round(expected_pixel_size)
    else:
        estimated_size = round(statistics.median(pixel_sizes))

    cv2.imwrite(debug_filename, debug_img)
    print(f"Size estimation debug image saved: {debug_filename}")
    return estimated_size


def find_pixels_to_paint(img, target_color_bgr, pixel_size, tolerance=1, debug_filename=None):
    """
    Finds pixels to paint. Expects a BGR image and a BGR target color.
    """
    h, w, _ = img.shape
    matches = []

    debug_img = img.copy() if debug_filename else None
    debug_counter = 0
    max_debug_items = 50

    step = pixel_size + 1
    for y in range(0, h - pixel_size, step):
        for x in range(0, w - pixel_size, step):
            cx = x + pixel_size // 2
            cy = y + pixel_size // 2

            preview_color = img[cy, cx]
            is_preview_match = all(
                abs(int(preview_color[i]) - target_color_bgr[i]) <= tolerance
                for i in range(3)
            )

            if is_preview_match:
                pixel_color = img[y + 2, x + 2]
                is_pixel_match = all(
                    abs(int(pixel_color[i]) - target_color_bgr[i]) <= tolerance
                    for i in range(3)
                )

                if not is_pixel_match:
                    matches.append((cx, cy))

                    if debug_img is not None and debug_counter < max_debug_items:
                        cv2.rectangle(debug_img, (x, y), (x + pixel_size, y + pixel_size), (255, 255, 0), 1)
                        cv2.circle(debug_img, (cx, cy), 2, (255, 0, 0), -1)
                        cv2.circle(debug_img, (x + 2, y + 2), 2, (0, 0, 255), -1)
                        cv2.putText(debug_img, "PAINT", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                        debug_counter += 1

    if debug_img is not None:
        cv2.imwrite(debug_filename, debug_img)
        print(f"Painting scan debug image saved: {debug_filename}")

    return matches