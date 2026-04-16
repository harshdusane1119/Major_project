from flask import Flask, request, jsonify, render_template
import uuid

app = Flask(__name__)

sessions = {}

# Serve frontend
@app.route('/')
def home():
    return render_template('index.html')


# Start session
@app.route('/start', methods=['GET'])
def start_session():
    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "eye": 0.0,
        "expression": 0.0,
        "gesture": 0.0,
        "frames": 0
    }

    return jsonify({"session_id": session_id})


# Receive live data
@app.route('/score', methods=['POST'])
def score():
    data = request.json
    session_id = data.get("session_id")

    if session_id not in sessions:
        return jsonify({"error": "Invalid session"}), 400

    s = sessions[session_id]

    s["eye"] += float(data.get("eye_contact", 0))
    s["expression"] += float(data.get("expression", 0))
    s["gesture"] += float(data.get("gesture", 0))
    s["frames"] += 1

    return jsonify({"status": "updated"})


# Final score
@app.route('/final', methods=['POST'])
def final_score():
    data = request.json
    session_id = data.get("session_id")

    if session_id not in sessions:
        return jsonify({"error": "Invalid session"}), 400

    s = sessions[session_id]

    if s["frames"] == 0:
        return jsonify({"final": 0})

    eye = (s["eye"] / s["frames"]) * 100
    exp = (s["expression"] / s["frames"]) * 100
    gest = (s["gesture"] / s["frames"]) * 100

    final = (eye * 0.4) + (exp * 0.3) + (gest * 0.3)

    return jsonify({
        "eye_score": round(eye, 2),
        "expression_score": round(exp, 2),
        "gesture_score": round(gest, 2),
        "final_score": round(final, 2)
    })


import os

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
