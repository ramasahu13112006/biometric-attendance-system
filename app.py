import base64
import cv2
import numpy as np
from flask import Flask, render_template_string, request, jsonify

# MediaPipe Face Mesh Import
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

@app.route('/')
def index():
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    return render_template_string(html_content)

@app.route('/process_frame', methods=['POST'])
def process_frame():
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'success': False, 'message': 'No image data'})

        image_data = data['image'].split(',')[1]
        decoded_data = base64.b64decode(image_data)
        np_arr = np.frombuffer(decoded_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({'success': False, 'message': 'Invalid image frame'})

        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            left_ear = calculate_ear(landmarks, LEFT_EYE, w, h)
            right_ear = calculate_ear(landmarks, RIGHT_EYE, w, h)
            avg_ear = round(float((left_ear + right_ear) / 2.0), 2)

            if avg_ear < 0.20:
                state = "FATIGUE_DROWSY"
            else:
                state = "DEEP_FOCUS" if 0.20 <= avg_ear <= 0.26 else "RELAXED"

            est_hr = 85 if state == "HIGH_STRESS" else (68 if state == "RELAXED" else (78 if state == "FATIGUE_DROWSY" else 72))
            est_hrv = 30.0 if state == "HIGH_STRESS" else (62.0 if state == "RELAXED" else (42.0 if state == "FATIGUE_DROWSY" else 50.0))

            return jsonify({
                "success": True,
                "state": state,
                "metrics": {"ear": avg_ear, "estimated_hr": est_hr, "hrv": est_hrv},
                "config": CONFIGS[state]
            })

        return jsonify({
            "success": True,
            "state": "NO_FACE",
            "metrics": {"ear": 0.0, "estimated_hr": 0, "hrv": 0.0},
            "config": {
                "title": "🔍 NO FACE DETECTED",
                "bg_gradient": "linear-gradient(135deg, #111 0%, #222 100%)",
                "card_border": "#666",
                "light_color": "⚪ Searching...",
                "light_hex": "#ffffff",
                "soundscape": "🔇 None",
                "hvac": "❄️ Auto Mode",
                "advice": "Please align your face in front of the camera."
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Vercel handler
app = app

            
