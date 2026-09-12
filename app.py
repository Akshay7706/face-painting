from flask import Flask, render_template, Response, jsonify
import cv2
import time
import numpy as np

from hand_tracker import HandTracker
from gesture_detector import GestureDetector
from drawing_canvas import DrawingCanvas
from toolbar import Toolbar
from zoom_controller import ZoomController

app = Flask(__name__)

# Global Application State
cam_index = 0
cap = None
tracker = None
detector = None
canvas = None
toolbar = None
zoom = None
show_camera = True
width = 640
height = 480

# State variables for HTML HUD
global_gesture = "NONE"
global_tool = "SOLID"
global_size = 10
global_color = [0, 0, 255]
last_timestamp_ms = 0

def init_app_state():
    global cap, tracker, detector, canvas, toolbar, zoom, width, height, last_timestamp_ms
    
    if cap is not None:
        cap.release()
        
    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        print(f"Error: Could not open webcam {cam_index}.")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    tracker = HandTracker()
    detector = GestureDetector()
    canvas = DrawingCanvas(width, height)
    toolbar = Toolbar(width, height)
    zoom = ZoomController(width, height)
    last_timestamp_ms = int(time.time() * 1000)

def gen_frames():
    global cap, tracker, detector, canvas, toolbar, zoom, show_camera, cam_index
    global global_gesture, global_tool, global_size, global_color, last_timestamp_ms
    
    was_pinched = False
    
    while True:
        if cap is None or not cap.isOpened():
            time.sleep(0.5)
            continue
            
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.flip(frame, 1)
        
        # Ensure strictly monotonic timestamps for MediaPipe
        current_time_ms = int(time.time() * 1000)
        if current_time_ms <= last_timestamp_ms:
            current_time_ms = last_timestamp_ms + 1
        last_timestamp_ms = current_time_ms
            
        detection_result = tracker.process_frame(frame, current_time_ms)
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
                    pass 
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
        
        # Update global state for HTML HUD
        global_gesture = active_gesture_text
        global_tool = toolbar.active_tool
        global_size = toolbar.brush_size
        global_color = list(toolbar.current_color)
            
        annotated_frame = tracker.draw_landmarks(frame, detection_result)
        transformed_canvas = zoom.apply_transform(canvas.get_canvas())
        
        canvas_gray = cv2.cvtColor(transformed_canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(canvas_gray, 1, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        
        bg_opacity = toolbar.opacity if show_camera else 0.0
        black_bg = np.zeros_like(frame) 
        cam_bg = cv2.addWeighted(annotated_frame, bg_opacity, black_bg, 1.0 - bg_opacity, 0)
        
        bg = cv2.bitwise_and(cam_bg, cam_bg, mask=mask_inv)
        final_frame = cv2.add(bg, transformed_canvas)
            
        final_frame = toolbar.draw(final_frame)
        
        # NOTE: Removed draw_hud! The HUD is now rendered cleanly in HTML via /state
        
        if px is not None and py is not None:
            cv2.circle(final_frame, (px, py), toolbar.brush_size + 4, (255, 255, 255), 2)
            if is_pinching:
                cv2.circle(final_frame, (px, py), 6, (0, 255, 0), -1)
            elif active_gesture_text == "POINTING":
                cv2.circle(final_frame, (px, py), 6, toolbar.current_color, -1)
            else:
                cv2.circle(final_frame, (px, py), 3, (200, 200, 200), -1)
        
        ret, buffer = cv2.imencode('.jpg', final_frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/state')
def get_state():
    return jsonify({
        "gesture": global_gesture,
        "tool": global_tool,
        "size": global_size,
        "color": global_color,
        "show_camera": show_camera,
        "cam_index": cam_index
    })

@app.route('/clear_canvas', methods=['POST'])
def clear_canvas():
    global canvas
    if canvas:
        canvas.clear()
    return jsonify({"status": "success"})

@app.route('/toggle_camera', methods=['POST'])
def toggle_camera():
    global show_camera
    show_camera = not show_camera
    return jsonify({"status": "success", "show_camera": show_camera})

@app.route('/switch_camera', methods=['POST'])
def switch_camera():
    global cam_index, cap
    cam_index = (cam_index + 1) % 4
    init_app_state()
    return jsonify({"status": "success", "cam_index": cam_index})

if __name__ == '__main__':
    init_app_state()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
