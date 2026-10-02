# Plan before installing

The target is a Windows 11 x64 PC with an NVIDIA GPU, a Mac SSH client, reliable home internet, and someone who can press the PC's power button. Windows Home is sufficient for this approach; it does not rely on Remote Desktop hosting, WSL, or Docker.

## Read-only inventory

Run these in PowerShell. Keep the results private; system tools may include identifying information.

```powershell
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsBuildNumber
Get-CimInstance Win32_Processor | Select-Object Name
Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory
Get-Volume | Select-Object DriveLetter, SizeRemaining, Size
Get-Command git, uv, python, ssh, nvidia-smi -ErrorAction SilentlyContinue
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
Get-Service sshd, Tailscale -ErrorAction SilentlyContinue
powercfg /getactivescheme
powercfg /query SCHEME_CURRENT SUB_SLEEP
```

Check installed software and existing project folders before installing anything. Do not recursively inspect personal files or export identifiers. `nvidia-smi`'s CUDA label is driver compatibility, not proof of a toolkit or working Python CUDA environment.

Ask the owner about firmware/BitLocker prompts, administrator access, other users, outages, and local recovery help. A Windows sign-in password is different from a preboot password. Do not remove either to make remote access convenient.

## Storage and memory

Start with an allowance of **8–15 GiB** for Python, CUDA wheels, Jupyter, tools, and temporary downloads, while leaving **at least 20 GiB** free for Windows. These are planning allowances, not guaranteed requirements. If capacity is tight, stop before downloading the environment and choose more storage. Do not delete someone else's files or repartition the disk.

Put the checkout, caches, and output on a local non-synced volume. For example:

```text
<user profile>/Research/
  projects/mac-windows-gpu/
    environment/.venv/
    .local/                 # private runtime and synthetic checkpoints
  cache/uv/
  python/
```

Keeping uv cache and environments on the same NTFS volume allows hardlinks. Logical folder sizes can double-count them; compare actual free space before and after installation. Models, datasets, and checkpoints need their own additional budget.

An 8 GB system-RAM PC is constrained even with 8 GB VRAM. Start with small jobs; GPU memory and system memory are separate limits. Avoid parallel model loads, large data-loader worker counts, and assumptions that every model fits.

## Availability

Tailscale and sshd need to run before desktop login. Windows must also stay awake while plugged in. Inspect AC sleep/hibernate settings and decide deliberately whether to change them; turning off the screen alone is fine. Windows Update, lost power, and reboots can end jobs. This guide makes restart explicit rather than claiming uninterrupted operation.

Use [official Git for Windows](https://git-scm.com/install/windows) and [uv installation guidance](https://docs.astral.sh/uv/getting-started/installation/). Per-user or portable installs avoid changing system Python. Retain installer version and checksum provenance privately.
