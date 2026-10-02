# Jobs independent of the SSH terminal

Task Scheduler owns the process. The wrapper executes the selected Python script in that same process, captures logs, and records script/manifest hashes. This avoids claiming that `Start-Process` or a closed browser demonstrates persistence.

Tasks use the current account with **S4U**, limited privileges, no triggers, unlimited execution time, and `IgnoreNew` for overlapping starts. No Windows password is put in a file. Microsoft's [S4U documentation](https://learn.microsoft.com/en-us/windows/win32/taskschd/principal-logontype) notes restrictions on network resources and encrypted files. Do not assume access to mapped drives, Windows-authenticated shares, or credentials protected for an interactive session. Validate the exact workload's needs; an alternate secure logon method may require the owner to enter credentials locally.

The scripts register tasks only when explicitly invoked. They do not run anything at boot. Keep manifests and scripts trusted: changing a manifest changes the code executed as that user.

## Register the synthetic demonstration

From the checkout root in PowerShell, after [initialization](jupyter.md):

```powershell
$python = (Resolve-Path .\environment\.venv\Scripts\python.exe).Path
$state = Join-Path (Get-Location) '.local\checkpoint.json'
@('--state', $state, '--steps', '300', '--delay', '2') |
  ConvertTo-Json | Set-Content .\.local\test-args.json -Encoding UTF8
.\scripts\Register-Task.ps1 -Name SyntheticProgress -Python $python `
  -Script .\examples\checkpoint_job.py -WorkingDirectory (Get-Location).Path `
  -ArgumentsFile .\.local\test-args.json
Start-ScheduledTask -TaskPath '\MacWindowsGPU\' -TaskName SyntheticProgress
```

The task performs about ten minutes of small integer work and atomic checkpoint writes. It is not a benchmark or scientific dataset. Do not start the same checkpoint through multiple tasks or manual processes: it is a **single-writer** example. Task Scheduler's `IgnoreNew` only prevents duplicate starts of that same registered task.

Inspect progress without displaying unrelated logs:

```powershell
Get-ScheduledTask -TaskPath '\MacWindowsGPU\' -TaskName SyntheticProgress
Get-ScheduledTaskInfo -TaskPath '\MacWindowsGPU\' -TaskName SyntheticProgress
$state = Get-Content .\.local\checkpoint.json -Raw | ConvertFrom-Json
$state.steps.Count
$state.sessions | Select-Object -Last 1
```

## Disconnect test: requires the Mac

Record the current step and PID. Close **all Mac SSH sessions and tunnels** while the task is running; wait at least 20 seconds, reconnect, and record progress again. A PASS requires more completed steps and the same running PID, with the task still active. If it finished, inspect recorded progress/timestamps and repeat with a longer duration if necessary. Local checks or owner assertions about a different SSH test are not substitutes.

Jupyter needs its own check: start it as a task, disconnect, reconnect and recreate the tunnel, then confirm the same server process and working notebook access.

## Stop and resume: a separate test

```powershell
Stop-ScheduledTask -TaskPath '\MacWindowsGPU\' -TaskName SyntheticProgress
# Wait until task state is Ready; then record the completed steps.
Copy-Item .\.local\checkpoint.json .\.local\before-resume.json
Start-ScheduledTask -TaskPath '\MacWindowsGPU\' -TaskName SyntheticProgress
```

After more steps appear, compare the old completed prefix with the new one. The next session must record `resume_after` equal to the old count, and IDs must remain exactly `1..N` with value `step**2`. The test refuses inconsistent checkpoints or a changed target. After a forced stop, the saved status field can still say `running`; Task Scheduler is authoritative for current process state.

Atomic replacement prevents a partial JSON write from replacing the previous checkpoint. A stop between calculation and save can repeat that uncommitted calculation; this example promises no duplicated **committed steps**, not universal exactly-once external side effects or power-loss-proof storage.

On Windows, a reader or scanner can briefly prevent replacement. The example retries known sharing/access errors up to 20 times, waiting 50 ms between attempts. Persistent denial still fails and leaves the previous checkpoint intact; it does not delete the destination or silently discard the error.

## Your own job

Create an ignored arguments JSON array and register a new unique task name with your project's exact Python, script, and working directory. Do not pass secrets as command-line arguments. `-WhatIf` previews registration. Existing task names and run directories are refused to protect work. Inspect errors and partial directories before retrying.

Use `Start-ScheduledTask`, `Stop-ScheduledTask`, and the status commands above with your name. Logs live under `.local/runs/<name>/job.log`; they can contain application output and must remain private. The wrapper does **not** add checkpoint support to arbitrary code, pin mutable source code, or make subprocess trees durable. Your application must handle recovery, child processes, and artifact integrity explicitly.

After cold boot, reconnect by SSH and start Jupyter/the desired job on demand. Processes do not survive reboot. Restarting the demonstration reads saved progress; test the same behavior for each real application before trusting it remotely.
