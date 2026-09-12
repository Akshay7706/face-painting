"""
drawing_canvas.py

Manages the drawing surface where user strokes are rendered.
Supports various brush types and fill operations.
"""
import numpy as np
import cv2
import random

class DrawingCanvas:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Main persistent canvas (BGR)
        self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        # Temporary layer for translucent strokes (like marker)
        self.temp_layer = np.zeros_like(self.canvas)
        
        self.current_color = (0, 0, 255)
        self.brush_size = 10
        self.active_tool = "SOLID"
        self.prev_point = None

    def clear(self):
        self.canvas.fill(0)
        self.temp_layer.fill(0)
        self.prev_point = None

    def set_color(self, color):
        self.current_color = color
        
    def set_brush_size(self, size):
        self.brush_size = max(1, size)
        
    def set_tool(self, tool_name):
        self.active_tool = tool_name

    def fill(self, x, y):
        """
        Paint bucket tool using floodFill.
        """
        # OpenCV floodFill requires a mask that is 2 pixels larger than the image
        mask = np.zeros((self.height + 2, self.width + 2), np.uint8)
        # Using a tolerance to allow smooth edges to fill slightly
        diff = (5, 5, 5)
        # Apply flood fill on the main canvas
        cv2.floodFill(self.canvas, mask, (x, y), self.current_color, diff, diff, cv2.FLOODFILL_FIXED_RANGE)

    def draw(self, x, y):
        current_point = (x, y)
        if self.prev_point is None:
            self.prev_point = current_point
            
        color = self.current_color
        thickness = self.brush_size
        
        if self.active_tool == "SOLID":
            cv2.line(self.canvas, self.prev_point, current_point, color, thickness, cv2.LINE_AA)
            
        elif self.active_tool == "ERASER":
            cv2.line(self.canvas, self.prev_point, current_point, (0,0,0), thickness * 3, cv2.LINE_AA)
            
        elif self.active_tool == "AIRBRUSH":
            # Draw random dots within the radius
            num_points = thickness * 3
            radius = thickness
            for _ in range(num_points):
                angle = random.uniform(0, 2 * np.pi)
                r = random.uniform(0, radius)
                px = int(x + r * np.cos(angle))
                py = int(y + r * np.sin(angle))
                if 0 <= px < self.width and 0 <= py < self.height:
                    # Draw small dots
                    cv2.circle(self.canvas, (px, py), 1, color, -1)
                    
        elif self.active_tool == "MARKER":
            # Draw on temp layer, which will be alpha blended
            cv2.line(self.temp_layer, self.prev_point, current_point, color, thickness, cv2.LINE_AA)
            
        self.prev_point = current_point

    def stop_drawing(self):
        self.prev_point = None
        # Commit temp_layer to canvas for Marker
        if np.any(self.temp_layer):
            mask = cv2.cvtColor(self.temp_layer, cv2.COLOR_BGR2GRAY)
            _, mask_bin = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)
            
            # Blend only where temp layer has color (alpha = 0.5)
            roi = cv2.bitwise_and(self.canvas, self.canvas, mask=mask_bin)
            blended = cv2.addWeighted(roi, 0.5, self.temp_layer, 0.5, 0)
            
            mask_inv = cv2.bitwise_not(mask_bin)
            bg = cv2.bitwise_and(self.canvas, self.canvas, mask=mask_inv)
            
            self.canvas = cv2.add(bg, blended)
            self.temp_layer.fill(0)

    def get_canvas(self):
        if np.any(self.temp_layer):
            # Combine for real-time preview of marker
            mask = cv2.cvtColor(self.temp_layer, cv2.COLOR_BGR2GRAY)
            _, mask_bin = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)
            roi = cv2.bitwise_and(self.canvas, self.canvas, mask=mask_bin)
            blended = cv2.addWeighted(roi, 0.5, self.temp_layer, 0.5, 0)
            mask_inv = cv2.bitwise_not(mask_bin)
            bg = cv2.bitwise_and(self.canvas, self.canvas, mask=mask_inv)
            return cv2.add(bg, blended)
        return self.canvas
