"""
toolbar.py

Renders and manages the on-screen toolbar UI for colour and tool selection.
Updated with a Neon Cyberpunk Aesthetic.
"""
import cv2
import numpy as np
import math

def draw_angled_rect(img, top_left, bottom_right, color, thickness=-1, cut=15):
    """Draw a cyberpunk-style rectangle with chamfered (cut) corners."""
    x1, y1 = top_left
    x2, y2 = bottom_right
    
    # Define 8 points for chamfered corners
    pts = np.array([
        [x1 + cut, y1],
        [x2 - cut, y1],
        [x2, y1 + cut],
        [x2, y2 - cut],
        [x2 - cut, y2],
        [x1 + cut, y2],
        [x1, y2 - cut],
        [x1, y1 + cut]
    ], np.int32)
    
    pts = pts.reshape((-1, 1, 2))
    
    if thickness < 0:
        cv2.fillPoly(img, [pts], color)
    else:
        cv2.polylines(img, [pts], True, color, thickness, cv2.LINE_AA)
    
    return img

class Toolbar:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Tools
        self.tools = ["SOLID", "AIRBRUSH", "MARKER", "BUCKET", "ERASER", "CLEAR"]
        self.active_tool = "SOLID"
        self.current_color = (0, 255, 204) # Default to Neon Cyan
        
        self.brush_size = 10
        self.brush_size_range = (1, 50)
        self.opacity = 0.5
        
        # Cyberpunk Color Wheel Layout
        self.wheel_radius = 55
        self.wheel_inner_radius = 25
        self.wheel_center = (width - 90, height - 90)
        
        # Precompute hollow color wheel image
        self.wheel_img = np.zeros((self.wheel_radius*2, self.wheel_radius*2, 3), dtype=np.uint8)
        for y in range(self.wheel_radius*2):
            for x in range(self.wheel_radius*2):
                dy = y - self.wheel_radius
                dx = x - self.wheel_radius
                dist = math.hypot(dx, dy)
                if self.wheel_inner_radius <= dist <= self.wheel_radius:
                    angle = math.atan2(dy, dx)
                    hue = (angle / (2 * math.pi) + 1.0) % 1.0 * 180
                    sat = 255
                    val = 255
                    self.wheel_img[y, x] = [hue, sat, val]
        self.wheel_img = cv2.cvtColor(self.wheel_img, cv2.COLOR_HSV2BGR)
        
        # Sliders
        self.slider_w = 150
        self.slider_h = 16
        self.s1_rect = (50, height - 120, self.slider_w, self.slider_h)
        self.s2_rect = (50, height - 70, self.slider_w, self.slider_h)
        
        # Buttons
        self.buttons = []
        x_offset = 240
        y_offset = height - 100
        btn_w = 85
        btn_h = 35
        gap = 15
        
        for t in self.tools:
            self.buttons.append({
                "name": t,
                "rect": (x_offset, y_offset, btn_w, btn_h)
            })
            x_offset += btn_w + gap

    def draw(self, frame):
        overlay = frame.copy()
        
        # Draw translucent background panel with angled edges
        px, py = 20, self.height - 150
        pw, ph = self.width - 20, self.height - 20
        draw_angled_rect(overlay, (px, py), (pw, ph), (10, 10, 15), -1, cut=30)
        
        # Cyberpunk blend (darker)
        cv2.addWeighted(overlay, 0.9, frame, 0.1, 0, frame)
        
        # Neon Border (Magenta)
        draw_angled_rect(frame, (px, py), (pw, ph), (255, 0, 255), 2, cut=30)
        
        # Draw Hollow Color Wheel
        wx, wy = self.wheel_center
        r = self.wheel_radius
        roi = frame[wy-r:wy+r, wx-r:wx+r]
        
        # Mask for the hollow wheel
        mask = np.zeros_like(self.wheel_img)
        cv2.circle(mask, (r, r), r, (255, 255, 255), -1)
        cv2.circle(mask, (r, r), self.wheel_inner_radius, (0, 0, 0), -1)
        np.copyto(roi, self.wheel_img, where=mask.astype(bool))
        
        # Sci-Fi Ticks
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            x1 = int(wx + (r+2) * math.cos(rad))
            y1 = int(wy + (r+2) * math.sin(rad))
            x2 = int(wx + (r+8) * math.cos(rad))
            y2 = int(wy + (r+8) * math.sin(rad))
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
            
        # Current color indicator in the center
        cv2.circle(frame, self.wheel_center, self.wheel_inner_radius - 5, self.current_color, -1)
        cv2.circle(frame, self.wheel_center, self.wheel_inner_radius - 5, (255, 255, 255), 2)
        
        # Brush Size Slider (Cyberpunk Style)
        sx, sy, sw, sh = self.s1_rect
        cv2.putText(frame, "BRUSH SIZE", (sx, sy - 8), cv2.FONT_HERSHEY_DUPLEX, 0.4, (255,255,255), 1)
        draw_angled_rect(frame, (sx, sy), (sx+sw, sy+sh), (30, 30, 30), -1, cut=5)
        fill_w = int((self.brush_size - self.brush_size_range[0]) / (self.brush_size_range[1] - self.brush_size_range[0]) * sw)
        if fill_w > 0:
            draw_angled_rect(frame, (sx, sy), (sx+fill_w, sy+sh), (255, 204, 0), -1, cut=5) # Neon Cyan
        draw_angled_rect(frame, (sx, sy), (sx+sw, sy+sh), (255, 204, 0), 1, cut=5)
        
        # Opacity Slider
        sx, sy, sw, sh = self.s2_rect
        cv2.putText(frame, "OPACITY", (sx, sy - 8), cv2.FONT_HERSHEY_DUPLEX, 0.4, (255,255,255), 1)
        draw_angled_rect(frame, (sx, sy), (sx+sw, sy+sh), (30, 30, 30), -1, cut=5)
        fill_w = int(self.opacity * sw)
        if fill_w > 0:
            draw_angled_rect(frame, (sx, sy), (sx+fill_w, sy+sh), (255, 204, 0), -1, cut=5)
        draw_angled_rect(frame, (sx, sy), (sx+sw, sy+sh), (255, 204, 0), 1, cut=5)
        
        # Draw Buttons
        for btn in self.buttons:
            bx, by, bw, bh = btn["rect"]
            is_active = (btn["name"] == self.active_tool)
            
            bg_color = (40, 40, 40)
            border_color = (150, 150, 150)
            
            if btn["name"] == "CLEAR":
                border_color = (0, 0, 255) # Red for danger
                
            if is_active:
                bg_color = (80, 80, 80)
                border_color = (255, 204, 0) # Neon Cyan
                # Glow Box
                draw_angled_rect(frame, (bx-3, by-3), (bx+bw+3, by+bh+3), border_color, 1, cut=8)
            
            draw_angled_rect(frame, (bx, by), (bx+bw, by+bh), bg_color, -1, cut=8)
            draw_angled_rect(frame, (bx, by), (bx+bw, by+bh), border_color, 2, cut=8)
            
            text_size = cv2.getTextSize(btn["name"], cv2.FONT_HERSHEY_DUPLEX, 0.4, 1)[0]
            tx = bx + (bw - text_size[0]) // 2
            ty = by + (bh + text_size[1]) // 2
            text_col = (255, 255, 255) if not is_active else (255, 204, 0)
            cv2.putText(frame, btn["name"], (tx, ty), cv2.FONT_HERSHEY_DUPLEX, 0.4, text_col, 1)
            
        return frame

    def check_interaction(self, x, y, is_pinch):
        if not is_pinch:
            return None
            
        # Hollow wheel check
        wx, wy = self.wheel_center
        dist = math.hypot(x - wx, y - wy)
        if self.wheel_inner_radius <= dist <= self.wheel_radius:
            color = self.wheel_img[y - wy + self.wheel_radius, x - wx + self.wheel_radius]
            self.current_color = (int(color[0]), int(color[1]), int(color[2]))
            return "COLOR", self.current_color
            
        # Sliders
        sx, sy, sw, sh = self.s1_rect
        if sx <= x <= sx + sw and sy <= y <= sy + sh:
            ratio = (x - sx) / sw
            self.brush_size = int(self.brush_size_range[0] + ratio * (self.brush_size_range[1] - self.brush_size_range[0]))
            return "BRUSH_SIZE", self.brush_size
            
        sx, sy, sw, sh = self.s2_rect
        if sx <= x <= sx + sw and sy <= y <= sy + sh:
            self.opacity = (x - sx) / sw
            return "OPACITY", self.opacity
            
        # Buttons
        for btn in self.buttons:
            bx, by, bw, bh = btn["rect"]
            if bx <= x <= bx + bw and by <= y <= by + bh:
                if btn["name"] != "CLEAR":
                    self.active_tool = btn["name"]
                return btn["name"], None
                
        return None
