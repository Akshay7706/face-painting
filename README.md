# Neon Canvas 🤖🎨

A highly advanced, futuristic Hand Gesture Drawing Application. Draw directly onto a web-based digital canvas using nothing but your hand movements and computer webcam!

Powered by **Python**, **OpenCV**, **MediaPipe**, and **Flask**, this application features a stunning **Neon Cyberpunk** web interface with an interactive holographic OpenCV menu.

## Features ✨
- **Hand Gesture Tracking**: Uses Google MediaPipe to track 21 3D hand landmarks in real-time.
- **Pinch to Draw**: Simply pinch your index finger and thumb to start drawing!
- **Holographic Menu**: An in-canvas interactive OpenCV menu that you can control entirely with your hands.
- **Advanced Tools**:
  - `SOLID` Brush
  - `AIRBRUSH` Particle Spray
  - `MARKER` Translucent Highlighter
  - `BUCKET` Smart Flood Fill
- **Cyberpunk Web UI**: A beautiful HTML/CSS frontend with dynamic gradients, glowing neon CSS borders, and a real-time data-bound HTML HUD.
- **Two-Handed Zoom**: Use both hands simultaneously to intuitively pan and zoom around your canvas like a touch screen!

## Installation 🚀

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/neon-canvas.git
   cd neon-canvas
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python app.py
   ```

4. **Access the Interface**:
   Open your browser and navigate to `http://localhost:5000`

## Gestures Guide 🖐️
- **Hover**: Keep your hand open to move the cursor around the screen.
- **Select / Draw**: Pinch your index finger to your thumb to click buttons on the holographic menu, select colors, or draw on the canvas.
- **Pan / Zoom**: Bring both hands into the frame. Pinch with both hands and move them apart to zoom in, or together to zoom out. Move both hands simultaneously to pan across the canvas!

## Note on Hosting ☁️
This application uses OpenCV (`cv2.VideoCapture`) to access the local physical webcam on the machine it is running on. Therefore, it is designed to be run **locally**. Hosting this directly on a cloud provider (like Heroku or Render) will not work because the cloud server does not have access to your local webcam.
