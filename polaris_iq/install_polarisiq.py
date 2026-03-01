import sys
import subprocess
import importlib.util
import os
from typing import List


MIN_PYTHON = (3, 10)


REQUIRED_LIBRARIES = [
    "duckdb",
    "polars",
    "pyarrow",
    "pandas",
    "numpy",
    "scikit-learn",
    "pydantic",
    "diskcache",
    "fastapi",
    "matplotlib",
]


OPTIONAL_LIBRARIES = [
    "scipy",
    "statsmodels",
    "joblib",
    "numexpr",
]


def _is_installed(package: str) -> bool:
    spec = importlib.util.find_spec(package.replace("-", "_"))
    return spec is not None


def _run_command(cmd: List[str], env=None):
    subprocess.check_call(cmd, env=env)


def _check_cuda_available() -> bool:
    try:
        subprocess.check_output(["nvidia-smi"])
        return True
    except Exception:
        return False


def _install_standard_package(package: str):
    print(f"Installing {package}...")
    _run_command([sys.executable, "-m", "pip", "install", "--upgrade", package])


def _install_llama_cpp_gpu():
    print("Installing llama-cpp-python with CUDA support...")

    env = os.environ.copy()
    env["CMAKE_ARGS"] = "-DGGML_CUDA=on"
    env["FORCE_CMAKE"] = "1"

    _run_command(
        [sys.executable, "-m", "pip", "install", "--upgrade", "llama-cpp-python"],
        env=env,
    )


def _install_llama_cpp_cpu():
    print("Installing llama-cpp-python (CPU mode)...")
    _run_command(
        [sys.executable, "-m", "pip", "install", "--upgrade", "llama-cpp-python"]
    )


def install_polaris_dependencies(include_optional: bool = False):
    """
    Install PolarisIQ dependencies with GPU-enabled llama-cpp-python if CUDA is available.
    """

    print("Checking Python version...")

    if sys.version_info < MIN_PYTHON:
        raise RuntimeError(
            f"PolarisIQ requires Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+"
        )

    print("Python version OK\n")

    print("Installing required libraries...\n")

    for package in REQUIRED_LIBRARIES:
        if not _is_installed(package):
            _install_standard_package(package)
        else:
            print(f"{package} already installed.")

    print("\nChecking CUDA availability...\n")

    if _check_cuda_available():
        print("CUDA detected via nvidia-smi.")
        _install_llama_cpp_gpu()
    else:
        print("CUDA not detected. Falling back to CPU build.")
        _install_llama_cpp_cpu()

    if include_optional:
        print("\nInstalling optional libraries...\n")
        for package in OPTIONAL_LIBRARIES:
            if not _is_installed(package):
                _install_standard_package(package)
            else:
                print(f"{package} already installed.")

    print("\nPolarisIQ environment setup complete.")


if __name__ == "__main__":
    install_polaris_dependencies(include_optional=True)
