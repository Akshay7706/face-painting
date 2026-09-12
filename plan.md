# Development Plan — Hand Gesture Colouring

## Phase 0: Project Setup (current)
- [x] Create folder/file structure
- [x] Create virtual environment
- [x] Add dependencies to requirements.txt
- [x] Write initial README.md
- [x] Verify project structure

## Phase 1: Hand Tracking Foundation
- [ ] Capture webcam feed with OpenCV in `main.py`
- [ ] Implement `HandTracker` in `hand_tracker.py` using MediaPipe Hands
- [ ] Draw hand landmarks on the video feed for visual verification

## Phase 2: Gesture Detection
- [ ] Implement `GestureDetector` in `gesture_detector.py`
- [ ] Detect basic gestures: pointing (index finger up), pinch (thumb + index), fist, open palm
- [ ] Map gestures to intended actions (draw, select, erase, clear)

## Phase 3: Drawing Canvas
- [ ] Implement `DrawingCanvas` in `drawing_canvas.py`
- [ ] Support freehand drawing driven by fingertip position
- [ ] Support colour changes and brush size
- [ ] Support clearing the canvas

## Phase 4: Toolbar UI
- [ ] Implement `Toolbar` in `toolbar.py`
- [ ] On-screen colour palette and tool buttons
- [ ] Gesture-based selection of toolbar items (e.g. hover + pinch)

## Phase 5: Zoom & Pan Controls
- [ ] Implement `ZoomController` in `zoom_controller.py`
- [ ] Two-hand pinch/spread gesture to zoom canvas
- [ ] Pan gesture support

## Phase 6: Integration & Polish
- [ ] Wire all modules together in `main.py`
- [ ] Add on-screen instructions/help overlay
- [ ] Handle edge cases (no hand detected, multiple hands, low light)
- [ ] Performance tuning (frame rate, detection confidence thresholds)

## Phase 7: Extras (stretch goals)
- [ ] Save/export drawings as image files
- [ ] Undo/redo support
- [ ] Multiple brush shapes/textures
- [ ] Gesture customization/config file

---
**Note:** Do not proceed to the next phase until the current phase is reviewed and confirmed complete.
