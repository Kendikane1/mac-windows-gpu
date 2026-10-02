[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Project,
    [Parameter(Mandatory=$true)][string]$Python,
    [ValidateRange(1024,65535)][int]$Port = 8888
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
$local = Join-Path $repo '.local'
if (Test-Path -LiteralPath $local) { throw '.local exists; inspect it instead of overwriting.' }
$resolvedProject = (Resolve-Path -LiteralPath $Project).Path
$resolvedPython = (Resolve-Path -LiteralPath $Python).Path
if (-not (Test-Path -LiteralPath $resolvedProject -PathType Container)) { throw 'Project must be a directory.' }
if (-not (Test-Path -LiteralPath $resolvedPython -PathType Leaf)) { throw 'Python must be a file.' }
New-Item -ItemType Directory -Path $local | Out-Null
# Establish a protected ACL before writing any runtime configuration.
$sid = [Security.Principal.WindowsIdentity]::GetCurrent().User
$acl = New-Object Security.AccessControl.DirectorySecurity
$acl.SetOwner($sid)
$acl.SetAccessRuleProtection($true, $false)
foreach ($allowed in @($sid.Value, 'S-1-5-18', 'S-1-5-32-544')) {
    $identity = New-Object Security.Principal.SecurityIdentifier($allowed)
    $rule = New-Object Security.AccessControl.FileSystemAccessRule(
        $identity, 'FullControl', 'ContainerInherit,ObjectInherit', 'None', 'Allow'
    )
    $acl.AddAccessRule($rule)
}
Set-Acl -LiteralPath $local -AclObject $acl
foreach ($name in @('runtime','config','data','runs')) {
    New-Item -ItemType Directory -Path (Join-Path $local $name) | Out-Null
}
@{ project=$resolvedProject; python=$resolvedPython; port=$Port } |
    ConvertTo-Json | Set-Content -LiteralPath (Join-Path $local 'settings.json') -Encoding UTF8
Write-Output 'Private local settings created; no service or task started.'
