# llm/model_loader.py

from llama_cpp import Llama
import os


class PolarisModel:
    def __init__(
        self,
        model_path: str,
        n_ctx: int = 10000,
        n_gpu_layers: int = -1,
        n_threads: int = 8,
        verbose: bool = False,
    ):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")

        self.model = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            n_threads=n_threads,
            verbose=verbose,
        )

    def generate(
        self, prompt: str, max_tokens: int = 800, temperature: float = 0.0
    ) -> str:

        response = self.model.create_chat_completion(
            messages=[
                {"role": "system", "content": "You are a strict JSON compiler. Output ONLY valid JSON with no extra text."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return response["choices"][0]["message"]["content"]
