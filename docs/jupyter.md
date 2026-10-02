# Authenticated Jupyter through SSH

Use PowerShell in the checkout root. Finish the environment and SSH checks first. The commands use this checkout's environment; substitute the verified interpreter of your own project if adapting the helpers.

## Private configuration and kernel

```powershell
$python = (Resolve-Path .\environment\.venv\Scripts\python.exe).Path
.\scripts\Initialize-Local.ps1 -Project (Get-Location).Path -Python $python -Port 8888
& $python -m ipykernel install --prefix .\environment\.venv `
  --name mac-windows-gpu --display-name 'Windows GPU (Python 3.12)'
```

Initialization creates a protected, ignored `.local/` tree. It refuses to overwrite existing settings. Run it as the intended account, not a different administrator. Review `.local/settings.json` privately. Keep all code/runtime files on a local non-synced volume. The kernel specification records the environment's absolute Python path, so recreate it after moving or rebuilding the environment.

## Register and start

```powershell
.\scripts\Register-Task.ps1 -Name Jupyter -Python $python `
  -Script .\scripts\jupyter_launcher.py -WorkingDirectory (Get-Location).Path
Start-ScheduledTask -TaskPath '\MacWindowsGPU\' -TaskName Jupyter
Get-ScheduledTask -TaskPath '\MacWindowsGPU\' -TaskName Jupyter
Get-ScheduledTaskInfo -TaskPath '\MacWindowsGPU\' -TaskName Jupyter
& $python .\scripts\jupyter_control.py status
Get-NetTCPConnection -State Listen -LocalPort 8888 | Select-Object LocalAddress, LocalPort
```

Expected listener: **127.0.0.1:8888 only**. A task being Running does not alone prove an HTTP server is ready; retry status briefly while it initializes. A port conflict fails instead of silently choosing another port. The launcher uses a fresh token and does not open a Windows browser. [Jupyter security documentation](https://jupyter-server.readthedocs.io/en/latest/operators/security.html) explains token authentication and its arbitrary-code-execution implications.

If task registration is denied, use normal UAC as the **same Windows account** and retry after inspecting any partial `.local/runs/Jupyter` directory. Do not switch to SYSTEM, weaken execution policy, or save a password in a script. See [task limitations](background-jobs.md).

## Mac tunnel

Use the private `windows-gpu` SSH host entry from [remote access](remote-access.md). It retains the dedicated identity, account, and strict host-key checking:

```sh
ssh -N -T -o ExitOnForwardFailure=yes \
  -L 127.0.0.1:8888:127.0.0.1:8888 windows-gpu
```

Leave this tunnel running and open **http://127.0.0.1:8888/lab** on the Mac. If Mac port 8888 is occupied, use `-L 127.0.0.1:8889:127.0.0.1:8888` and browse port 8889 instead. No Windows firewall rule for Jupyter is needed.

In a separate trusted SSH window, enter PowerShell, change to the checkout, and retrieve the token privately:

```powershell
& .\environment\.venv\Scripts\python.exe .\scripts\jupyter_control.py token
```

Paste it in Jupyter's login field. Never send it to an issue, assistant transcript, report, or reusable command file. Runtime JSON contains the token by design; it stays under protected `.local/runtime`. Each server restart changes the token.

## Verify and stop

Open `examples/kernel-check.ipynb`, select **Windows GPU (Python 3.12)**, and run it. Confirm `sys.executable` matches the Windows project environment. This verifies the Mac browser path only when actually performed on the Mac; a locally executed notebook is a separate check. Clear notebook outputs before committing.

Stop gracefully:

```powershell
& .\environment\.venv\Scripts\python.exe .\scripts\jupyter_control.py stop
Get-ScheduledTask -TaskPath '\MacWindowsGPU\' -TaskName Jupyter
```

Confirm the task returns to Ready and the listener disappears. If graceful shutdown fails, inspect the private job log before using `Stop-ScheduledTask`; forced termination can interrupt running notebook cells. Closing the browser or SSH tunnel is not a server shutdown. For long recoverable work, use a checkpoint-aware script rather than relying on an unsaved notebook cell.
