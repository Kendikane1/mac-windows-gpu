# Remote access before desktop login

Keep a local recovery path and a working SSH window throughout configuration. If access already works, inspect it and run the verification checklist instead of replacing it. System changes in this section require an elevated PowerShell window under normal UAC controls.

## 1. Tailscale

Install Tailscale on both devices, sign in to the intended tailnet, and confirm both devices are connected. Identify the Mac explicitly. On Windows, enable **Run unattended**, then inspect the Tailscale service's status and startup type. This enables operation without an interactive desktop session. See [Tailscale unattended mode](https://tailscale.com/docs/how-to/run-unattended).

```powershell
Get-Service Tailscale | Select-Object Status, StartType
tailscale status
tailscale ip -4
```

Keep device addresses and names in your private notes. Before travel, inspect device-key expiration in the Tailscale admin console. Expiration or revoked access can interrupt remote access; decide account policy deliberately. Do not silently disable expiration. A tailnet access policy must also permit the connection: a Windows firewall rule cannot override a Tailscale denial.

## 2. Inspect/install OpenSSH Server

OpenSSH **Client** alone is insufficient. Check capability state and pending installation before adding Server. Follow [Microsoft's installation guide](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse).

```powershell
Get-WindowsCapability -Online | Where-Object Name -like 'OpenSSH*'
# Only if Server is NotPresent and no installation is underway:
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Set-Service sshd -StartupType Automatic
```

For a new installation, restrict its firewall rule **before** starting sshd. For an existing running server, coordinate changes so the current connection remains recoverable.

## 3. Restrict the firewall

Inspect effective rules in `wf.msc`, including program/service rules that allow sshd, broad TCP rules, and `OpenSSH-Server-In-TCP`. Rules are additive: adding a narrow rule does not cancel an existing broad allow. Do not disable unrelated rules or the firewall.

For a fresh setup, this creates one IPv4 rule. Enter the exact addresses privately when prompted:

```powershell
$serverAddress = Read-Host 'Windows Tailscale IPv4 address'
$macAddress = Read-Host 'Mac Tailscale IPv4 address'
New-NetFirewallRule -Name 'MacWindowsGPU-SSH' `
  -DisplayName 'SSH from intended Mac over Tailscale' `
  -Direction Inbound -Action Allow -Protocol TCP -LocalPort 22 `
  -LocalAddress $serverAddress -RemoteAddress $macAddress -Profile Any
```

Once reviewed, disable the installer's broad allow if present:

```powershell
Get-NetFirewallRule -Name OpenSSH-Server-In-TCP -ErrorAction SilentlyContinue |
  Disable-NetFirewallRule
Get-NetFirewallRule -Name MacWindowsGPU-SSH | Get-NetFirewallAddressFilter
```

If another rule allows wider SSH, narrow that SSH-specific rule too. A managed policy you cannot edit needs the administrator's help. Use the IPv4 address in the client configuration for this example. Do not assume an unreviewed IPv6 rule is harmless. Do not open router ports, Jupyter ports, or Tailscale Funnel.

## 4. Key authentication

On the Mac, generate a dedicated key in a newly created directory; this cannot overwrite an existing key. Set a passphrase when prompted.

```sh
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"
keydir=$(mktemp -d "$HOME/.ssh/windows-gpu.XXXXXXXX")
ssh-keygen -t ed25519 -f "$keydir/id_ed25519" -C mac-windows-gpu
printf 'IdentityFile: %s\n' "$keydir/id_ed25519"
cat "$keydir/id_ed25519.pub"
```

Transfer only the `.pub` line. Standard accounts normally use `%USERPROFILE%\.ssh\authorized_keys`; the default administrator match block instead uses `%ProgramData%\ssh\administrators_authorized_keys`. Read the actual `sshd_config` first. Preserve existing authorized keys. Administrator keys are shared by the administrator match configuration; prefer a dedicated standard account when appropriate.

Microsoft requires the administrator key file to be accessible only to Administrators and SYSTEM. After backing up its existing ACL, use the documented permissions (SIDs avoid localized group names):

```powershell
icacls.exe "$env:ProgramData\ssh\administrators_authorized_keys" /inheritance:r
icacls.exe "$env:ProgramData\ssh\administrators_authorized_keys" /grant:r '*S-1-5-32-544:F' '*S-1-5-18:F'
icacls.exe "$env:ProgramData\ssh\administrators_authorized_keys"
```

Review and remove any remaining inappropriate explicit grants individually; `/grant:r` is not a blanket removal of all other principals. For standard-account key permissions, follow [Microsoft key management](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_keymanagement).

## 5. Verify identity and then remove password login

Validate the configuration before starting or restarting:

```powershell
& "$env:WINDIR\System32\OpenSSH\sshd.exe" -t
# Stop here if validation failed.
Start-Service sshd
ssh-keygen -lf "$env:ProgramData\ssh\ssh_host_ed25519_key.pub"
```

Compare that fingerprint through a trusted channel at the Mac's first connection. Never accept a changed key merely to dismiss a warning. Use the correct Windows username, including quotes when it contains spaces. Keep the resulting connection open.

After a **fresh key-only login works**, back up `%ProgramData%\ssh\sshd_config`. Set these in its global section, before any `Match` blocks:

```text
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
```

Run `sshd -t` again and inspect applicable match settings. Restart sshd only with the recovery session/local help available. Open another fresh connection forcing key authentication; do not infer success from an already-open window. See [Microsoft server configuration](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh-server-configuration).

## Private Mac configuration

Create a host entry in `~/.ssh/config`, replacing placeholders privately:

```sshconfig
Host windows-gpu
    HostName WINDOWS_TAILSCALE_IPV4
    User "WINDOWS_USERNAME"
    IdentityFile /absolute/path/to/dedicated/id_ed25519
    IdentitiesOnly yes
    PasswordAuthentication no
    HostKeyAlgorithms ssh-ed25519
    StrictHostKeyChecking yes
```

For the **first verified enrollment only**, use `ssh -o StrictHostKeyChecking=ask windows-gpu`, compare the fingerprint, and accept only a match. Later use `ssh windows-gpu`. Do not use `StrictHostKeyChecking=no`, or treat `ssh-keyscan` alone as identity verification.

Before travel, test SSH from a phone hotspot, after Windows sign-out, and after cold boot without a desktop login. Coordinate these tests with anyone using the PC.
