"""Tiny synthetic CUDA check; no models, downloads, or scientific data."""

import json
import platform
import sys

import torch


def check_gpu():
    details = {
        "python": platform.python_version(),
        "executable": sys.executable,
        "torch": torch.__version__,
        "torch_cuda": torch.version.cuda,
        "cuda_available": torch.cuda.is_available(),
    }
    if not details["cuda_available"]:
        raise RuntimeError(f"CUDA unavailable: {json.dumps(details)}")
    torch.set_num_threads(2)
    torch.cuda.init()
    torch.cuda.reset_peak_memory_stats()
    generator = torch.Generator(device="cpu").manual_seed(1729)
    a = torch.randn((64, 64), generator=generator, dtype=torch.float64)
    b = torch.randn((64, 64), generator=generator, dtype=torch.float64)
    reference = a @ b
    ga, gb = a.cuda(), b.cuda()
    result = ga @ gb
    torch.cuda.synchronize()
    actual = result.cpu()
    torch.testing.assert_close(actual, reference, rtol=1e-10, atol=1e-10)
    return {
        **details,
        "status": "PASS",
        "synthetic_only": True,
        "gpu": torch.cuda.get_device_name(0),
        "shape": [64, 64],
        "dtype": "float64",
        "rtol": 1e-10,
        "atol": 1e-10,
        "max_absolute_error": float((actual - reference).abs().max()),
        "allocated_bytes": torch.cuda.memory_allocated(),
        "peak_allocated_bytes": torch.cuda.max_memory_allocated(),
        "reserved_bytes": torch.cuda.memory_reserved(),
        "memory_scope": "PyTorch allocator only; excludes context and other processes",
        "synchronized": True,
    }


if __name__ == "__main__":
    print(json.dumps(check_gpu(), indent=2))
