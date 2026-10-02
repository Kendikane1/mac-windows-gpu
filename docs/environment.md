# Python and CUDA environment

Install [Git for Windows](https://git-scm.com/install/windows) and [uv](https://docs.astral.sh/uv/getting-started/installation/) from official sources if absent. Keep system Python intact. Clone this repository to a local non-synced folder. Commands below run in **PowerShell from the checkout root** unless stated otherwise.

## Storage gate and cache layout

Read [planning](planning.md) before downloading wheels. At least 35 GiB free is a conservative starting gate for this example: roughly 15 GiB installation allowance plus 20 GiB Windows headroom. Reassess for a different volume or future releases. Stop if this gate fails; do not solve it by deleting personal files.

```powershell
$researchRoot = Join-Path $env:USERPROFILE 'Research'
$drive = [IO.DriveInfo]::new([IO.Path]::GetPathRoot($researchRoot))
if ($drive.AvailableFreeSpace -lt 35GB) { throw 'Insufficient planned installation headroom' }
$env:UV_CACHE_DIR = Join-Path $researchRoot 'cache\uv'
$env:UV_PYTHON_INSTALL_DIR = Join-Path $researchRoot 'python'
uv python install 3.12
uv sync --project .\environment --locked
if ($LASTEXITCODE -ne 0) { throw 'Environment sync failed' }
```

These environment variables apply to the current shell only. Document or set your own per-user cache paths deliberately if you want them persisted. Do not set global `PYTHONPATH` or use global pip. The project owns `environment/.venv`.

## Why a dedicated CUDA source?

The supplied project pins torch 2.13.0 and uses an explicit official `cu130` index only on Windows. Apple Silicon uses PyPI. CUDA is not available on macOS; using the Mac as an SSH/browser client requires no local Python installation. See [uv's PyTorch integration guide](https://docs.astral.sh/uv/guides/integration/pytorch/).

This environment intentionally omits the original scientific project's libraries and torchvision: neither is necessary for matrix multiplication or Jupyter. It supports Windows x64 and Apple Silicon resolution, not arbitrary platforms. The original torch Mac wheel required macOS 14 or newer; actual Mac execution remains a separate test.

Check the installed NVIDIA driver against [NVIDIA's CUDA compatibility guidance](https://docs.nvidia.com/deploy/cuda-compatibility/minor-version-compatibility.html) and the [PyTorch selector](https://pytorch.org/get-started/locally/). CUDA 13.x needs the appropriate 580-or-newer driver family; the historical workstation used 591.86. Prebuilt PyTorch wheels include runtime components; do not install a full CUDA toolkit unless a concrete dependency needs compilation.

## Verify actual GPU computation

```powershell
& .\environment\.venv\Scripts\python.exe .\examples\gpu_check.py
```

The probe uses seeded 64×64 float64 tensors, synchronizes CUDA, and compares against CPU multiplication with `rtol=1e-10`, `atol=1e-10`. It prints Python/PyTorch/CUDA versions, GPU identity, maximum error, and allocator memory. Allocator figures exclude the driver context and other processes. It downloads no models and saves no scientific results.

Run it only when a small GPU allocation will not disturb existing jobs. A driver compatibility label alone is not a PASS. A CPU-only PyTorch wheel, missing driver, or failed comparison must remain a FAIL until diagnosed.

## Updates

Use `uv sync --locked` for reproduction. Edit version pins deliberately and run `uv lock` only when reviewing an update. Review both `pyproject.toml` and `uv.lock`; recheck the Windows GPU and Mac resolution paths before committing. Do not silently loosen another project's dependencies or replace its lock with this one.

For an existing research repository, use its own Python/version constraints, instructions, tests, and environment. The helpers accept an explicit interpreter path; never assume that a successful example environment proves a different project's GPU support.
