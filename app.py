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

@app.route('/')
def index():
    with open('index.html', 'r', encoding='utf-8') as f:
        return render_template_string(f.read())

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
