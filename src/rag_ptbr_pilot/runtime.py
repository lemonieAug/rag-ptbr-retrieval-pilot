"""Read-only runtime inventory; environment variables are allowlisted."""

from __future__ import annotations

import os
import platform
from importlib.metadata import PackageNotFoundError, version


def collect_environment() -> dict:
    libraries = ("torch", "transformers", "sentence-transformers", "accelerate",
                 "huggingface-hub", "numpy", "pydantic", "PyYAML", "pdfplumber",
                 "pypdf", "requests", "pytest")
    versions = {}
    for library in libraries:
        try:
            versions[library] = version(library)
        except PackageNotFoundError:
            versions[library] = None
    gpu = {"cuda_available": False, "device_count": 0, "device_name": None,
           "total_vram_bytes": None, "torch_cuda_version": None,
           "cuda_runtime_version": None}
    try:
        import torch

        gpu["torch_cuda_version"] = torch.version.cuda
        gpu["cuda_available"] = bool(torch.cuda.is_available())
        if gpu["cuda_available"]:
            import ctypes
            runtime_version = ctypes.c_int()
            try:
                if torch.cuda.cudart().cudaRuntimeGetVersion(ctypes.byref(runtime_version)) == 0:
                    number = runtime_version.value
                    gpu["cuda_runtime_version"] = f"{number // 1000}.{(number % 1000) // 10}"
            except (AttributeError, OSError):
                pass
            gpu["device_count"] = torch.cuda.device_count()
            gpu["device_name"] = torch.cuda.get_device_name(0)
            gpu["total_vram_bytes"] = int(torch.cuda.get_device_properties(0).total_memory)
    except (ImportError, RuntimeError, OSError, AssertionError):
        pass
    return {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "hostname": platform.node(),
        "runpod": bool(os.environ.get("RUNPOD_POD_ID")),
        "hf_cache_path": os.environ.get("HF_HOME"),
        "library_versions": versions,
        "gpu": gpu,
    }


def manifest_runtime_fields(cfg, env: dict, devices: dict, dtypes: dict) -> dict:
    """Only allowlisted metadata enters run_manifest.json."""
    return {
        "hardware": {
            **env.get("gpu", {}),
            "platform": env.get("platform"),
            "hostname": env.get("hostname"),
            "runpod": env.get("runpod"),
            "hf_cache_path": env.get("hf_cache_path"),
            "runtime_devices": devices,
            "runtime_dtypes": dtypes,
        },
        "parameters": {
            "batch_sizes": cfg.runtime.model_dump(mode="json"),
            "model_dtypes": {**cfg.models.dtype.model_dump(mode="json"),
                             "reranker": cfg.models.reranker.dtype},
        },
    }
