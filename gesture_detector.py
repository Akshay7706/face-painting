"""
gesture_detector.py

Interprets hand landmarks (from HandTracker) into recognized gestures
such as pointing, pinching, fist, and open palm.
"""
import math

class GestureDetector:
    def __init__(self):
        pass

    def get_distance(self, p1, p2):
        return math.hypot(p1.x - p2.x, p1.y - p2.y)

    def detect_gestures(self, detection_result):
        """
        Returns a list of dictionaries with gesture info for each detected hand.
        """
        gestures = []
        if not detection_result or not detection_result.hand_landmarks:
            return gestures

        for idx, landmarks in enumerate(detection_result.hand_landmarks):
            handedness = detection_result.handedness[idx][0].category_name
            
            # Key landmarks
            wrist = landmarks[0]
            thumb_tip = landmarks[4]
            thumb_ip = landmarks[3]
            index_tip = landmarks[8]
            index_pip = landmarks[6]
            middle_tip = landmarks[12]
            middle_pip = landmarks[10]
            ring_tip = landmarks[16]
            ring_pip = landmarks[14]
            pinky_tip = landmarks[20]
            pinky_pip = landmarks[18]
            
            def is_extended(tip, pip):
                return self.get_distance(wrist, tip) > self.get_distance(wrist, pip)
                
            index_ext = is_extended(index_tip, index_pip)
            middle_ext = is_extended(middle_tip, middle_pip)
            ring_ext = is_extended(ring_tip, ring_pip)
            pinky_ext = is_extended(pinky_tip, pinky_pip)
            
            pinky_base = landmarks[17]
            thumb_ext = self.get_distance(thumb_tip, pinky_base) > self.get_distance(thumb_ip, pinky_base)
            
            pinch_dist = self.get_distance(thumb_tip, index_tip)
            is_pinch = pinch_dist < 0.05
            
            gesture = "UNKNOWN"
            if is_pinch:
                gesture = "PINCH"
            elif index_ext and not middle_ext and not ring_ext and not pinky_ext:
                gesture = "POINTING"
            elif index_ext and middle_ext and ring_ext and pinky_ext and thumb_ext:
                gesture = "OPEN_PALM"
            elif not index_ext and not middle_ext and not ring_ext and not pinky_ext and not thumb_ext:
                gesture = "FIST"
                
            gestures.append({
                "handedness": handedness,
                "gesture": gesture,
                "landmarks": landmarks,
                "index_tip": index_tip,
                "thumb_tip": thumb_tip,
                "pinch_dist": pinch_dist
            })
            
        return gestures
        
    def detect_two_hand_zoom(self, gestures):
        if len(gestures) >= 2:
            h1 = gestures[0]
            h2 = gestures[1]
            if h1["gesture"] == "PINCH" and h2["gesture"] == "PINCH":
                return self.get_distance(h1["index_tip"], h2["index_tip"])
        return None
