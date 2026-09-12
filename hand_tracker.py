"""
hand_tracker.py

Wraps MediaPipe's Hands solution to provide hand landmark detection
and tracking from webcam frames.
"""
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import cv2

class HandTracker:
    def __init__(self, model_path='hand_landmarker.task', num_hands=2):
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=num_hands,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5)
        
        self.landmarker = vision.HandLandmarker.create_from_options(options)
        
        self.connections = [
            (0,1), (1,2), (2,3), (3,4),       # Thumb
            (0,5), (5,6), (6,7), (7,8),       # Index
            (5,9), (9,10), (10,11), (11,12),  # Middle
            (9,13), (13,14), (14,15), (15,16),# Ring
            (13,17), (17,18), (18,19), (19,20),# Pinky
            (0,17)                            # Palm base
        ]
        
    def process_frame(self, frame, timestamp_ms):
        """
        Process a BGR frame and return the HandLandmarkerResult.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = self.landmarker.detect_for_video(mp_image, int(timestamp_ms))
        return result

    def draw_landmarks(self, frame, detection_result):
        """
        Draws hand landmarks on the BGR frame in-place.
        """
        if not detection_result or not detection_result.hand_landmarks:
            return frame
            
        annotated_image = frame
        h, w, _ = annotated_image.shape
        hand_landmarks_list = detection_result.hand_landmarks
        
        for idx in range(len(hand_landmarks_list)):
            hand_landmarks = hand_landmarks_list[idx]
            
            # Draw connections
            for connection in self.connections:
                start_idx = connection[0]
                end_idx = connection[1]
                
                start_point = (int(hand_landmarks[start_idx].x * w), int(hand_landmarks[start_idx].y * h))
                end_point = (int(hand_landmarks[end_idx].x * w), int(hand_landmarks[end_idx].y * h))
                
                cv2.line(annotated_image, start_point, end_point, (0, 255, 0), 2)
            
            # Draw landmarks
            for landmark in hand_landmarks:
                px = int(landmark.x * w)
                py = int(landmark.y * h)
                cv2.circle(annotated_image, (px, py), 4, (0, 0, 255), -1)
                
        return annotated_image
