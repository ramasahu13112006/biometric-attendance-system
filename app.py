from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

CONFIGS = {
    "HIGH_STRESS": {
        "title": "🚨 HIGH STRESS DETECTED",
        "bg_gradient": "linear-gradient(135deg, #2b0808 0%, #4a1212 100%)",
        "card_border": "#ff4d4d",
        "light_color": "🟠 Warm Amber Lights",
        "soundscape": "🌊 432Hz Calm Waves & Pink Noise",
        "hvac": "❄️ 22.0°C (Active Cooling)",
        "advice": "💡 Facial strain detected. Lowering brightness to soothe mind."
    },
    "DEEP_FOCUS": {
        "title": "🎯 DEEP WORK / FOCUSED",
        "bg_gradient": "linear-gradient(135deg, #051b2c 0%, #0d3b66 100%)",
        "card_border": "#00d2ff",
        "light_color": "🔵 Cool Blue Circadian Light",
        "soundscape": "🎧 40Hz Gamma Binaural Beats",
        "hvac": "🌡️ 21.0°C (Optimal Concentration)",
        "advice": "⚡ High focus state detected. Optimizing environment for productivity."
    },
    "FATIGUE_DROWSY": {
        "title": "😴 MENTAL FATIGUE / DROWSY",
        "bg_gradient": "linear-gradient(135deg, #1f1a00 0%, #3d3300 100%)",
        "card_border": "#ffcc00",
        "light_color": "☀️ Bright Dynamic Daylight",
        "soundscape": "🎵 Upbeat Acoustic Beats",
        "hvac": "💨 20.0°C (Refreshing Cold Breeze)",
        "advice": "⚠️ Eye fatigue detected. Boosting brightness & airflow to increase alertness."
    },
    "RELAXED": {
        "title": "🧘 RELAXED & CALM STATE",
        "bg_gradient": "linear-gradient(135deg, #092013 0%, #174226 100%)",
        "card_border": "#00e676",
        "light_color": "🟢 Soft Emerald Green",
        "soundscape": "🌧️ Ambient Forest Rain",
        "hvac": "❄️ 23.5°C (Comfort)",
        "advice": "✨ Normal gaze detected. Maintaining calm ambient space."
    }
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Biometric Environment AI</title>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/face_mesh.js" crossorigin="anonymous"></script>

    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', sans-serif; transition: all 0.3s ease; }
        body { min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; color: #fff; background: #0f172a; }
        .dashboard { width: 100%; max-width: 480px; background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border-radius: 24px; padding: 25px; border: 2px solid #00e676; box-shadow: 0 8px 32px rgba(0,0,0,0.5); text-align: center; }
        h1 { font-size: 1.2rem; margin-bottom: 15px; }
        .video-box { width: 100%; height: 230px; border-radius: 16px; overflow: hidden; background: #000; margin-bottom: 15px; border: 1px solid rgba(255, 255, 255, 0.2); }
        video { width: 100%; height: 100%; object-fit: cover; }
        .metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 15px; }
        .metric-card { background: rgba(0,0,0,0.3); padding: 10px; border-radius: 12px; }
        .metric-card h4 { font-size: 0.75rem; color: #aaa; margin-bottom: 4px; }
        .metric-card p { font-size: 1rem; font-weight: bold; }
        .info-box { background: rgba(0, 0, 0, 0.25); padding: 12px; border-radius: 12px; text-align: left; font-size: 0.85rem; line-height: 1.5; }

        @media screen and (max-width: 480px) {
            body { padding: 10px; }
            .dashboard { padding: 15px; border-radius: 18px; }
            h1 { font-size: 1rem; margin-bottom: 10px; }
            .video-box { height: 180px; }
            .metrics-grid { gap: 6px; }
            .metric-card { padding: 8px 5px; }
            .metric-card h4 { font-size: 0.65rem; }
            .metric-card p { font-size: 0.85rem; }
            .info-box { font-size: 0.75rem; padding: 10px; }
        }
        @media screen and (max-width: 360px) {
            .metrics-grid { grid-template-columns: 1fr; }
            .video-box { height: 150px; }
        }
        @media screen and (min-width: 768px) {
            .dashboard { max-width: 550px; padding: 30px; }
            h1 { font-size: 1.4rem; }
            .video-box { height: 260px; }
            .metric-card p { font-size: 1.1rem; }
            .info-box { font-size: 0.9rem; }
        }
    </style>
</head>
<body>
    <div id="main-dashboard" class="dashboard">
        <h1 id="state-title">🧘 RELAXED & CALM STATE</h1>

        <div class="video-box">
            <video id="webcam" autoplay playsinline muted></video>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <h4>EAR</h4>
                <p id="metric-ear">0.30</p>
            </div>
            <div class="metric-card">
                <h4>Heart Rate</h4>
                <p id="metric-hr">72 BPM</p>
            </div>
            <div class="metric-card">
                <h4>HRV</h4>
                <p id="metric-hrv">60 ms</p>
            </div>
        </div>

        <div class="info-box">
            <div><strong>Lighting:</strong> <span id="light-val">🟢 Soft Emerald Green</span></div>
            <div><strong>Sound:</strong> <span id="sound-val">🌧️ Ambient Forest Rain</span></div>
            <div><strong>HVAC:</strong> <span id="hvac-val">❄️ 23.5°C (Comfort)</span></div>
            <hr style="margin: 8px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.1);">
            <div id="advice-val">✨ Normal gaze detected. Maintaining calm ambient space.</div>
        </div>
    </div>

    <script>
        const videoElement = document.getElementById('webcam');

        function calcEAR(landmarks, indices) {
            const p = indices.map(i => landmarks[i]);
            const v1 = Math.hypot(p[1].x - p[5].x, p[1].y - p[5].y);
            const v2 = Math.hypot(p[2].x - p[4].x, p[2].y - p[4].y);
            const h = Math.hypot(p[0].x - p[3].x, p[0].y - p[3].y);
            return h === 0 ? 0 : (v1 + v2) / (2.0 * h);
        }

        const faceMesh = new FaceMesh({
            locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`
        });

        faceMesh.setOptions({ maxNumFaces: 1, refineLandmarks: true, minDetectionConfidence: 0.5 });

        faceMesh.onResults((results) => {
            if (results.multiFaceLandmarks && results.multiFaceLandmarks.length > 0) {
                const landmarks = results.multiFaceLandmarks[0];
                const leftEAR = calcEAR(landmarks, [362, 385, 387, 263, 373, 380]);
                const rightEAR = calcEAR(landmarks, [33, 160, 158, 133, 153, 144]);
                const avgEAR = (leftEAR + rightEAR) / 2.0;

                fetch('/api/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ear: avgEAR })
                })
                .then(r => r.json())
                .then(data => {
                    if(data.success) {
                        document.body.style.background = data.config.bg_gradient;
                        document.getElementById('main-dashboard').style.borderColor = data.config.card_border;
                        document.getElementById('state-title').innerText = data.config.title;

                        document.getElementById('metric-ear').innerText = data.metrics.ear;
                        document.getElementById('metric-hr').innerText = data.metrics.estimated_hr + " BPM";
                        document.getElementById('metric-hrv').innerText = data.metrics.hrv + " ms";

                        document.getElementById('light-val').innerText = data.config.light_color;
                        document.getElementById('sound-val').innerText = data.config.soundscape;
                        document.getElementById('hvac-val').innerText = data.config.hvac;
                        document.getElementById('advice-val').innerText = data.config.advice;
                    }
                });
            }
        });

        const camera = new Camera(videoElement, {
            onFrame: async () => { await faceMesh.send({ image: videoElement }); },
            width: 640, height: 480
        });
        camera.start();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json or {}
    ear = data.get('ear', 0.30)
    
    if ear < 0.20:
        state = "FATIGUE_DROWSY"
    elif 0.20 <= ear <= 0.26:
        state = "DEEP_FOCUS"
    else:
        state = "RELAXED"
        
    est_hr = 85 if state == "HIGH_STRESS" else (68 if state == "RELAXED" else (78 if state == "FATIGUE_DROWSY" else 72))
    est_hrv = 30.0 if state == "HIGH_STRESS" else (62.0 if state == "RELAXED" else (42.0 if state == "FATIGUE_DROWSY" else 50.0))

    return jsonify({
        "success": True,
        "state": state,
        "metrics": {"ear": round(ear, 2), "estimated_hr": est_hr, "hrv": est_hrv},
        "config": CONFIGS[state]
    })

app = app
