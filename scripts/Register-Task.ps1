[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Za-z0-9_-]+$')][string]$Name,
    [Parameter(Mandatory=$true)][string]$Python,
    [Parameter(Mandatory=$true)][string]$Script,
    [Parameter(Mandatory=$true)][string]$WorkingDirectory,
    [string]$ArgumentsFile
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$local = Join-Path $repo '.local'
if (-not (Test-Path -LiteralPath (Join-Path $local 'settings.json'))) { throw 'Initialize local settings first.' }
$taskPath = '\MacWindowsGPU\'
if (Get-ScheduledTask -TaskPath $taskPath -TaskName $Name -ErrorAction SilentlyContinue) {
    throw 'Task exists; refusing overwrite.'
}
$resolvedPython = (Resolve-Path -LiteralPath $Python).Path
$resolvedScript = (Resolve-Path -LiteralPath $Script).Path
$resolvedDirectory = (Resolve-Path -LiteralPath $WorkingDirectory).Path
foreach ($file in @($resolvedPython, $resolvedScript)) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw 'Expected a file path.' }
}
if (-not (Test-Path -LiteralPath $resolvedDirectory -PathType Container)) { throw 'Expected working directory.' }
$jobArgs = @()
if ($ArgumentsFile) {
    $raw = Get-Content -LiteralPath $ArgumentsFile -Raw
    if (-not $raw.TrimStart().StartsWith('[')) { throw 'Arguments file must be a JSON array.' }
    $jobArgs = @($raw | ConvertFrom-Json)
    if (@($jobArgs | Where-Object { $_ -isnot [string] }).Count) { throw 'Arguments must be strings.' }
}
$jobDirectory = Join-Path $local ('runs\' + $Name)
if (Test-Path -LiteralPath $jobDirectory) { throw 'Job directory exists; inspect before reuse.' }
$manifestPath = Join-Path $jobDirectory 'manifest.json'
$runner = Join-Path $PSScriptRoot 'run_job.py'
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-ScheduledTaskPrincipal -UserId $identity.User.Value -LogonType S4U -RunLevel Limited
$action = New-ScheduledTaskAction -Execute $resolvedPython `
    -Argument ('-u "' + $runner + '" "' + $manifestPath + '"') -WorkingDirectory $resolvedDirectory
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -MultipleInstances IgnoreNew -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
if ($PSCmdlet.ShouldProcess(($taskPath + $Name), 'Register on-demand limited-user S4U task')) {
    New-Item -ItemType Directory -Path $jobDirectory | Out-Null
    @{ script=$resolvedScript; args=@($jobArgs); cwd=$resolvedDirectory; log=(Join-Path $jobDirectory 'job.log') } |
        ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
    Register-ScheduledTask -TaskPath $taskPath -TaskName $Name -Action $action `
        -Principal $principal -Settings $settings -Description 'On-demand Python; no boot trigger; application checkpoints required.' | Out-Null
    # Default owner task permissions; no broad ACL changes or elevated run level.
    Write-Output ('Registered ' + $taskPath + $Name + '; not started.')
}
