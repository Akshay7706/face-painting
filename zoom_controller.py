"""
zoom_controller.py

Handles zoom and pan controls for the drawing canvas using
two-hand gestures.
"""
import cv2
import numpy as np

class ZoomController:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.zoom_factor = 1.0
        self.pan_x = 0
        self.pan_y = 0
        
        self.base_zoom_dist = None
        
    def update(self, two_hand_zoom_dist):
        if two_hand_zoom_dist is not None:
            if self.base_zoom_dist is None:
                self.base_zoom_dist = two_hand_zoom_dist
            else:
                scale = two_hand_zoom_dist / self.base_zoom_dist
                self.zoom_factor = max(0.5, min(3.0, self.zoom_factor * scale))
                self.base_zoom_dist = two_hand_zoom_dist
        else:
            self.base_zoom_dist = None

    def apply_transform(self, canvas):
        M = np.float32([
            [self.zoom_factor, 0, self.pan_x],
            [0, self.zoom_factor, self.pan_y]
        ])
        transformed = cv2.warpAffine(canvas, M, (self.width, self.height))
        return transformed
