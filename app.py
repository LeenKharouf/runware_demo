from flask import Flask, request, jsonify, send_from_directory
import os
import requests
from dotenv import load_dotenv

# Step 1: Load my secret API key from a .env file
# (This way I don’t hardcode it in my code — safer + cleaner)
load_dotenv()
RUNWARE_API_KEY = os.getenv("RUNWARE_API_KEY")

# Step 2: Spin up a tiny Flask server to handle requests
app = Flask(__name__)

# ---------------- IMAGE GENERATION ----------------
@app.route("/generate-image", methods=["POST"])
def generate_image():
    # Grab the user’s prompt from the request body
    body = request.get_json()
    prompt = body.get("prompt", "")

    # Runware’s image generation endpoint
    url = "https://api.runware.ai/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {RUNWARE_API_KEY}",  # my key = my “ticket” to Runware
        "Content-Type": "application/json"
    }

    # What Runware expects → an array with task details
    data = [{
        "taskType": "imageInference",
        "positivePrompt": prompt,   # user’s words go here
        "model": "runware:101@1",   # a base model ID from docs
        "height": 512,
        "width": 512,
        "numberResults": 1
    }]

    # Send request to Runware
    r = requests.post(url, headers=headers, json=data)

    # Error handling — make messages human-friendly
    if r.status_code != 200:
        try:
            error_data = r.json()
            if error_data.get("errors") and error_data["errors"][0].get("code") == "invalidApiKey":
                return jsonify({"error": "Your API key is invalid. Please check it."}), 401
            else:
                return jsonify({"error": error_data}), r.status_code
        except:
            return jsonify({"error": r.text}), r.status_code

    # If success → return the JSON response from Runware
    return jsonify(r.json())


# ---------------- VIDEO GENERATION ----------------
@app.route("/generate-video", methods=["POST"])
def generate_video():
    # Same idea as images, but video-specific fields
    body = request.get_json()
    prompt = body.get("prompt", "")

    url = "https://api.runware.ai/v1/videos/generations"
    headers = {
        "Authorization": f"Bearer {RUNWARE_API_KEY}",
        "Content-Type": "application/json"
    }

    data = [{
        "taskType": "videoInference",
        "positivePrompt": prompt,
        "model": "runware:201@1",   # base video model ID
        "height": 512,
        "width": 512,
        "duration": 5,              # 5-second clip
        "numberResults": 1
    }]

    r = requests.post(url, headers=headers, json=data)

    # Same style of error handling as images
    if r.status_code != 200:
        try:
            error_data = r.json()
            if error_data.get("errors") and error_data["errors"][0].get("code") == "invalidApiKey":
                return jsonify({"error": "Your API key is invalid. Please check it."}), 401
            else:
                return jsonify({"error": error_data}), r.status_code
        except:
            return jsonify({"error": r.text}), r.status_code

    return jsonify(r.json())


# ---------------- FRONTEND ----------------
@app.route("/")
def home():
    # Serve up my static HTML/JS/CSS
    return send_from_directory("static", "index.html")


# ---------------- EXTRA MODE: INPAINTING ----------------
@app.route("/inpaint-image", methods=["POST"])
def inpaint_image():
    """
    Example of Runware’s inpainting feature.
    Normally: you upload a base image + a mask, then provide a new prompt.
    For demo: I’ve hardcoded fake IDs for seed + mask images.
    """

    body = request.get_json()
    prompt = body.get("prompt", "")

    url = "https://api.runware.ai/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {RUNWARE_API_KEY}",
        "Content-Type": "application/json"
    }

    data = [{
        "taskType": "imageInference",
        "positivePrompt": prompt,
        "seedImage": "c64351d5-4c59-42f7-95e1-eace013eddab",  # placeholder
        "maskImage": "d7e8f9a0-2b5c-4e7f-a1d3-9c8b7a6e5d4f",   # placeholder
        "model": "civitai:139562@297320",
        "height": 512,
        "width": 512,
        "strength": 0.8,
        "numberResults": 1
    }]

    r = requests.post(url, headers=headers, json=data)

    if r.status_code != 200:
        try:
            error_data = r.json()
            if error_data.get("errors") and error_data["errors"][0].get("code") == "invalidApiKey":
                return jsonify({"error": "Your API key is invalid. Please check it."}), 401
            else:
                return jsonify({"error": error_data}), r.status_code
        except:
            return jsonify({"error": r.text}), r.status_code

    return jsonify(r.json())


# ---------------- START SERVER ----------------
if __name__ == "__main__":
    # Run the server locally so I can open http://127.0.0.1:5000
    app.run(debug=True)
