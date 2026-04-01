import os
from pathlib import Path


# Project root: two levels up from this file (core/config.py → polaris_iq → project root)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class PolarisConfig:
    def __init__(self):
        self.MODEL_PATH = os.environ.get(
            "POLARISIQ_MODEL_PATH",
            str(_PROJECT_ROOT / "models" / "Qwen2.5-7B-Instruct-Q4_K_M.gguf"),
        )
        self.CONTEXT_SIZE = int(os.environ.get("POLARISIQ_CONTEXT_SIZE", "4096"))
        self.DUCKDB_PATH = os.environ.get("POLARISIQ_DB_PATH", "polaris.db")

