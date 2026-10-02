# Checks performed for this repository

Date: **2026-10-02**. Native Windows, Python 3.12.14, uv 0.12.13.

| Check | Result | Limits |
| --- | --- | --- |
| Standard-library suite | PASS, 8 tests | Synthetic subprocesses and static/source checks |
| Forced process stop/resume | PASS | Committed prefix preserved; not a Mac disconnect or reboot |
| Corrupt/changed checkpoint rejection | PASS | No silent reset |
| Wrapper argument boundaries / exit status | PASS | Paths with spaces, literal special characters, nonzero exit |
| Python and notebook code parsing | PASS | Does not import/install GPU packages |
| Notebook output hygiene | PASS | No execution results or personal executable paths stored |
| PowerShell parser | PASS, both scripts | Scripts parsed; task registration not executed |
| Universal uv lock | PASS, 102 package records resolved | Metadata resolution, not installation |
| Windows x64 locked dry run | PASS, 97 packages selected | torch 2.13.0+cu130 |
| Apple Silicon macOS 14 locked dry run | PASS, 98 packages selected | torch 2.13.0 from PyPI; no actual Mac execution |
| New minimal environment install/GPU run | NOT TESTED | Avoided a duplicate large installation; historical GPU evidence is separate |
| Generalized Jupyter/task live deployment | NOT TESTED | Existing private workstation services were preserved |
| Mac browser/disconnect tests of this checkout | NOT TESTED | Requires the Mac |
| Initial GitHub Actions run | FAIL | Windows file-access denial during checkpoint replacement; see follow-up below |

The current lock includes newer transitive versions than the historical workstation, including Jupyter Server 2.21.1. Do not claim that the historical GPU/Jupyter runtime tests validated this new resolved environment. Install and test it on the target machine before relying on it.

For repeatable dry runs, from the checkout root:

```powershell
uv sync --project .\environment --locked --dry-run
$env:MACOSX_DEPLOYMENT_TARGET = '14.0'
uv sync --project .\environment --locked --dry-run --python-platform aarch64-apple-darwin
Remove-Item Env:MACOSX_DEPLOYMENT_TARGET
```

Use a Python 3.12 interpreter. A dry run can fetch resolution metadata but does not install the environment. Documentation links point to official upstream guidance; upstream changes should trigger review rather than unrecorded configuration changes.

## Publication follow-up: 2026-10-03

The [first Windows CI run](https://github.com/Kendikane1/mac-windows-gpu/actions/runs/37036150684) found a transient `WinError 5` during checkpoint replacement while progress was being read. The follow-up adds bounded retries for Windows sharing/access errors, with regression tests for recovery and for persistent denial preserving the old checkpoint. The expanded local suite passes **10 tests**. Consult the [workflow runs](https://github.com/Kendikane1/mac-windows-gpu/actions/workflows/check.yml) for remote results on the exact commit you use; source tests still do not establish Mac connectivity or live task deployment.
