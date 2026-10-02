# Reference results and limits

## Original workstation: 2026-09-13

The private deployment report recorded Windows 11 Home, Ryzen 5 5500, about 8 GB system RAM, RTX 4060 with 8,188 MiB VRAM, and NVIDIA driver 591.86. The setup used native Windows, Python 3.12.14, uv 0.12.13, Git 2.55.0.windows.5, torch 2.13.0+cu130, JupyterLab 4.6.3, and ipykernel 7.3.0.

| Check | Outcome recorded at the time |
| --- | --- |
| Tiny CUDA matrix calculation | PASS; 64×64 float64, rtol/atol 1e-10, maximum absolute error 7.105427357601002e-15 |
| GPU allocator memory | 8.21875 MiB allocated/peak; 22 MiB reserved; excludes context/other processes |
| Original scientific repo checks | PASS: sync, 14 tests, lint, format, type check, synthetic smoke |
| Locally authenticated loopback Jupyter | PASS |
| Notebook executed under the scheduled identity | PASS locally |
| Deliberate synthetic scheduled stop/resume | PASS, preserved committed prefix |
| SSH hotspot/sign-out/cold boot | PASS, owner-reported |
| Mac Jupyter browser connection | NOT TESTED at that handoff |
| Actual Mac-disconnect job persistence | NOT TESTED at that handoff |
| Real research application recovery | NOT TESTED |

These are dated observations, not a statement about the workstation's present state. The public guide excludes its account names, addresses, keys, machine paths, raw logs, task exports, and research outputs.

## Generalized repository: 2026-10-02

The helper code here is adapted and parameterized. Historical deployment success does not automatically transfer to the adapted code. See `publication-checks.md` for the actual source and synthetic test results obtained when preparing this repository.

The new environment is deliberately smaller than the scientific project: torch, JupyterLab, and ipykernel only. A newly generated lock is reviewed separately; no scientific repository lock or source files are changed by creating this guide.

The included task and Jupyter examples still require a real deployment test with the selected user and a Mac. CI uses no GPU and does not modify Windows services or create scheduled tasks. Treat instructions and unexecuted integration paths as NOT TESTED rather than converting the historical results into claims about new code.
