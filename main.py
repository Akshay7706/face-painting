"""
main.py

Entry point for the Hand Gesture Colouring application.
Supports Borderless Transparent Desktop Overlay mode.
"""
import cv2
import time
import numpy as np
import ctypes

from hand_tracker import HandTracker
from gesture_detector import GestureDetector
from drawing_canvas import DrawingCanvas
from toolbar import Toolbar, draw_rounded_rect
from zoom_controller import ZoomController

def draw_hud(frame, gesture, active_tool, cam_index):
    overlay = frame.copy()
    draw_rounded_rect(overlay, (20, 20), (340, 110), (25, 25, 30), -1, radius=15)
    cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
    
    draw_rounded_rect(frame, (20, 20), (340, 110), (100, 100, 100), 2, radius=15)
    
    cv2.putText(frame, "Liquid Glass Canvas", (40, 45), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 200, 0), 1)
    
    gesture_color = (0, 255, 0) if gesture != "UNKNOWN" and gesture != "NONE" else (150, 150, 150)
    cv2.putText(frame, f"Mode: {active_tool} | {gesture}", (40, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, gesture_color, 2)
    cv2.putText(frame, f"Cam: {cam_index} | [n] Switch [t] Toggle BG [q] Quit", (40, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)
    
    return frame

def setup_transparent_window(window_name):
    # Find the window by name
    hwnd = ctypes.windll.user32.FindWindowW(None, window_name)
    if hwnd:
        # Remove borders (WS_POPUP)
        GWL_STYLE = -16
        WS_POPUP = 0x80000000
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, WS_POPUP)
        
        # Enable transparency
        GWL_EXSTYLE = -20
        WS_EX_LAYERED = 0x00080000
        styles = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, styles | WS_EX_LAYERED)
        
        # Set black (0,0,0) to be completely transparent
        LWA_COLORKEY = 1
        ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 0, LWA_COLORKEY)

def main():
    cam_index = 0
    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    window_name = "Hand Gesture Colouring"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    # Initialize the window immediately so we can apply transparency
    cv2.imshow(window_name, np.zeros((height, width, 3), dtype=np.uint8))
    cv2.waitKey(100)
    setup_transparent_window(window_name)
    
    tracker = HandTracker()
    detector = GestureDetector()
    canvas = DrawingCanvas(width, height)
    toolbar = Toolbar(width, height)
    zoom = ZoomController(width, height)
    
    show_camera = False # Hide camera by default so the screen is transparent!
    start_time = time.time()
    
    was_pinched = False
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.flip(frame, 1)
        
        timestamp_ms = int((time.time() - start_time) * 1000)
        if timestamp_ms == 0: timestamp_ms = 1
            
        detection_result = tracker.process_frame(frame, timestamp_ms)
        gestures = detector.detect_gestures(detection_result)
        two_hand_zoom_dist = detector.detect_two_hand_zoom(gestures)
        zoom.update(two_hand_zoom_dist)
        
        active_gesture_text = "NONE"
        px, py = None, None
        
        is_pinching = False
        
        if len(gestures) > 0:
            primary_hand = gestures[0]
            active_gesture_text = primary_hand["gesture"]
            index_tip = primary_hand["index_tip"]
            px = int(index_tip.x * width)
            py = int(index_tip.y * height)
            
            is_pinching = (active_gesture_text == "PINCH")
            
            action = toolbar.check_interaction(px, py, is_pinching)
            if action:
                action_type, action_value = action
                if action_type == "COLOR" and is_pinching:
                    canvas.set_color(action_value)
                elif action_type == "BRUSH_SIZE":
                    canvas.set_brush_size(action_value)
                elif action_type == "OPACITY":
                    pass # Handled below
                elif is_pinching:
                    canvas.set_tool(action_type)
                    if action_type == "CLEAR":
                        canvas.clear()
            else:
                if toolbar.active_tool == "BUCKET":
                    if is_pinching and not was_pinched:
                        canvas.fill(px, py)
                else:
                    if active_gesture_text == "POINTING":
                        canvas.draw(px, py)
                    else:
                        canvas.stop_drawing()
        else:
            canvas.stop_drawing()
            
        was_pinched = is_pinching
            
        annotated_frame = tracker.draw_landmarks(frame, detection_result)
        transformed_canvas = zoom.apply_transform(canvas.get_canvas())
        
        canvas_gray = cv2.cvtColor(transformed_canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(canvas_gray, 1, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        
        # Transparent overlay logic
        bg_opacity = toolbar.opacity if show_camera else 0.0
        black_bg = np.zeros_like(frame) # Solid black will be rendered transparent by the OS
        cam_bg = cv2.addWeighted(annotated_frame, bg_opacity, black_bg, 1.0 - bg_opacity, 0)
        
        bg = cv2.bitwise_and(cam_bg, cam_bg, mask=mask_inv)
        final_frame = cv2.add(bg, transformed_canvas)
            
        final_frame = toolbar.draw(final_frame)
        final_frame = draw_hud(final_frame, active_gesture_text, toolbar.active_tool, cam_index)
        
        if px is not None and py is not None:
            cv2.circle(final_frame, (px, py), toolbar.brush_size + 4, (255, 255, 255), 2)
            if is_pinching:
                cv2.circle(final_frame, (px, py), 6, (0, 255, 0), -1)
            elif active_gesture_text == "POINTING":
                cv2.circle(final_frame, (px, py), 6, toolbar.current_color, -1)
            else:
                cv2.circle(final_frame, (px, py), 3, (200, 200, 200), -1)
        
        cv2.imshow(window_name, final_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            canvas.clear()
        elif key == ord('t'):
            show_camera = not show_camera
        elif key == ord('n'):
            cap.release()
            cam_index = (cam_index + 1) % 4
            cap = cv2.VideoCapture(cam_index)
            if not cap.isOpened():
                cam_index = 0
                cap = cv2.VideoCapture(cam_index)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
