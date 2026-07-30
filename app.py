import cv2
import numpy as np
from flask import Flask, render_template, jsonify, Response
import time
import threading

# MediaPipe Solutions Direct Sub-module Imports
import mediapipe as mp
try:
    from mediapipe.python.solutions import face_mesh as mp_face_mesh
except ImportError:
    import mediapipe.solutions.face_mesh as mp_face_mesh

app = Flask(__name__)

# MediaPipe Face Mesh Setup
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]

def calculate_ear(landmarks, eye_indices, img_w, img_h):
    """Eye Aspect Ratio (EAR) calculate karta hai."""
    pts = np.array([(landmarks[idx].x * img_w, landmarks[idx].y * img_h) for idx in eye_indices])
    v1 = np.linalg.norm(pts[1] - pts[5])
    v2 = np.linalg.norm(pts[2] - pts[4])
    h = np.linalg.norm(pts[0] - pts[3])
    if h == 0:
        return 0.0
    return (v1 + v2) / (2.0 * h)

current_telemetry = {
    "state": "RELAXED",
    "metrics": {"ear": 0.30, "estimated_hr": 72, "hrv": 60.0},
    "config": {
        "title": "🧘 RELAXED & CALM STATE",
        "bg_gradient": "linear-gradient(135deg, #092013 0%, #174226 100%)",
        "card_border": "#00e676",
        "light_color": "🟢 Soft Emerald Green",
        "light_hex": "#00e676",
        "soundscape": "🌧️ Ambient Forest Rain",
        "hvac": "❄️ 23.5°C (Comfort)",
        "advice": "✨ Normal gaze detected. Maintaining calm ambient space."
    }
}

CONFIGS = {
    "HIGH_STRESS": {
        "title": "🚨 HIGH STRESS DETECTED",
        "bg_gradient": "linear-gradient(135deg, #2b0808 0%, #4a1212 100%)",
        "card_border": "#ff4d4d",
        "light_color": "🟠 Warm Amber Lights",
        "light_hex": "#FF7A00",
        "soundscape": "🌊 432Hz Calm Waves & Pink Noise",
        "hvac": "❄️ 22.0°C (Active Cooling)",
        "advice": "💡 Facial strain detected. Lowering brightness to soothe mind."
    },
    "DEEP_FOCUS": {
        "title": "🎯 DEEP WORK / FOCUSED",
        "bg_gradient": "linear-gradient(135deg, #051b2c 0%, #0d3b66 100%)",
        "card_border": "#00d2ff",
        "light_color": "🔵 Cool Blue Circadian Light",
        "light_hex": "#00d2ff",
        "soundscape": "🎧 40Hz Gamma Binaural Beats",
        "hvac": "🌡️ 21.0°C (Optimal Concentration)",
        "advice": "⚡ High focus state detected. Optimizing environment for productivity."
    },
    "FATIGUE_DROWSY": {
        "title": "😴 MENTAL FATIGUE / DROWSY",
        "bg_gradient": "linear-gradient(135deg, #1f1a00 0%, #3d3300 100%)",
        "card_border": "#ffcc00",
        "light_color": "☀️ Bright Dynamic Daylight",
        "light_hex": "#ffcc00",
        "soundscape": "🎵 Upbeat Acoustic Beats",
        "hvac": "💨 20.0°C (Refreshing Cold Breeze)",
        "advice": "⚠️ Eye fatigue detected. Boosting brightness & airflow to increase alertness."
    },
    "RELAXED": {
        "title": "🧘 RELAXED & CALM STATE",
        "bg_gradient": "linear-gradient(135deg, #092013 0%, #174226 100%)",
        "card_border": "#00e676",
        "light_color": "🟢 Soft Emerald Green",
        "light_hex": "#00e676",
        "soundscape": "🌧️ Ambient Forest Rain",
        "hvac": "❄️ 23.5°C (Comfort)",
        "advice": "✨ Normal gaze detected. Maintaining calm ambient space."
    }
}

global_cap = None

def analyze_webcam_frame():
    global global_cap
    global_cap = cv2.VideoCapture(0)
    closed_eye_frames = 0

    while True:
        if global_cap is None or not global_cap.isOpened():
            time.sleep(0.1)
            continue

        ret, frame = global_cap.read()
        if not ret:
            time.sleep(0.05)
            continue

        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            left_ear = calculate_ear(landmarks, LEFT_EYE, w, h)
            right_ear = calculate_ear(landmarks, RIGHT_EYE, w, h)
            avg_ear = round(float((left_ear + right_ear) / 2.0), 2)

            if avg_ear < 0.20:
                closed_eye_frames += 1
                state = "FATIGUE_DROWSY" if closed_eye_frames > 2 else "HIGH_STRESS"
            else:
                closed_eye_frames = 0
                state = "DEEP_FOCUS" if 0.20 <= avg_ear <= 0.26 else "RELAXED"

            est_hr = 85 if state == "HIGH_STRESS" else (68 if state == "RELAXED" else (78 if state == "FATIGUE_DROWSY" else 72))
            est_hrv = 30.0 if state == "HIGH_STRESS" else (62.0 if state == "RELAXED" else (42.0 if state == "FATIGUE_DROWSY" else 50.0))

            current_telemetry["state"] = state
            current_telemetry["metrics"] = {"ear": avg_ear, "estimated_hr": est_hr, "hrv": est_hrv}
            current_telemetry["config"] = CONFIGS[state]

        time.sleep(0.05)

def gen_frames():
    while True:
        if global_cap is not None and global_cap.isOpened():
            ret, frame = global_cap.read()
            if ret:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.04)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/biometrics')
def get_biometrics():
    return jsonify(current_telemetry)

if __name__ == '__main__':
    t = threading.Thread(target=analyze_webcam_frame)
    t.daemon = True
    t.start()
    app.run(debug=False, port=5000)
