from TTS.api import TTS
from app.config import TTS_MODEL, MODELS_DIR
import numpy as np
import sounddevice as sd
import io
from pydub import AudioSegment

class TTS_Engine:
    def __init__(self):
        self.tts = TTS(
            model_name=TTS_MODEL,
            progress_bar=False,
            gpu=False
        )

    def synthesize(self, text: str) -> bytes:
        if not text.strip():
            return b""
            
        # Synthesize to file-like object
        with io.BytesIO() as wav_io:
            self.tts.tts_to_file(
                text=text,
                file_path=wav_io,
                speaker=self.tts.speakers[0] if self.tts.speakers else None
            )
            wav_io.seek(0)
            return wav_io.read()

    def play_audio(self, audio_bytes: bytes):
        """Play audio bytes directly"""
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
        samples = np.array(audio.get_array_of_samples())
        sd.play(samples, audio.frame_rate)
        sd.wait()