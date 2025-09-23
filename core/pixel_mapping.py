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