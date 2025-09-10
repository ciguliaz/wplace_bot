import pyautogui
import numpy as np
from PIL import Image
import time
import keyboard

def get_screen(region=None):
    screenshot = pyautogui.screenshot(region=region)
    return np.array(screenshot)

def pick_color():
    print("Move your mouse over the preview color and press Enter.")
    input()
    x, y = pyautogui.position()
    color = pyautogui.screenshot().getpixel((x, y))
    print(f"Selected color: {color}")
    return color

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

def find_color_positions(img, target_color, tolerance=20, grid_size=10):
    matches = []
    h, w = img.shape[:2]
    for y in range(0, h, grid_size):
        for x in range(0, w, grid_size):
            sample = img[y, x][:3]
            if all(abs(sample[i] - target_color[i]) <= tolerance for i in range(3)):
                matches.append((x, y))
    return matches

def auto_click_positions(positions, offset=(0,0)):
    print("Press ESC to stop at any time.")
    for x, y in positions:
        if keyboard.is_pressed('esc'):
            print("Stopped by user.")
            break
        pyautogui.click(x + offset[0], y + offset[1])
        time.sleep(0.02)

def main():
    print("Focus the browser window. Press Enter to continue...")
    input()
    region = select_region()
    target_color = pick_color()
    img = get_screen(region)
    positions = find_color_positions(img, target_color)
    print(f"Found {len(positions)} spots to click.")
    # Offset click positions by region's top-left corner
    auto_click_positions(positions, offset=(region[0], region[1]))

if __name__ == "__main__":
    main()