import pyautogui
import numpy as np


def get_screen(region=None):
    """Capture screen region using pyautogui."""
    screenshot = pyautogui.screenshot(region=region)
    return np.array(screenshot)