from TTS.api import TTS

# Pick a TTS model (single speaker for simplicity)
tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)

# Generate speech
tts.tts_to_file(text="This is a test of Coqui T T S. 1 2 3", file_path="output1.wav")
