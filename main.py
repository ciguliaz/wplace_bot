import pyautogui
import numpy as np
from PIL import Image
import time

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
    for x, y in positions:
        pyautogui.click(x + offset[0], y + offset[1])
        time.sleep(0.02) # Adjust for site speed

def main():
    print("Focus the browser window. Press Enter to continue...")
    input()
    # Optionally, ask user to select the browser window region
    target_color = pick_color()
    img = get_screen()
    positions = find_color_positions(img, target_color)
    print(f"Found {len(positions)} spots to click.")
    auto_click_positions(positions)

if __name__ == "__main__":
    main()