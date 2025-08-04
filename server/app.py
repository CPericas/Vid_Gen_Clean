from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from TTS.api import TTS
from werkzeug.utils import secure_filename
import os
import logging
import traceback

# === Init Flask App and CORS ===
app = Flask(__name__)
CORS(app)

# === Configure logging ===
logging.basicConfig(
    filename='app_errors.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s: %(message)s'
)

# === Output folders ===
OUTPUT_FOLDER = os.path.join(os.getcwd(), "output")
AVATAR_FOLDER = os.path.join(OUTPUT_FOLDER, "avatars")
SADTALKER_RESULTS = os.path.join(os.getcwd(), "adTalker", "results")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(AVATAR_FOLDER, exist_ok=True)
os.makedirs(SADTALKER_RESULTS, exist_ok=True)

# === Initialize Coqui TTS ===
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)

@app.route("/upload-avatar", methods=["POST"])
def upload_avatar():
    if "avatar" not in request.files:
        logging.error("Upload avatar failed: No file part in request")
        return jsonify({"success": False, "error": "No file provided"}), 400
    
    file = request.files["avatar"]
    if file.filename == "":
        logging.error("Upload avatar failed: Empty filename")
        return jsonify({"success": False, "error": "Empty filename"}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(AVATAR_FOLDER, filename)
    try:
        file.save(filepath)
        return jsonify({
            "success": True,
            "path": f"/avatars/{filename}"
        })
    except Exception as e:
        logging.error(f"Error saving avatar: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"success": False, "error": "Failed to save avatar"}), 500

@app.route("/avatars/<filename>")
def serve_avatar(filename):
    return send_from_directory(AVATAR_FOLDER, filename)

# === Coqui TTS Endpoint ===
@app.route("/generate-audio", methods=["POST"])
def generate_audio():
    data = request.get_json()
    text = data.get("text", "")

    if not text.strip():
        logging.error("No text provided for TTS")
        return jsonify({"success": False, "error": "No text provided"}), 400

    output_file = os.path.join(OUTPUT_FOLDER, "output.wav")

    try:
        tts.tts_to_file(text=text, file_path=output_file)
        return jsonify({"success": True, "url": "/audio/output.wav"})
    except Exception as e:
        logging.error(f"TTS generation error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"success": False, "error": "Text-to-speech generation failed"}), 500

@app.route("/audio/<filename>")
def serve_audio(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

# === SadTalker Setup ===
from src.gradio_demo import SadTalker
sadtalker = SadTalker(checkpoint_path="checkpoints", config_path="src/config", lazy_load=True)

# === SadTalker Video Generation Endpoint ===
@app.route("/generate-video", methods=["POST"])
def generate_video():
    data = request.get_json()

    avatar_path = data.get("avatar")
    audio_path = os.path.join(OUTPUT_FOLDER, "output.wav")

    if not avatar_path or not os.path.isfile(audio_path):
        logging.error("Missing avatar or audio file for video generation")
        return jsonify({"success": False, "error": "Missing avatar or audio"}), 400

    try:
        sadtalker.test(
            source_image=avatar_path,
            driven_audio=audio_path,
            preprocess='full',
            still=True,
            enhancer=False,
            batch_size=2,
            size=256,
            pose_style=0
        )

        video_path = os.path.join(SADTALKER_RESULTS, "output.mp4")
        if not os.path.exists(video_path):
            logging.error("SadTalker did not produce output video")
            return jsonify({"success": False, "error": "Video not generated"}), 500

        return jsonify({"success": True, "url": "/video/output.mp4"})
    except Exception as e:
        logging.error(f"SadTalker video generation error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"success": False, "error": "Video generation failed"}), 500

@app.route("/video/<filename>")
def serve_video(filename):
    return send_from_directory(SADTALKER_RESULTS, filename)

# === Run Flask Server ===
if __name__ == "__main__":
    app.run(port=5001, debug=True)
