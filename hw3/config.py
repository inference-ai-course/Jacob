from pathlib import Path

# Paths
MODELS_DIR = Path("models")
MODELS_DIR.mkdir(exist_ok=True)

# Model configurations
ASR_MODEL = "small"  # faster-whisper model size (tiny, base, small, medium, large)
LLM_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"
TTS_MODEL = "tts_models/en/ljspeech/glow-tts"

# Conversation settings
MAX_CONVERSATION_TURNS = 5