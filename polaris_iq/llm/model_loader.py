# llm/model_loader.py
# Uses llama-server.exe (pre-compiled CUDA 12.4) as the inference backend.
# Falls back to llama-cpp-python if the server is not available.

import os
import json
import time
import subprocess
import requests
from pathlib import Path


# Default paths — override via environment variables
_LLAMA_BIN_DIR = os.environ.get(
    "LLAMA_CPP_BIN_DIR",
    r"C:\Users\ujjan\Downloads\llama-b8611-bin-win-cuda-12.4-x64",
)
_LLAMA_SERVER_EXE = os.path.join(_LLAMA_BIN_DIR, "llama-server.exe")
_LLAMA_SERVER_PORT = int(os.environ.get("LLAMA_SERVER_PORT", "8081"))


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

        self._model_path = model_path
        self._server_url = f"http://127.0.0.1:{_LLAMA_SERVER_PORT}"
        self._server_process = None
        self._use_server = False

        # Try to use llama-server.exe (CUDA) if available
        if os.path.exists(_LLAMA_SERVER_EXE):
            self._start_server(model_path, n_ctx, n_gpu_layers, n_threads)
        else:
            # Fallback: use llama-cpp-python (CPU)
            from llama_cpp import Llama
            self._llama = Llama(
                model_path=model_path,
                n_ctx=n_ctx,
                n_gpu_layers=n_gpu_layers,
                n_threads=n_threads,
                verbose=verbose,
            )

    def _start_server(self, model_path, n_ctx, n_gpu_layers, n_threads):
        """Start llama-server.exe as a subprocess with CUDA acceleration."""

        # Check if server is already running
        try:
            resp = requests.get(f"{self._server_url}/health", timeout=2)
            if resp.status_code == 200:
                print(f"[PolarisIQ] llama-server already running on port {_LLAMA_SERVER_PORT}")
                self._use_server = True
                return
        except requests.ConnectionError:
            pass

        print(f"[PolarisIQ] Starting llama-server.exe (CUDA 12.4) on port {_LLAMA_SERVER_PORT}...")

        cmd = [
            _LLAMA_SERVER_EXE,
            "--model", model_path,
            "--ctx-size", str(n_ctx),
            "--n-gpu-layers", str(n_gpu_layers),
            "--threads", str(n_threads),
            "--port", str(_LLAMA_SERVER_PORT),
            "--host", "127.0.0.1",
        ]

        self._server_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )

        # Wait for server to be ready (up to 60s for large models)
        for i in range(120):
            try:
                resp = requests.get(f"{self._server_url}/health", timeout=1)
                if resp.status_code == 200:
                    print(f"[PolarisIQ] llama-server ready (GPU CUDA) on port {_LLAMA_SERVER_PORT}")
                    self._use_server = True
                    return
            except requests.ConnectionError:
                pass
            time.sleep(0.5)

        raise RuntimeError(
            "llama-server.exe failed to start within 60s. "
            "Check if the model path is correct and CUDA drivers are installed."
        )

    _DEFAULT_SYSTEM = "You are a strict JSON compiler. Output ONLY valid JSON with no extra text."

    def generate(
        self, prompt: str, max_tokens: int = 800, temperature: float = 0.0,
        system_prompt: str = None,
    ) -> str:

        sys_msg = system_prompt or self._DEFAULT_SYSTEM

        if self._use_server:
            return self._generate_via_server(prompt, max_tokens, temperature, sys_msg)
        else:
            return self._generate_via_python(prompt, max_tokens, temperature, sys_msg)

    def _generate_via_server(self, prompt, max_tokens, temperature, system_prompt):
        """Call llama-server.exe's OpenAI-compatible chat endpoint."""

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        try:
            resp = requests.post(
                f"{self._server_url}/v1/chat/completions",
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            raise RuntimeError(f"llama-server request failed: {e}")

        choices = data.get("choices")
        if not choices or len(choices) == 0:
            raise ValueError(f"LLM returned no choices: {data}")

        message = choices[0].get("message")
        if message is None:
            raise ValueError(f"LLM returned no message: {choices[0]}")

        content = message.get("content")
        if content is None:
            raise ValueError(f"LLM returned None content: {message}")

        return content

    def _generate_via_python(self, prompt, max_tokens, temperature, system_prompt):
        """Fallback: use llama-cpp-python directly."""

        response = self._llama.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        if response is None:
            raise ValueError("LLM returned None response")

        choices = response.get("choices")
        if not choices or len(choices) == 0:
            raise ValueError(f"LLM returned no choices: {response}")

        message = choices[0].get("message")
        if message is None:
            raise ValueError(f"LLM returned no message: {choices[0]}")

        content = message.get("content")
        if content is None:
            raise ValueError(f"LLM returned None content: {message}")

        return content

    def shutdown(self):
        """Stop the llama-server subprocess if we started it."""
        if self._server_process:
            self._server_process.terminate()
            self._server_process.wait(timeout=10)
            self._server_process = None
