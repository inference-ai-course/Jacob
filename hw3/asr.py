from faster_whisper import WhisperModel
from app.config import ASR_MODEL, MODELS_DIR
import numpy as np
import webrtcvad
from pydub import AudioSegment
import io

class ASR:
    def __init__(self):
        self.model = WhisperModel(
            ASR_MODEL,
            device="cpu",
            compute_type="int8",
            download_root=str(MODELS_DIR)
        )
        self.vad = webrtcvad.Vad(2)  # Aggressiveness mode (0-3)

    def is_speech(self, audio_np: np.ndarray, sample_rate: int = 16000) -> bool:
        """Check if audio contains speech using VAD."""
        if sample_rate not in [8000, 16000, 32000, 48000]:
            raise ValueError("Sample rate must be 8000, 16000, 32000, or 48000 Hz")
        
        # Convert to 16-bit PCM
        audio_np = (audio_np * 32767).astype(np.int16)
        frame_duration = 30  # ms
        frame_size = int(sample_rate * frame_duration / 1000)
        
        for i in range(0, len(audio_np), frame_size):
            frame = audio_np[i:i+frame_size].tobytes()
            if len(frame) < frame_size * 2:  # 2 bytes per sample
                continue
            if self.vad.is_speech(frame, sample_rate):
                return True
        return False

    def transcribe(self, audio_bytes: bytes) -> str:
        """Transcribe audio bytes to text."""
        # Convert bytes to AudioSegment
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
        
        # Convert to mono 16kHz for Whisper
        audio = audio.set_frame_rate(16000).set_channels(1)
        
        # Convert to numpy array
        samples = np.array(audio.get_array_of_samples()).astype(np.float32) / 32768.0
        
        # Skip if no speech detected
        if not self.is_speech(samples):
            return ""
        
        segments, _ = self.model.transcribe(samples, beam_size=5)
        text = " ".join([segment.text for segment in segments])
        return text.strip()