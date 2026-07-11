# src/ai_logic.py - Biometric calculations for driver monitoring
import math

def calculate_dist(p1, p2):
    """Calculate Euclidean distance between two points"""
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def calculate_ear(payload):
    """
    Calculate Eye Aspect Ratio (EAR) for drowsiness detection.

    EAR formula: (vertical distances) / (horizontal distance)
    Lower values indicate closed eyes.

    Args:
        payload: Clean landmark data from camera_handler

    Returns:
        Average EAR of both eyes, or None if landmarks missing
    """
    lm_dict = {pt['id']: (pt['x'], pt['y']) for pt in payload}

    required_left = [362, 385, 386, 263, 374, 380]
    required_right = [33, 160, 159, 133, 145, 153]

    if not all(idx in lm_dict for idx in required_left + required_right):
        return None

    # Left eye EAR
    v1_left = calculate_dist(lm_dict[385], lm_dict[380])
    v2_left = calculate_dist(lm_dict[386], lm_dict[374])
    h_left = calculate_dist(lm_dict[362], lm_dict[263])
    ear_left = (v1_left + v2_left) / (2.0 * h_left)

    # Right eye EAR
    v1_right = calculate_dist(lm_dict[160], lm_dict[145])
    v2_right = calculate_dist(lm_dict[159], lm_dict[153])
    h_right = calculate_dist(lm_dict[33], lm_dict[133])
    ear_right = (v1_right + v2_right) / (2.0 * h_right)

    return (ear_left + ear_right) / 2.0

def calculate_mar(payload):
    """
    Calculate Mouth Aspect Ratio (MAR) for yawn detection.

    MAR formula: (vertical distances) / (horizontal distance)
    Higher values indicate open mouth (yawning).

    Args:
        payload: Clean landmark data from camera_handler

    Returns:
        MAR value
    """
    lm_dict = {pt['id']: (pt['x'], pt['y']) for pt in payload}

    required_mouth = [13, 14, 78, 308, 81, 311, 178, 402]

    if not all(idx in lm_dict for idx in required_mouth):
        return 0.0

    # Vertical distances
    v1_mouth = calculate_dist(lm_dict[81], lm_dict[178])
    v2_mouth = calculate_dist(lm_dict[13], lm_dict[14])
    v3_mouth = calculate_dist(lm_dict[311], lm_dict[402])
    # Horizontal distance
    h_mouth = calculate_dist(lm_dict[78], lm_dict[308])

    if h_mouth == 0:
        return 0.0
    return (v1_mouth + v2_mouth + v3_mouth) / (3.0 * h_mouth)

def check_distraction(payload):
    """
    Estimate head pose direction using geometric distance ratios.

    Returns:
        "LEFT" - Head turned left
        "RIGHT" - Head turned right
        "DOWN" - Head tilted down
        "STRAIGHT" - Looking forward
    """
    lm_dict = {pt['id']: (pt['x'], pt['y']) for pt in payload}

    if not all(idx in lm_dict for idx in [4, 33, 263]):
        return "STRAIGHT"

    p_nose = lm_dict[4]
    p_right_eye = lm_dict[33]
    p_left_eye = lm_dict[263]

    # Yaw detection (left/right turn)
    dist_nose_left = calculate_dist(p_nose, p_left_eye)
    dist_nose_right = calculate_dist(p_nose, p_right_eye)

    if dist_nose_right == 0:
        return "STRAIGHT"
    ratio_yaw = dist_nose_left / dist_nose_right

    if ratio_yaw < 0.42:
        return "LEFT"
    if ratio_yaw > 2.35:
        return "RIGHT"

    # Pitch detection (head down)
    mid_eyes_y = (p_right_eye[1] + p_left_eye[1]) / 2
    nose_drop = p_nose[1] - mid_eyes_y

    if nose_drop > 55:
        return "DOWN"

    return "STRAIGHT"
