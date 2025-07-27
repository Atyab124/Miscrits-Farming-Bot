import cv2
import numpy as np
import pyautogui
import pytesseract
import time
import re
import os
from utils import extract_text_from_screen_region, find_and_click_template_on_screen, find_template_on_screen, convert_screenshot_to_bgr, fuzzy_text_match

# Import PLATINUM_TRAINING from autofarm.py
#try:
#    from autofarm import PLATINUM_TRAINING
#except ImportError:
#    PLATINUM_TRAINING = False  # Default value if import fails
# PLATINUM_TRAINING is now loaded from config file

# =====================
# Helper Functions
# =====================
def read_config_from_file():
    """Read both target miscrit name and platinum training from config file (set by autofarm.py)."""
    try:
        with open('config_file.txt', 'r') as f:
            content = f.read().strip()
            if '|' in content:
                target_name, platinum_training_str = content.split('|', 1)
                platinum_training = platinum_training_str.lower() == 'true'
                return target_name, platinum_training
            else:
                # Legacy format - just target name
                return content, False  # Default to False for platinum training
    except FileNotFoundError:
        return 'None', True  # Default fallback
    except Exception as e:
        print(f"Error reading config: {e}")
        return 'None', True  # Default fallback

def read_target_miscrit_from_config():
    """Read the target miscrit name from config file (set by autofarm.py)."""
    target_name, _ = read_config_from_file()
    return target_name

def load_target_encounter_counter():
    """Load the persistent encounter counter from file."""
    try:
        with open('target_encounters.txt', 'r') as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return 0

def save_target_encounter_counter(counter):
    """Save the encounter counter to file."""
    with open('target_encounters.txt', 'w') as f:
        f.write(str(counter))

def check_and_update_target_miscrit(new_target_name):
    """Check if the target miscrit name has changed and update the config file if so."""
    try:
        with open('config_file.txt', 'r') as f:
            old_target = f.read().strip()
        if old_target != new_target_name:
            with open('config_file.txt', 'w') as f:
                f.write(new_target_name)
            return True
        return False
    except FileNotFoundError:
        with open('config_file.txt', 'w') as f:
            f.write(new_target_name)
        return False

def execute_battle_move(move_index, attack_coords):
    """Execute a battle move by clicking the corresponding attack button."""
    if 0 <= move_index < len(attack_coords):
        x, y = attack_coords[move_index]
        print(f"Clicking move {move_index+1} at ({x}, {y})")
        pyautogui.moveTo(x, y, duration=0.2)
        pyautogui.click()
    else:
        print(f"Invalid move index: {move_index}")

def end_battle_and_handle_training():
    """End the battle by clicking Continue button and handle training sequence if needed."""
    continue_button_path = 'reference_images/Continue.png'
    time.sleep(1)
    screenshot = pyautogui.screenshot()
    screenshot_np = np.array(screenshot)
    screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    template = cv2.imread(continue_button_path, cv2.IMREAD_UNCHANGED)
    if template is None:
        print(f"Reference image not found at {continue_button_path}")
        return
    result = cv2.matchTemplate(screenshot_bgr, template[:, :, :3], cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val >= 0.7:
        # Before clicking, check for 'ready to train' using pytesseract
        rtt_x, rtt_y, rtt_w, rtt_h = 472, 490, 78, 9
        ready_text, ready_area = extract_text_from_screen_region(screenshot, rtt_x, rtt_y, rtt_w, rtt_h)
        ready_area.save('screenshots/ready_to_train_area.png')
        is_match, similarity = fuzzy_text_match(ready_text, 'ready to train')
        print(f"OCR result for ready to train area: {ready_text}")
        print(f"Similarity ratio with 'ready to train': {similarity:.2f}")
        if is_match:
            # 1. Click continue as usual, wait 2 seconds
            template_h, template_w = template.shape[:2]
            center_x = max_loc[0] + template_w // 2
            center_y = max_loc[1] + template_h // 2
            print(f"Continue button found at ({center_x}, {center_y}). Clicking once...")
            pyautogui.moveTo(center_x, center_y, duration=0.2)
            pyautogui.click()
            time.sleep(2)
            # 2. Check for 'okay' in okay area, click if found
            okay_x, okay_y, okay_w, okay_h = 545, 622, 50, 20
            okay_screenshot = pyautogui.screenshot()
            okay_text, okay_area = extract_text_from_screen_region(okay_screenshot, okay_x, okay_y, okay_w, okay_h)
            okay_area.save('screenshots/okay_area_after_train.png')
            is_okay_match, okay_similarity = fuzzy_text_match(okay_text, 'okay')
            print(f"OCR result for okay area after train: {okay_text}")
            print(f"Similarity ratio with 'okay': {okay_similarity:.2f}")
            if is_okay_match:
                center_x = okay_x + okay_w // 2
                center_y = okay_y + okay_h // 2
                print(f"'Okay' detected after train. Clicking at ({center_x}, {center_y})")
                pyautogui.moveTo(center_x, center_y, duration=0.3)
                pyautogui.click()
            # 3. Click train icon
            pyautogui.moveTo(515, 60, duration=0.2)
            pyautogui.click()
            time.sleep(1)
            # 4. Click second miscrit
            pyautogui.moveTo(376, 414, duration=0.2)
            pyautogui.click()
            time.sleep(1)
            # 5. Click train now
            pyautogui.moveTo(600, 347, duration=0.2)
            pyautogui.click()
            time.sleep(5)
            if platinum_training_enabled:
                pyautogui.moveTo(530, 786, duration=0.2)
                pyautogui.click()
                time.sleep(3)
                #Click continue
                pyautogui.moveTo(579, 784, duration=0.2)
                pyautogui.click()
                time.sleep(1)
            else:
                # 6. Click continue
                pyautogui.moveTo(681, 781, duration=0.2)
                pyautogui.click()
                time.sleep(1)
            # 7.1. Check for and click continue button using OCR with hardcoded coordinates
            continue_x, continue_y, continue_w, continue_h = 638, 660, 71, 20  # Adjust these coordinates as needed
            continue_screenshot = pyautogui.screenshot()
            continue_text, continue_area = extract_text_from_screen_region(continue_screenshot, continue_x, continue_y, continue_w, continue_h)
            continue_area.save('screenshots/continue_button_area.png')
            is_continue_match, continue_similarity = fuzzy_text_match(continue_text, 'continue')
            print(f"OCR result for continue button area: {continue_text}")
            print(f"Similarity ratio with 'continue': {continue_similarity:.2f}")
            if is_continue_match:
                center_x = continue_x + continue_w // 2
                center_y = continue_y + continue_h // 2
                print(f"'Continue' detected during training sequence. Clicking at ({center_x}, {center_y})")
                pyautogui.moveTo(center_x, center_y, duration=0.2)
                pyautogui.click()
                time.sleep(1)
            # 7.2. Check for 'okay' using template matching
            screenshot_bgr2, _ = convert_screenshot_to_bgr()
            if find_and_click_template_on_screen(screenshot_bgr2, 'reference_images/Okay.png'):
                print("'Okay' detected with template matching and clicked.")
                time.sleep(1)
            # 8. Click click cross
            pyautogui.moveTo(850, 325, duration=0.2)
            pyautogui.click()
            time.sleep(0.5)
            # 9. Check for 'okay' in the specified region
            okay2_x, okay2_y, okay2_w, okay2_h = 550, 742, 47, 16
            okay2_screenshot = pyautogui.screenshot()
            okay2_text, okay2_area = extract_text_from_screen_region(okay2_screenshot, okay2_x, okay2_y, okay2_w, okay2_h)
            okay2_area.save('screenshots/okay2_area.png')
            is_okay2_match, okay2_similarity = fuzzy_text_match(okay2_text, 'okay')
            print(f"OCR result for okay2 area: {okay2_text}")
            print(f"Similarity ratio with 'okay': {okay2_similarity:.2f}")
            if is_okay2_match:
                center_x = okay2_x + okay2_w // 2
                center_y = okay2_y + okay2_h // 2
                print(f"'Okay' detected in second area. Clicking at ({center_x}, {center_y})")
                pyautogui.moveTo(center_x, center_y, duration=0.3)
                pyautogui.click()
            print("Training sequence complete. Returning to farming loop.")
            return
        # If not ready to train, just click continue as usual
        template_h, template_w = template.shape[:2]
        center_x = max_loc[0] + template_w // 2
        center_y = max_loc[1] + template_h // 2
        print(f"Continue button found at ({center_x}, {center_y}). Clicking once...")
        pyautogui.moveTo(center_x, center_y, duration=0.2)
        pyautogui.click()
        time.sleep(3)

        #Check for okay button
        okay2_x, okay2_y, okay2_w, okay2_h = 550, 742, 47, 16
        okay2_screenshot = pyautogui.screenshot()
        okay2_text, okay2_area = extract_text_from_screen_region(okay2_screenshot, okay2_x, okay2_y, okay2_w, okay2_h)
        okay2_area.save('screenshots/okay2_area.png')
        is_okay2_match, okay2_similarity = fuzzy_text_match(okay2_text, 'okay')
        print(f"OCR result for okay2 area: {okay2_text}")
        print(f"Similarity ratio with 'okay': {okay2_similarity:.2f}")
        if is_okay2_match:
            center_x = okay2_x + okay2_w // 2
            center_y = okay2_y + okay2_h // 2
            print(f"'Okay' detected in second area. Clicking at ({center_x}, {center_y})")
            pyautogui.moveTo(center_x, center_y, duration=0.3)
            pyautogui.click()
    else:
        print("Continue button not found.")



# =====================
# MAIN BATTLE LOGIC
# =====================

# User-configurable coordinates (could be loaded from config if desired)
capture_perc_x, capture_perc_y, capture_perc_w, capture_perc_h = 556, 135, 40, 18
enemy_name_x, enemy_name_y, enemy_name_w, enemy_name_h = 774, 50, 100, 15
attack_coords = [
    (330, 1025),  # First attack
    (500, 1025),  # Second attack
    (670, 1025),  # Third attack
    (840, 1025),  # Fourth attack
]
turn_card_x, turn_card_y, turn_card_w, turn_card_h = 522, 965, 180, 25
target_miscrit_name, platinum_training_enabled = read_config_from_file()
target_miscrit_encounters = load_target_encounter_counter()

print(f"Loaded configuration - Target: {target_miscrit_name}, Platinum Training: {platinum_training_enabled}")
print(f"Configuration loaded successfully from config_file.txt")

# --- ENEMY NAME DETECTION (ONCE PER BATTLE) ---
screenshot = pyautogui.screenshot()
enemy_name, enemy_name_area = extract_text_from_screen_region(screenshot, enemy_name_x, enemy_name_y, enemy_name_w, enemy_name_h)
enemy_name_area.save('screenshots/enemy_name_area.png')
print(f"Enemy miscrit name detected: {enemy_name}")
is_match, similarity = fuzzy_text_match(enemy_name, target_miscrit_name.lower())
print(f"Similarity ratio with target: {similarity:.2f}")
is_target_miscrit = is_match
if is_target_miscrit:
    target_miscrit_encounters += 1
    save_target_encounter_counter(target_miscrit_encounters)
    print(f"Target miscrit encounters: {target_miscrit_encounters}")

# --- MAIN BATTLE LOOP ---
turn_card_reference_path = "reference_images/It's your turn!.png"
turn_card_reference_saved = True

while True:
    screenshot_bgr, screenshot = convert_screenshot_to_bgr()

    # If we haven't saved the turn card reference yet, use OCR to detect and save it
    if not turn_card_reference_saved:
        turn_card_text, turn_card_area = extract_text_from_screen_region(screenshot, turn_card_x, turn_card_y, turn_card_w, turn_card_h)
        is_match, similarity = fuzzy_text_match(turn_card_text, 'your turn')
        print(f"OCR result for turn card (battle): {turn_card_text}")
        print(f"Similarity ratio with 'your turn': {similarity:.2f}")
        if is_match:
            turn_card_area.save(turn_card_reference_path)
            print(f"Saved turn card reference image to {turn_card_reference_path}")
            turn_card_reference_saved = True
        else:
            print("Not in battle or not your turn. Retrying in 0.2s...")
            time.sleep(0.2)
            continue

    # 1. Use template matching for fast turn detection
    turn_template = cv2.imread(turn_card_reference_path, cv2.IMREAD_UNCHANGED)
    result = cv2.matchTemplate(screenshot_bgr, turn_template[:, :, :3], cv2.TM_CCOEFF_NORMED)
    _, turn_max_val, _, turn_max_loc = cv2.minMaxLoc(result)
    is_your_turn = turn_max_val > 0.7

    # 2. Check for Continue button
    continue_button_path = 'reference_images/Continue.png'
    continue_template = cv2.imread(continue_button_path, cv2.IMREAD_UNCHANGED)
    result = cv2.matchTemplate(screenshot_bgr, continue_template[:, :, :3], cv2.TM_CCOEFF_NORMED)
    _, cont_max_val, _, cont_max_loc = cv2.minMaxLoc(result)
    is_continue = cont_max_val > 0.7

    # 3. OCR capture percentage using pytesseract on the predetermined area
    capture_text, capture_area = extract_text_from_screen_region(screenshot, capture_perc_x, capture_perc_y, capture_perc_w, capture_perc_h)
    capture_area.save('screenshots/capture_percentage_area.png')
    print(f"Raw OCR result for capture chance: {capture_text}")
    match = re.search(r'\d+', capture_text)
    if match:
        capture_percent = int(match.group())
    else:
        capture_percent = 0
    print(f"Capture chance detected: {capture_percent}%")

    # 4. If enemy is target and capture chance > 85, click capture
    if is_target_miscrit and capture_percent > 85:
        print("Target miscrit found and capture chance is high! Clicking capture button...")
        cap_loc, cap_shape = find_template_on_screen(screenshot_bgr, 'reference_images/Capture button.png')
        if cap_loc:
            cap_x = cap_loc[0] + cap_shape[1] // 2
            cap_y = cap_loc[1] + cap_shape[0] // 2
            pyautogui.moveTo(cap_x, cap_y, duration=0.2)
            pyautogui.click()
            time.sleep(2)
            continue
        else:
            print("Capture button not found!")

    if is_your_turn:
        print("It's your turn! Clicking first move (hardcoded)...")
        execute_battle_move(0, attack_coords)
        time.sleep(2)
    elif is_continue:
        print("Continue button detected. Clicking to end battle...")
        end_battle_and_handle_training()
        break
    else:
        time.sleep(0.05)
        continue

end_battle_and_handle_training() 