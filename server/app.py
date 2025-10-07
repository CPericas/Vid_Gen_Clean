from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from rembg import remove
from PIL import Image
import os, sys, logging, traceback, shutil, subprocess

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

    # Save the original file
    filename = secure_filename(file.filename)
    filepath = os.path.join(AVATAR_FOLDER, filename)
    file.save(filepath)
    print(f"[UPLOAD] Avatar saved to {filepath}")

    try:
        # Always save the processed file as .png (supports RGBA)
        base, _ = os.path.splitext(filename)
        transparent_filename = f"transparent_{base}.png"
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

# === Updated generate-video route with overlay + music mix ===
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

        avatar_rel = avatar_filename.replace("/avatars/", "")

        uploaded_avatar_path = os.path.join(AVATAR_FOLDER, avatar_rel)
        preloaded_avatar_path = os.path.join(os.path.dirname(BASE_DIR), "public", "avatars", avatar_rel)

        if os.path.exists(uploaded_avatar_path):
            source_path = uploaded_avatar_path
            print(f"[DEBUG] Using uploaded avatar: {source_path}")
        elif os.path.exists(preloaded_avatar_path):
            source_path = preloaded_avatar_path
            print(f"[DEBUG] Using preloaded avatar: {source_path}")
        else:
            return jsonify({"success": False, "error": f"Avatar not found: {avatar_rel}"}), 404

        # ensure a transparent PNG exists (created earlier by remove_avatar_background)
        transparent_filename = f"transparent_{avatar_rel}"
        transparent_path = os.path.join(AVATAR_FOLDER, transparent_filename)
        if not os.path.exists(transparent_path):
            print(f"[BG-REMOVE] Generating transparent avatar: {transparent_filename}")
            remove_avatar_background(source_path, transparent_path)
        else:
            print(f"[BG-REMOVE] Transparent avatar already exists: {transparent_filename}")

        avatar_full = transparent_path
        print(f"[DEBUG] Avatar to use for SadTalker: {avatar_full}")

        # Ensure TTS audio exists
        audio_path = os.path.join(OUTPUT_FOLDER, "output.wav")
        if not os.path.exists(audio_path):
            return jsonify({"success": False, "error": "Audio file not found"}), 404

        # Run SadTalker -> produces a video (usually in results/<uuid>/transparent_<name>__output.mp4)
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
        video_path = os.path.abspath(video_path)
        print(f"[SADTALKER] Video generated at {video_path}")

        # Prepare final composite
        final_path = os.path.join(OUTPUT_FOLDER, "final_video.mp4")
        background_path = os.path.join(OUTPUT_FOLDER, "background.png")
        music_path = os.path.join(OUTPUT_FOLDER, "music.mp3")

        if not (os.path.exists(background_path) and os.path.exists(music_path)):
            print("[WARN] Missing background.png or music.mp3, returning raw SadTalker video")
            return jsonify({"success": True, "video_path": video_path})

        # avatar_full is the transparent PNG produced earlier (output/avatars/transparent_*.png)
        avatar_png = os.path.abspath(avatar_full)
        if not os.path.exists(avatar_png):
            print(f"[ERROR] Transparent PNG not found at {avatar_png}; falling back to simple overlay without feather.")
            # fallback simple overlay using the SadTalker video directly
            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-i", background_path,
                "-i", video_path,
                "-i", music_path,
                "-filter_complex",
                (
                    "[1:v]scale=550:-1[avatar];"
                    "[2:a]volume=0.3[music];"
                    "[0:v][avatar]overlay=(W-w)/2:H-h-200[vout];"
                    "[1:a][music]amix=inputs=2:duration=first:dropout_transition=2[aout]"
                ),
                "-map", "[vout]",
                "-map", "[aout]",
                "-c:v", "libx264",
                "-crf", "18",
                "-preset", "veryfast",
                "-c:a", "aac",
                "-shortest",
                final_path
            ]
            print("[FFMPEG] Running fallback overlay (no feather)...")
            subprocess.run(ffmpeg_cmd, check=True)
            print(f"[FFMPEG] Final video ready at {final_path}")
            return jsonify({"success": True, "video_path": f"/video/{os.path.basename(final_path)}"})

        # ---- MAIN: use PNG mask + SadTalker video to produce feathered avatar ----
        # Inputs order: [0]=background, [1]=video, [2]=avatar_png, [3]=music
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-i", background_path,    # 0
            "-i", video_path,         # 1
            "-i", avatar_png,         # 2 (transparent PNG created by remove_avatar_background)
            "-i", music_path,         # 3
            "-filter_complex",
            (
                # scale the SadTalker rendered frames (video) and make RGBA
                "[1:v]scale=550:-1,format=rgba[vid_rgba];"
                # scale the source PNG to exactly the same size and keep RGBA
                "[2:v]scale=550:-1,format=rgba[png_rgba];"
                # extract alpha from the scaled PNG and blur it (feather)
                "[png_rgba]alphaextract,boxblur=12:12[mask_blurred];"
                # alphamerge: put the blurred mask into the scaled video -> avatar with soft edges
                "[vid_rgba][mask_blurred]alphamerge[avatar_soft];"
                # lower music volume
                "[3:a]volume=0.28[music];"
                # overlay softened avatar onto the background (centered, slightly above bottom)
                "[0:v][avatar_soft]overlay=x=(W-w)/2:y=H-h-150:format=yuv420[vout];"
                # mix SadTalker audio (from input 1) with the lowered music
                "[1:a][music]amix=inputs=2:duration=first:dropout_transition=2[aout]"
            ),
            "-map", "[vout]",
            "-map", "[aout]",
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "veryfast",
            "-c:a", "aac",
            "-shortest",
            final_path
        ]

        print("[FFMPEG] Running composite (mask-based feathering)...")
        # capture output to help debugging if ffmpeg fails
        try:
            proc = subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
            print(proc.stdout)
            print(proc.stderr)
        except subprocess.CalledProcessError as e:
            print("[FFMPEG-ERROR] ffmpeg failed:")
            print(e.stdout if hasattr(e, "stdout") else "")
            print(e.stderr if hasattr(e, "stderr") else "")
            raise

        print(f"[DEBUG] Background path in use: {background_path}")
        print(f"[DEBUG] Music path in use: {music_path}")
        print(f"[FFMPEG] Final video ready at {final_path}")
        return jsonify({"success": True, "video_path": f"/video/{os.path.basename(final_path)}"})

    except Exception as e:
        logging.error(f"Video generation failed: {str(e)}\n{traceback.format_exc()}")
        traceback.print_exc()
        return jsonify({"success": False, "error": "Video generation failed"}), 500

@app.route("/select-scene-assets", methods=["POST"])
def select_scene_assets():
    try:
        data = request.get_json()
        selected_background = data.get("background")
        selected_music = data.get("music")

        if not selected_background or not selected_music:
            return jsonify({"success": False, "error": "Background or music not provided"}), 400

        # Normalize filenames (strip any leading paths)
        bg_name = os.path.basename(selected_background)
        music_name = os.path.basename(selected_music)

        # Correct source paths (go up one directory from /server to /Vid_Gen/public)
        bg_src = os.path.join(os.getcwd(), "..", "public", "backgrounds", bg_name)
        music_src = os.path.join(os.getcwd(), "..", "public", "music", music_name)
        bg_dest = os.path.join(OUTPUT_FOLDER, "background.png")
        music_dest = os.path.join(OUTPUT_FOLDER, "music.mp3")

        # Debug confirmation
        print(f"[DEBUG] Background source: {bg_src}")
        print(f"[DEBUG] Music source: {music_src}")
        print(f"[DEBUG] Destination folder: {OUTPUT_FOLDER}")

        # Clear old files before copying
        for f in [bg_dest, music_dest]:
            if os.path.exists(f):
                os.remove(f)

        shutil.copy(bg_src, bg_dest)
        shutil.copy(music_src, music_dest)

        print(f"[ASSETS] Copied {bg_name} and {music_name} to output/")
        return jsonify({"success": True, "message": "Scene assets copied successfully."})

    except Exception as e:
        logging.error(f"Scene asset selection failed: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"success": False, "error": "Scene asset selection failed"}), 500

@app.route("/process-preloaded-avatar", methods=["POST"])
def process_preloaded_avatar():
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
    return send_from_directory("output", filename, mimetype="video/mp4")

@app.route("/download-video")
def download_video():
    return send_file(
        os.path.join("output", "final_video.mp4"),   # FIXED: use final_video.mp4 directly
        mimetype="video/mp4",
        as_attachment=True,
        download_name="avatar_scene.mp4"
    )

# === Run Flask Server ===
if __name__ == "__main__":
    app.run(port=5001, debug=False, use_reloader=False)

