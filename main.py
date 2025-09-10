import pyautogui
import numpy as np
from PIL import Image, ImageDraw
import time
import keyboard
import math

color_palette = [
    {"id": 0, "premium": False, "name": "Transparent", "rgb": [0, 0, 0]},
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