import pyautogui
import keyboard
import time


def auto_click_positions(positions, offset=(0, 0)):
    """Automatically click at given positions with optional offset."""
    print("Press ESC to stop at any time.")
    for x, y in positions:
        if keyboard.is_pressed("esc"):
            print("Stopped by user.")
            break
        pyautogui.click(x + offset[0], y + offset[1])
        time.sleep(0.02)