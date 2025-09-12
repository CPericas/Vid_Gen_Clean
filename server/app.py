from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from rembg import remove
from PIL import Image
import os, sys, logging, traceback, shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SADTALKER_DIR = os.path.join(BASE_DIR, "SadTalker", "src")
# === Setup Python paths ===
sys.path.append(SADTALKER_DIR)
sys.path.append(os.path.join(SADTALKER_DIR, "utils"))

from utils.init_path import init_path

# Load SadTalker paths once
sadtalker_paths = init_path()

print("[DEBUG] Checking checkpoints folder at:", sadtalker_paths["checkpoints_dir"])
if os.path.exists(sadtalker_paths["checkpoints_dir"]):
    for fn in os.listdir(sadtalker_paths["checkpoints_dir"]):
        print("  -", fn)
else:
    print("[ERROR] Checkpoints folder not found!")

print("[INIT] Starting Flask app setup...")

# === Init Flask App and CORS ===
app = Flask(__name__)
CORS(app)
print("[INIT] Flask app and CORS initialized")

# === Configure logging ===
logging.basicConfig(
    filename='app_errors.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s: %(message)s'
)
print("[INIT] Logging configured")

# === Output folders ===
OUTPUT_FOLDER = os.path.join(os.getcwd(), "output")
AVATAR_FOLDER = os.path.join(OUTPUT_FOLDER, "avatars")
SADTALKER_RESULTS = os.path.join(os.getcwd(), "SadTalker", "results")

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(AVATAR_FOLDER, exist_ok=True)
os.makedirs(SADTALKER_RESULTS, exist_ok=True)
print(f"[INIT] Output folders ready: {OUTPUT_FOLDER}, {AVATAR_FOLDER}, {SADTALKER_RESULTS}")

# === Lazy-loaded global instances ===
tts = None
sadtalker = None
print("[INIT] Lazy-load variables initialized")

# === Helper to remove avatar background ===
def remove_avatar_background(input_path, output_path):
    print(f"[BG-REMOVE] Removing background from {input_path}")
    try:
        input_image = Image.open(input_path).convert("RGBA")
        output_image = remove(input_image)
        output_image.save(output_path)
        print(f"[BG-REMOVE] Saved processed image to {output_path}")
    except Exception as e:
        print(f"[ERROR] Background removal failed: {e}")
        raise

# === Routes ===
@app.route("/upload-avatar", methods=["POST"])
def upload_avatar():
    print("[ROUTE] /upload-avatar called")
    if "avatar" not in request.files:
        logging.error("Upload avatar failed: No file part in request")
        return jsonify({"success": False, "error": "No file provided"}), 400

    file = request.files["avatar"]
    if file.filename == "":
        logging.error("Upload avatar failed: Empty filename")
        return jsonify({"success": False, "error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(AVATAR_FOLDER, filename)
    file.save(filepath)
    print(f"[UPLOAD] Avatar saved to {filepath}")

    try:
        transparent_filename = f"transparent_{filename}"
        transparent_path = os.path.join(AVATAR_FOLDER, transparent_filename)
        remove_avatar_background(filepath, transparent_path)
        return jsonify({"success": True, "path": f"/avatars/{transparent_filename}"})
    except Exception as e:
        logging.error(f"Background removal failed: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"success": False, "error": "Background removal failed"}), 500

@app.route("/avatars/<filename>")
def serve_avatar(filename):
    print(f"[ROUTE] Serving avatar: {filename}")
    return send_from_directory(AVATAR_FOLDER, filename)

@app.route("/generate-audio", methods=["POST"])
def generate_audio():
    print("[ROUTE] /generate-audio called")
    global tts
    if tts is None:
        print("[TTS] Initializing TTS...")
        try:
            from TTS.api import TTS
            from TTS.utils.audio import processor
            _original_init = processor.AudioProcessor.__init__

            def fast_load_init(self, *args, fast_load=True, **kwargs):
                self.fast_load = fast_load
                _original_init(self, *args, **kwargs)
                if self.fast_load:
                    self.mel_basis = None
                    self.stft = None

            processor.AudioProcessor.__init__ = fast_load_init
            tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)
            print("[TTS] TTS initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize TTS: {str(e)}\n{traceback.format_exc()}")
            return jsonify({"success": False, "error": "Failed to initialize TTS"}), 500

    data = request.get_json()
    text = data.get("text", "")
    if not text.strip():
        return jsonify({"success": False, "error": "No text provided"}), 400

    output_file = os.path.join(OUTPUT_FOLDER, "output.wav")
    try:
        tts.tts_to_file(text=text, file_path=output_file)
        print(f"[TTS] Audio saved to {output_file}")
        return jsonify({"success": True, "url": "/audio/output.wav"})
    except Exception as e:
        logging.error(f"TTS generation error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"success": False, "error": "Text-to-speech generation failed"}), 500

@app.route("/audio/<filename>")
def serve_audio(filename):
    print(f"[ROUTE] Serving audio: {filename}")
    return send_from_directory(OUTPUT_FOLDER, filename)

# === Updated generate-video route ===
@app.route("/generate-video", methods=["POST"])
def generate_video():
    print("[ROUTE] /generate-video called")
    global sadtalker

    # Initialize SadTalker if not already
    if sadtalker is None:
        print("[SADTALKER] Initializing SadTalker...")
        try:
            from gradio_demo import SadTalker
            sadtalker = SadTalker(
                checkpoint_path=sadtalker_paths["checkpoints_dir"],
                config_path=sadtalker_paths["config_dir"],
                lazy_load=False
            )
            print("[SADTALKER] Initialized successfully")
        except Exception as e:
            print("[ERROR] Failed to init SadTalker:", e)
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500

    try:
        data = request.get_json()
        avatar_filename = data.get("avatar")
        mode = data.get("mode", "full")

        if not avatar_filename:
            return jsonify({"success": False, "error": "No avatar filename provided"}), 400

        # Strip leading /avatars/ from frontend path
        avatar_rel = avatar_filename.replace("/avatars/", "")

        # Uploaded avatars go to server/output/avatars
        uploaded_avatar_path = os.path.join(AVATAR_FOLDER, avatar_rel)

        # Preloaded avatars live in frontend's public/avatars (one dir above server/)
        preloaded_avatar_path = os.path.join(os.path.dirname(BASE_DIR), "public", "avatars", avatar_rel)

        # Determine which source exists
        if os.path.exists(uploaded_avatar_path):
            source_path = uploaded_avatar_path
            print(f"[DEBUG] Using uploaded avatar: {source_path}")
        elif os.path.exists(preloaded_avatar_path):
            source_path = preloaded_avatar_path
            print(f"[DEBUG] Using preloaded avatar: {source_path}")
        else:
            logging.error(f"Avatar file not found: {avatar_rel}")
            return jsonify({"success": False, "error": f"Avatar not found: {avatar_rel}"}), 404

        # Generate transparent avatar if it doesn't exist
        transparent_filename = f"transparent_{avatar_rel}"
        transparent_path = os.path.join(AVATAR_FOLDER, transparent_filename)
        if not os.path.exists(transparent_path):
            print(f"[BG-REMOVE] Generating transparent avatar: {transparent_filename}")
            remove_avatar_background(source_path, transparent_path)
        else:
            print(f"[BG-REMOVE] Transparent avatar already exists: {transparent_filename}")

        # Use transparent avatar for SadTalker
        avatar_full = transparent_path
        print(f"[DEBUG] Avatar to use for SadTalker: {avatar_full}")

        # Ensure TTS audio exists
        audio_path = os.path.join(OUTPUT_FOLDER, "output.wav")
        if not os.path.exists(audio_path):
            return jsonify({"success": False, "error": "Audio file not found"}), 404

        # Run SadTalker
        print("[SADTALKER] Running test()...")
        video_path = sadtalker.test(
            source_image=avatar_full,
            driven_audio=audio_path,
            preprocess='crop',
            still_mode=False,
            use_enhancer=False,
            batch_size=1,
            size=256
        )
        print(f"[SADTALKER] Video generated at {video_path}")

        # Demo mode
        if mode == "demo":
            demo_video_path = os.path.join("public", "demo.mp4")
            shutil.copy(video_path, demo_video_path)
            return jsonify({"success": True, "video_path": "/demo.mp4"})

        return jsonify({"success": True, "video_path": video_path})

    except Exception as e:
        logging.error(f"Video generation failed: {str(e)}\n{traceback.format_exc()}")
        traceback.print_exc()
        return jsonify({"success": False, "error": "Video generation failed"}), 500

@app.route("/select-scene-assets", methods=["POST"])
def select_scene_assets():
    print("[ROUTE] /select-scene-assets called")
    try:
        data = request.get_json()
        selected_background = data.get("background")
        selected_music = data.get("music")
        if not selected_background or not selected_music:
            return jsonify({"success": False, "error": "Background or music not provided"}), 400

        bg_src = os.path.join(os.getcwd(), "public", "backgrounds", selected_background)
        bg_dest = os.path.join(OUTPUT_FOLDER, "background.png")
        music_src = os.path.join(os.getcwd(), "public", "music", selected_music)
        music_dest = os.path.join(OUTPUT_FOLDER, "music.mp3")

        shutil.copy(bg_src, bg_dest)
        shutil.copy(music_src, music_dest)
        return jsonify({"success": True, "message": "Scene assets copied successfully."})
    except Exception as e:
        logging.error(f"Error copying scene assets: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"success": False, "error": "Failed to copy scene assets"}), 500

@app.route("/process-preloaded-avatar", methods=["POST"])
def process_preloaded_avatar():
    print("[ROUTE] /process-preloaded-avatar called")
    try:
        data = request.get_json()
        relative_path = data.get("path")
        if not relative_path:
            return jsonify({"success": False, "error": "No avatar path provided"}), 400

        input_path = os.path.join(os.getcwd(), relative_path)
        if not os.path.exists(input_path):
            return jsonify({"success": False, "error": "Avatar file not found"}), 404

        filename = os.path.basename(relative_path)
        transparent_filename = f"transparent_{filename}"
        output_path = os.path.join(AVATAR_FOLDER, transparent_filename)
        remove_avatar_background(input_path, output_path)

        return jsonify({"success": True, "path": f"/avatars/{transparent_filename}"})
    except Exception as e:
        logging.error(f"Error processing preloaded avatar: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"success": False, "error": "Failed to process preloaded avatar"}), 500
    
@app.route("/video/<filename>")
def serve_video(filename):
    print(f"[ROUTE] Serving video: {filename}")
    return send_from_directory(OUTPUT_FOLDER, filename)
   

# === Run Flask Server ===
if __name__ == "__main__":
    print("[MAIN] Running Flask server on port 5001...")
    app.run(port=5001, debug=False, use_reloader=False)

