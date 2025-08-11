from vllm import LLM, SamplingParams
from app.config import LLM_MODEL, MODELS_DIR
from huggingface_hub import snapshot_download

class LLM_Agent:
    def __init__(self):
        # Download model if not already present
        model_path = MODELS_DIR / LLM_MODEL.split("/")[-1]
        if not model_path.exists():
            snapshot_download(
                LLM_MODEL,
                local_dir=str(model_path),
                local_dir_use_symlinks=False
            )
        
        self.llm = LLM(
            model=str(model_path),
            tokenizer=str(model_path),
            dtype="float32",  # CPU-compatible
            tensor_parallel_size=1
        )
        self.sampling_params = SamplingParams(
            temperature=0.7,
            top_p=0.9,
            max_tokens=256
        )

    def generate(self, prompt: str) -> str:
        outputs = self.llm.generate([prompt], self.sampling_params)
        return outputs[0].outputs[0].text