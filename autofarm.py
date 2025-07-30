import subprocess
import time
import cv2
import pyautogui
import pytesseract
from utils import extract_text_from_screen_region, find_and_click_template_on_screen, convert_screenshot_to_bgr, fuzzy_text_match

# =====================
# USER CONFIGURABLE SETTINGS
# =====================
TARGET_MISCRIT_NAME = 'Light Bludger'
PLATINUM_TRAINING = False
FARM_COOLDOWN = 20
BATTLE_CHECK_WINDOW = 15
REFERENCE_OBJECT_PATH = 'Insert_images/reference_image.png'
TURN_CARD_X, TURN_CARD_Y, TURN_CARD_W, TURN_CARD_H = 522, 965, 180, 25
POTION_DROP_PATH = 'reference_images/potion drop.png'
GOLD_DROP_PATH = 'reference_images/gold drop.png'
OKAY_TEMPLATE_PATH = 'reference_images/okay.png'
BATTLE_ENGINE_SCRIPT = 'battle_engine.py'
# =====================

def save_config_to_file():
    """Save current configuration to config_file.txt"""
    try:
        with open('config_file.txt', 'w') as f:
            f.write(f"{TARGET_MISCRIT_NAME}|{PLATINUM_TRAINING}")
        print(f"Configuration saved: {TARGET_MISCRIT_NAME}, Platinum Training: {PLATINUM_TRAINING}")
    except Exception as e:
        print(f"Error saving configuration: {e}")

def load_config_from_file():
    """Load configuration from config_file.txt and return (target_name, platinum_training)"""
    try:
        with open('config_file.txt', 'r') as f:
            content = f.read().strip()
            if '|' in content:
                target_name, platinum_training_str = content.split('|', 1)
                platinum_training = platinum_training_str.lower() == 'true'
                return target_name, platinum_training
            else:
                # Legacy format - just target name
                return content, True  # Default to True for platinum training
    except FileNotFoundError:
        return TARGET_MISCRIT_NAME, PLATINUM_TRAINING  # Use defaults if file doesn't exist
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return TARGET_MISCRIT_NAME, PLATINUM_TRAINING  # Use defaults on error

# Save current configuration to file
save_config_to_file()
print(f"Configuration saved to config_file.txt: {TARGET_MISCRIT_NAME}|{PLATINUM_TRAINING}")

def detect_battle_from_turn_indicator(screenshot):
    """Detect if a battle has started by looking for the 'It's your turn!' indicator."""
    turn_card_text, turn_card_area = extract_text_from_screen_region(screenshot, TURN_CARD_X, TURN_CARD_Y, TURN_CARD_W, TURN_CARD_H)
    turn_card_area.save('screenshots/turn_card_area_farm.png')
    print(f"OCR result for turn card (farm): {turn_card_text}")
    is_match, similarity = fuzzy_text_match(turn_card_text, "your turn")
    print(f"Similarity ratio with 'your turn': {similarity:.2f}")
    return is_match

def find_and_click_farming_object(screenshot_bgr, reference_path, threshold=0.7):
    """Find and click the farming object. If not found, check for 'Okay' button using template matching."""
    template = cv2.imread(reference_path, cv2.IMREAD_UNCHANGED)
    if template is None:
        print(f"Warning: Reference image not found at {reference_path}")
        print("Please ensure the reference image exists in the specified path.")
        return False
    result = cv2.matchTemplate(screenshot_bgr, template[:, :, :3], cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val < threshold:
        print(f"Farming object not found (max match: {max_val:.2f}). Skipping this cycle.")
        # Check for 'Okay' button using template matching
        screenshot_bgr2, _ = convert_screenshot_to_bgr()
        if find_and_click_template_on_screen(screenshot_bgr2, OKAY_TEMPLATE_PATH):
            print("'Okay' detected with template matching and clicked.")
        return False
    template_h, template_w = template.shape[:2]
    center_x = max_loc[0] + template_w // 2
    center_y = max_loc[1] + template_h // 2
    print(f"Farming object found at ({center_x}, {center_y}) with match {max_val:.2f}. Clicking...")
    pyautogui.moveTo(center_x, center_y, duration=0.3)
    pyautogui.mouseDown()
    pyautogui.mouseUp()
    pyautogui.click()
    return True

def collect_any_visible_drops(drop_paths, threshold=0.7):
    """Check for and collect any visible drops (potions, gold, etc.)."""
    screenshot_bgr, _ = convert_screenshot_to_bgr()
    for drop_path in drop_paths:
        find_and_click_template_on_screen(screenshot_bgr, drop_path, threshold)

# Check if required files exist
import os
if not os.path.exists(REFERENCE_OBJECT_PATH):
    print(f"Warning: Reference image not found at {REFERENCE_OBJECT_PATH}")
    print("Please ensure the reference image exists before starting.")
if not os.path.exists(BATTLE_ENGINE_SCRIPT):
    print(f"Warning: Battle engine script not found at {BATTLE_ENGINE_SCRIPT}")
    print("Please ensure battle_engine.py exists in the same directory.")

print("Starting autofarm...")
print(f"Target miscrit: {TARGET_MISCRIT_NAME}")
print(f"Platinum training: {PLATINUM_TRAINING}")
print(f"Farm cooldown: {FARM_COOLDOWN} seconds")
print(f"Battle check window: {BATTLE_CHECK_WINDOW} seconds")

last_farm_time = 0

while True:
    try:
        # Take a screenshot
        screenshot_bgr, screenshot = convert_screenshot_to_bgr()

        # Check if cooldown has passed
        time_since_last_farm = time.time() - last_farm_time
        if time_since_last_farm >= FARM_COOLDOWN:
            print("Farming...")
            farm_success = find_and_click_farming_object(screenshot_bgr, REFERENCE_OBJECT_PATH)
            if farm_success:
                last_farm_time = time.time()
                # After farming click, for the next BATTLE_CHECK_WINDOW seconds, check for battle
                print(f"Checking for battle for the next {BATTLE_CHECK_WINDOW} seconds...")
                battle_found = False
                for _ in range(BATTLE_CHECK_WINDOW):
                    _, screenshot = convert_screenshot_to_bgr()
                    if detect_battle_from_turn_indicator(screenshot):
                        print("Battle detected! Launching battle engine...")
                        try:
                            subprocess.run(['python', BATTLE_ENGINE_SCRIPT], check=True)
                            print("Battle finished. Resuming farming.")
                        except subprocess.CalledProcessError as e:
                            print(f"Battle engine failed with error: {e}")
                        except FileNotFoundError:
                            print(f"Battle engine script not found: {BATTLE_ENGINE_SCRIPT}")
                        battle_found = True
                        break
                    time.sleep(1)
                if not battle_found:
                    print("No battle detected. Checking for potion and gold drops...")
                    collect_any_visible_drops([POTION_DROP_PATH, GOLD_DROP_PATH])
            else:
                print("Retrying in 5 seconds...")
                time.sleep(5)
        else:
            wait_time = FARM_COOLDOWN - time_since_last_farm
            print(f"Waiting {wait_time:.1f} seconds for cooldown...")
            time.sleep(wait_time)
    except KeyboardInterrupt:
        print("\nFarming stopped by user.")
        break
    except Exception as e:
        print(f"Error in farming loop: {e}")
        print("Retrying in 5 seconds...")
        time.sleep(5) 