import cv2
import numpy as np
import pyautogui
import pytesseract
import difflib

def extract_text_from_screen_region(screenshot, x, y, w, h):
    """Extract text from a specific screen region using OCR (pytesseract)."""
    region = screenshot.crop((x, y, x + w, y + h))
    return pytesseract.image_to_string(region, config='--psm 7').strip().lower(), region

def find_and_click_template_on_screen(screenshot_bgr, template_path, threshold=0.7):
    """Find a template image on screen using OpenCV template matching and click its center if found."""
    template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    if template is None:
        print(f"Reference image not found at {template_path}")
        return False
    result = cv2.matchTemplate(screenshot_bgr, template[:, :, :3], cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val > threshold:
        template_h, template_w = template.shape[:2]
        center_x = max_loc[0] + template_w // 2
        center_y = max_loc[1] + template_h // 2
        print(f"Template match found for {template_path} at ({center_x}, {center_y}) with match {max_val:.2f}. Clicking...")
        pyautogui.moveTo(center_x, center_y, duration=0.3)
        pyautogui.click()
        return True
    return False

def find_template_on_screen(screenshot_bgr, template_path, threshold=0.7):
    """Find a template image on screen using OpenCV template matching and return (location, shape) if found, else (None, None)."""
    template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    if template is None:
        print(f"Reference image not found at {template_path}")
        return None, None
    result = cv2.matchTemplate(screenshot_bgr, template[:, :, :3], cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val > threshold:
        return max_loc, template.shape[:2]
    return None, None

def convert_screenshot_to_bgr():
    """Take a screenshot and convert it to BGR format for OpenCV processing."""
    screenshot = pyautogui.screenshot()
    screenshot_np = np.array(screenshot)
    return cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR), screenshot

def fuzzy_text_match(text, target, threshold=0.7):
    """Compare text with target using fuzzy matching (difflib)."""
    similarity = difflib.SequenceMatcher(None, text, target).ratio()
    return similarity > threshold, similarity 