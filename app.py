from flask import Flask, request, jsonify, send_from_directory
import os
import requests
import uuid
from dotenv import load_dotenv

# ---------------- LOAD API KEY ----------------
load_dotenv()
RUNWARE_API_KEY = os.getenv("RUNWARE_API_KEY")

# ---------------- FLASK APP ----------------
app = Flask(__name__, static_folder="static")

# ---------------- IMAGE GENERATION ----------------
@app.route("/generate-image", methods=["POST"])
def generate_image():
    body = request.get_json()
    prompt = body.get("prompt", "")

    url = "https://api.runware.ai/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {RUNWARE_API_KEY}",
        "Content-Type": "application/json"
    }

    data = [{
        "taskType": "imageInference",
        "taskUUID": str(uuid.uuid4()),
        "positivePrompt": prompt,
        "model": "runware:101@1",
        "height": 512,
        "width": 512,
        "numberResults": 1
    }]

    r = requests.post(url, headers=headers, json=data)
    return jsonify(r.json()), r.status_code

# ---------------- VIDEO GENERATION ----------------
@app.route("/generate-video", methods=["POST"])
def generate_video():
    body = request.get_json()
    prompt = body.get("prompt", "")

    url = "https://api.runware.ai/v1/videos/generations"
    headers = {
        "Authorization": f"Bearer {RUNWARE_API_KEY}",
        "Content-Type": "application/json"
    }

    task_uuid = str(uuid.uuid4())

    data = [{
        "taskType": "videoInference",
        "taskUUID": task_uuid,
        "positivePrompt": prompt,
        "model": "klingai:5@3",
        "duration": 10,
        "width": 1920,
        "height": 1080,
        "numberResults": 1,
        "outputType": "URL",
        "outputFormat": "MP4",
        "outputQuality": 90
    }]

    # 🛠 Print exactly what you are sending
    import json
    # print("Sending payload to Runware:")
    # print(json.dumps(data, indent=2))

    r = requests.post(url, headers=headers, json=data)

    try:
        response = r.json()
    except ValueError:
        return jsonify({"error": "Non-JSON response from Runware", "raw": r.text}), r.status_code

    return jsonify(response), r.status_code



# ---------------- VIDEO STATUS CHECK ----------------
@app.route("/check-video/<taskUUID>", methods=["GET"])
def check_video(taskUUID):
    url = f"https://api.runware.ai/v1/tasks/{taskUUID}"
    headers = {
        "Authorization": f"Bearer {RUNWARE_API_KEY}",
        "Content-Type": "application/json"
    }

    r = requests.get(url, headers=headers)
    try:
        data = r.json()
    except ValueError:
        # Runware didn’t send JSON
        return jsonify({"error": "Non-JSON response from Runware", "raw": r.text}), r.status_code

    return jsonify(data), r.status_code


# ---------------- FRONTEND ----------------
@app.route("/")
def home():
    return send_from_directory("static", "index.html")

# ---------------- START SERVER ----------------
if __name__ == "__main__":
    app.run(debug=True)
