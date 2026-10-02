# Verification checklist

Record outcomes privately with date, relevant versions, and whether each result is locally observed or owner-reported. Never record tokens, key contents, account identifiers, or real network addresses in a public result.

| Check | PASS requires |
| --- | --- |
| Storage | Installation allowance plus operating headroom; recheck after installation |
| Tailscale unattended | Connected service and a later real sign-out/cold-boot SSH test |
| SSH firewall | Exact intended client/server scope; no broader effective SSH allow |
| Server identity | Mac fingerprint matched a trusted Windows-side fingerprint |
| Key-only authentication | Fresh connection after password authentication disabled |
| GPU | CUDA available, tiny synchronized multiplication matches CPU tolerance |
| Kernel | Notebook's Python equals the verified environment's interpreter |
| Jupyter boundary | Only 127.0.0.1 listener; authentication required |
| Mac notebook | Actual Mac tunnel, browser login, and synthetic cell execution |
| Background task | Correct user, limited privileges, S4U, no triggers, explicit start |
| Disconnect | Progress continues after all Mac SSH connections close |
| Application resume | Deliberate stop/restart preserves committed prefix without duplicates |
| Hotspot | Fresh connection from Mac on a different network |
| Sign-out | Remote connection works without an active Windows desktop session |
| Cold boot | Someone presses power; remote connection and on-demand task startup work without desktop login |

Do not sign out or reboot a shared PC without coordinating with its users. Test application recovery independently of the network path. A resumed checkpoint does not prove a live process survived a reboot.

## Local helper checks

```powershell
python -m unittest discover -s tests -v
```

The tests force-stop and resume a small synthetic subprocess, reject corrupted checkpoints and changed targets, check argument boundaries and exit codes, parse Python/notebook code, and validate local documentation links. They do not start services, authenticate a Mac, or test the generalized scheduled tasks.

For Jupyter, an unauthenticated request to `/api/contents` should be denied. The private `jupyter_control.py status` command checks that the runtime token authenticates successfully without displaying it. Check the actual listener independently with `Get-NetTCPConnection`. A task's status or a generated token alone proves neither boundary nor connectivity.

## Zed

Consult [current Zed remote-development requirements](https://zed.dev/docs/remote-development) before choosing an editor workflow. Check the installed Mac version, Windows host support, and Windows-side bootstrap requirements against that release. Keep the working SSH shell/authentication intact; do not change them simply to try an editor. This repository does not install Zed or claim a tested Zed session.
