# Contributing

Keep the guide incremental and distinguish a documented procedure from a test that actually ran. Use PASS, FAIL, or NOT TESTED with the platform/date and limits of the evidence.

Do not copy private deployment reports, task XML, runtime files, or logs into a pull request. New helpers must take paths/configuration as inputs rather than embedding an operator's identity or network addresses. Clear notebook outputs. Follow [SECURITY.md](SECURITY.md).

Run these checks using Python 3.12; they require no third-party libraries:

```powershell
python -m unittest discover -s tests -v
```

Parse PowerShell files as shown in `.github/workflows/check.yml`. Review the staged diff and all added paths. The synthetic tests use temporary files and subprocesses; they do not register tasks, alter SSH/firewall settings, or allocate GPU memory.

For dependency changes, review the universal lock and platform markers, then separately test a Windows CUDA computation. Document Mac dry-run resolution separately from actual Mac execution. Never run real experiments merely to test this guide.

Task, SSH, and notebook end-to-end tests need an explicit local recovery plan. CI is intentionally limited to source checks and synthetic subprocess recovery. It is not proof of unattended Windows login behavior.
