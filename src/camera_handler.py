# src/camera_handler.py - Face mesh landmark extraction
import cv2

# MediaPipe Face Mesh landmark indices for facial features

LEFT_EYE_INDICES = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
RIGHT_EYE_INDICES = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
MOUTH_INNER_INDICES = [13, 14, 78, 308, 81, 311, 178, 402]
POSE_INDICES = [4]  # Nose tip for head direction

ALL_REQUIRED_INDICES = sorted(list(set(LEFT_EYE_INDICES + RIGHT_EYE_INDICES + MOUTH_INNER_INDICES + POSE_INDICES)))


def get_clean_landmarks(single_face):
    """
    Extract clean landmark data from MediaPipe Face Mesh output.

    Args:
        single_face: Raw face landmarks from detector

    Returns:
        List of dicts with landmark id and (x, y) coordinates
    """
    clean_list = []
    for idx in ALL_REQUIRED_INDICES:
        if idx < len(single_face):
            lm = single_face[idx]
            clean_list.append({
                "id": idx,
                "x": lm[0],
                "y": lm[1]
            })
    return clean_list
