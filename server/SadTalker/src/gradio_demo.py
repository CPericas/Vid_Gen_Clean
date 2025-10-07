import torch, uuid
import os, sys, shutil
from utils.preprocess import CropAndExtract
from test_audio2coeff import Audio2Coeff  
from facerender.animate import AnimateFromCoeff
from generate_batch import get_data
from generate_facerender_batch import get_facerender_data
from SadTalker.src.utils.init_path import init_path
from pydub import AudioSegment
import logging, traceback

# === Setup logging for SadTalker ===
logging.basicConfig(level=logging.DEBUG, format='[SADTALKER-LOG] %(message)s')

def mp3_to_wav(mp3_filename, wav_filename, frame_rate):
    mp3_file = AudioSegment.from_file(file=mp3_filename)
    mp3_file.set_frame_rate(frame_rate).export(wav_filename, format="wav")


class SadTalker():
    def __init__(self, checkpoint_path='checkpoints', config_path='src/config', lazy_load=False):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        os.environ['TORCH_HOME'] = checkpoint_path
        self.checkpoint_path = checkpoint_path
        self.config_path = config_path

    def test(self, source_image, driven_audio, preprocess='crop', 
             still_mode=False, use_enhancer=False, batch_size=1, size=256, 
             pose_style=0, exp_scale=1.0, 
             use_ref_video=False, ref_video=None, ref_info=None,
             use_idle_mode=False, length_of_audio=0, use_blink=True,
             result_dir='./results/'):

        try:
            logging.debug("Initializing SadTalker paths...")
            self.sadtalker_paths = init_path(self.checkpoint_path, self.config_path, size, False, preprocess)
            logging.debug(f"Paths: {self.sadtalker_paths}")

            logging.debug("Loading Audio2Coeff model...")
            self.audio_to_coeff = Audio2Coeff(self.sadtalker_paths, self.device)
            logging.debug("Audio2Coeff loaded successfully ✅")

            logging.debug("Loading CropAndExtract model...")
            self.preprocess_model = CropAndExtract(self.sadtalker_paths, self.device)
            logging.debug("CropAndExtract loaded successfully ✅")

            logging.debug("Loading AnimateFromCoeff model...")
            self.animate_from_coeff = AnimateFromCoeff(self.sadtalker_paths, self.device)
            logging.debug("AnimateFromCoeff loaded successfully ✅")

            # --- Setup directories ---
            time_tag = str(uuid.uuid4())
            save_dir = os.path.join(result_dir, time_tag)
            os.makedirs(save_dir, exist_ok=True)
            input_dir = os.path.join(save_dir, 'input')
            os.makedirs(input_dir, exist_ok=True)
            logging.debug(f"Created save_dir: {save_dir} and input_dir: {input_dir}")

            # --- Move source image ---
            pic_path = os.path.join(input_dir, os.path.basename(source_image)) 
            shutil.move(source_image, pic_path)
            logging.debug(f"Moved source_image to {pic_path}")

            # --- Move or convert driven audio ---
            if driven_audio and os.path.isfile(driven_audio):
                audio_path = os.path.join(input_dir, os.path.basename(driven_audio))
                if '.mp3' in audio_path:
                    logging.debug("Converting mp3 to wav...")
                    mp3_to_wav(driven_audio, audio_path.replace('.mp3', '.wav'), 16000)
                    audio_path = audio_path.replace('.mp3', '.wav')
                else:
                    shutil.move(driven_audio, input_dir)
                logging.debug(f"Audio prepared at {audio_path}")
            elif use_idle_mode:
                audio_path = os.path.join(input_dir, f'idlemode_{length_of_audio}.wav')
                AudioSegment.silent(duration=1000*length_of_audio).export(audio_path, format="wav")
                logging.debug(f"Generated silent audio at {audio_path}")
            else:
                assert use_ref_video == True and ref_info == 'all'

            # --- Preprocess first frame ---
            first_frame_dir = os.path.join(save_dir, 'first_frame_dir')
            os.makedirs(first_frame_dir, exist_ok=True)
            first_coeff_path, crop_pic_path, crop_info = self.preprocess_model.generate(pic_path, first_frame_dir, preprocess, True, size)
            if first_coeff_path is None:
                raise AttributeError("No face detected in source image")
            logging.debug(f"First frame processed: coeff_path={first_coeff_path}")

            # --- Optional reference video processing ---
            if use_ref_video:
                ref_video_videoname = os.path.splitext(os.path.basename(ref_video))[0]
                ref_video_frame_dir = os.path.join(save_dir, ref_video_videoname)
                os.makedirs(ref_video_frame_dir, exist_ok=True)
                logging.debug("Extracting 3DMM from reference video...")
                ref_video_coeff_path, _, _ = self.preprocess_model.generate(ref_video, ref_video_frame_dir, preprocess, source_image_flag=False)
            else:
                ref_video_coeff_path = None

            # --- Generate coefficients ---
            if use_ref_video and ref_info == 'all':
                coeff_path = ref_video_coeff_path
            else:
                batch = get_data(first_coeff_path, audio_path, self.device,
                                 ref_eyeblink_coeff_path=None, still=still_mode,
                                 idlemode=use_idle_mode, length_of_audio=length_of_audio,
                                 use_blink=use_blink)
                coeff_path = self.audio_to_coeff.generate(batch, save_dir, pose_style)
            logging.debug(f"Coefficient generation completed: {coeff_path}")

            # --- Generate video ---
            data = get_facerender_data(coeff_path, crop_pic_path, first_coeff_path, audio_path,
                                       batch_size, still_mode=still_mode, preprocess=preprocess,
                                       size=size, expression_scale=exp_scale)
            video_path = self.animate_from_coeff.generate(data, save_dir, pic_path, crop_info,
                                                          enhancer='gfpgan' if use_enhancer else None,
                                                          preprocess=preprocess, img_size=size)
            logging.debug(f"Video generated at: {video_path}")

            # --- Cleanup ---
            del self.preprocess_model
            del self.audio_to_coeff
            del self.animate_from_coeff
            import gc
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.synchronize()
            gc.collect()
            logging.debug("Memory cleaned up successfully ✅")

            return video_path

        except Exception as e:
            logging.error("SadTalker.test() failed:\n" + traceback.format_exc())
            raise

