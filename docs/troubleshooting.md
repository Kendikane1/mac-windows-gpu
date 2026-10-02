# Troubleshooting and rollback

| Symptom | Smallest useful check |
| --- | --- |
| SSH times out | Is Windows awake? Tailscale connected/unattended? Device key valid? Correct firewall source/destination and tailnet policy? |
| SSH rejects a key | Correct Windows account and actual authorized_keys path? Administrator match block? Restrictive ACL? |
| Changed host-key warning | Verify Windows-side fingerprint through trusted local access; do not bypass checking |
| `torch.cuda.is_available()` false | Print interpreter path, PyTorch version/build and `torch.version.cuda`; inspect driver and Windows CUDA source |
| Environment install fails | Disk headroom, supported Python/architecture, official index reachability, unchanged lock |
| Task registration denied | Intended account, normal UAC, local task permissions; never switch to SYSTEM as a workaround |
| Task exits immediately | `Get-ScheduledTaskInfo`, private `.local/runs/<name>/job.log`, absolute Python/script paths |
| Task Ready but checkpoint says running | A forced stop leaves stale application status; Task Scheduler is authoritative |
| Jupyter cannot start | Port already occupied, wrong configured interpreter, missing environment, private runtime ACL |
| Browser cannot connect | Tunnel still running? Correct Mac-local port? Windows listener really loopback? |
| Jupyter rejects token | Server restarted? Retrieve the new token privately; do not disable authentication |
| Resume refuses checkpoint | Changed target or corrupt/non-contiguous steps; preserve it for diagnosis, do not silently reset |
| Mapped drives/Windows credentials fail in a task | S4U restrictions; use local storage or plan a suitable secure logon method |

For PowerShell scripts blocked by policy, follow your organization's approved execution/signing process. Do not disable safeguards globally. Review downloaded code before any unblock action.

## Remove this guide's tasks

First stop your workloads and save their state. From PowerShell:

```powershell
# Graceful Jupyter shutdown first, if it is running:
& .\environment\.venv\Scripts\python.exe .\scripts\jupyter_control.py stop
# Stop only the tasks you registered with this guide:
Stop-ScheduledTask -TaskPath '\MacWindowsGPU\' -TaskName SyntheticProgress
Unregister-ScheduledTask -TaskPath '\MacWindowsGPU\' -TaskName SyntheticProgress
Unregister-ScheduledTask -TaskPath '\MacWindowsGPU\' -TaskName Jupyter
```

Confirm names before approving deletion. Repeat for your own added tasks only. Keep checkpoints and logs until no longer needed. Deleting the checkout alone does not remove tasks. Remove the environment and private runtime directory only after verifying their absolute paths and that no process uses them. Do not delete the shared uv cache or another project's environment as part of this cleanup.

Initialization changes only this checkout's `.local` tree. Kernel installation with `--prefix` stays inside its environment. No global Python changes or automatic boot triggers are required.

## Remote-access rollback is separate

If SSH/Tailscale existed beforehand, preserve them. If you created a new SSH rule or changed authentication, use your private before-change notes to reverse only those changes, with local recovery available. Do not blindly re-enable a broad firewall rule. Disabling sshd, deleting the authorized key, or signing Tailscale out can terminate your access; coordinate first.

For a broken environment, retain its lock and any outputs before rebuilding `.venv`. For a failed task registration that left a run directory, inspect it before removing or renaming it and retrying. For a task you intend to replace, export its definition privately, unregister that exact task, and register the reviewed replacement explicitly.
