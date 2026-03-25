from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime, timezone

app = FastAPI(title="IT Helpdesk API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class Message(BaseModel):
    id: str
    sender: str
    sender_type: str  # "user", "agent", "system"
    content: str
    timestamp: str


class Ticket(BaseModel):
    id: str
    title: str
    description: str
    category: str   # Network, Software, Hardware, Security, Access, Other
    priority: str   # Low, Medium, High, Critical
    status: str     # Open, In Progress, Resolved, Closed
    assigned_team: str
    assigned_agent: str
    created_at: str
    messages: List[Message]


# ---------------------------------------------------------------------------
# Request Bodies
# ---------------------------------------------------------------------------

class CreateTicketBody(BaseModel):
    title: str
    description: str
    category: str
    priority: str


class UpdateStatusBody(BaseModel):
    status: str


class SendMessageBody(BaseModel):
    content: str


# ---------------------------------------------------------------------------
# Knowledge Articles
# ---------------------------------------------------------------------------

KNOWLEDGE_ARTICLES = {
    "Network": [
        {
            "id": "KB-N001",
            "title": "How to reset your network adapter",
            "summary": "Step-by-step guide to reset your network adapter on Windows and Mac to resolve connectivity issues.",
            "content": """# How to Reset Your Network Adapter

Resetting your network adapter can resolve many connectivity issues including dropped connections, limited connectivity, and inability to obtain an IP address.

## Windows

1. Right-click the Start button and select **Device Manager**.
2. Expand **Network adapters**.
3. Right-click your adapter and select **Disable device**, then **Enable device**.

**Alternative — Command Prompt (run as Administrator):**
```
netsh winsock reset
netsh int ip reset
ipconfig /release
ipconfig /flushdns
ipconfig /renew
```
Restart your computer after running these commands.

## Mac

1. Open **System Settings** → **Network**.
2. Select your network interface and click the **–** button to remove it.
3. Click **+** to add it back, then reconnect.

**Alternative — Terminal:**
```bash
sudo ifconfig en0 down
sudo ifconfig en0 up
```

## When to Contact IT

If the issue persists after resetting, it may be a hardware fault or a network infrastructure problem. Submit a ticket with category **Network** and priority **High**.
"""
        },
        {
            "id": "KB-N002",
            "title": "VPN connection troubleshooting",
            "summary": "Common VPN errors and how to fix them, including authentication failures and timeout issues.",
            "content": """# VPN Connection Troubleshooting

## Common Errors

### Authentication Failed
- Verify your username and password are correct.
- Ensure your Active Directory password has not expired (try logging into your work PC first).
- If using MFA, confirm the push notification or code is entered within the time limit.

### Timeout / No Response
- Check your internet connection by visiting a public website.
- Disable any third-party firewall or antivirus temporarily to test.
- Try connecting from a different network (e.g., mobile hotspot).

### Connected but No Access
- Disconnect and reconnect to the VPN.
- Run `ipconfig /flushdns` (Windows) or `sudo dscacheutil -flushcache` (Mac).
- Ensure you are connecting to the correct VPN server (check the VPN client profile).

## Supported VPN Clients

| Client | Version |
|--------|---------|
| Cisco AnyConnect | 4.10+ |
| GlobalProtect | 5.2+ |

## Still Not Working?

Submit a helpdesk ticket with:
- VPN client name and version
- Exact error message
- Screenshot if possible
"""
        },
        {
            "id": "KB-N003",
            "title": "WiFi not connecting — quick fixes",
            "summary": "Checklist of steps to resolve WiFi connectivity issues including DNS flush and IP renewal.",
            "content": """# WiFi Not Connecting — Quick Fixes

## Step-by-Step Checklist

1. **Toggle WiFi off and on** — Use the WiFi icon in the taskbar/menu bar.
2. **Forget and reconnect** — Remove the saved network and reconnect with fresh credentials.
3. **Restart your router** — Unplug for 30 seconds, plug back in, wait 2 minutes.
4. **Renew your IP address (Windows):**
   ```
   ipconfig /release
   ipconfig /renew
   ipconfig /flushdns
   ```
5. **Check for interference** — Move closer to the access point. Microwaves and cordless phones can interfere with 2.4 GHz.
6. **Try 5 GHz band** — If your router broadcasts separate SSIDs (e.g., `Corp-5G`), try that one.
7. **Update network drivers** — Go to Device Manager → Network Adapters → Update driver.
8. **Check if others are affected** — If multiple users are impacted, report to IT immediately as it may be an infrastructure issue.

## If None of the Above Work

Submit a ticket with:
- Device make/model
- OS version
- SSID you are trying to connect to
- Whether other devices on the same network work
"""
        },
        {
            "id": "KB-N004",
            "title": "How to check network speed and latency",
            "summary": "Tools and steps to diagnose slow network performance and identify bottlenecks.",
            "content": """# How to Check Network Speed and Latency

## Speed Test

Use an approved internal speed test or ask IT for the URL. Record:
- **Download speed** (target: ≥ 50 Mbps on wired)
- **Upload speed** (target: ≥ 10 Mbps)
- **Latency / Ping** (target: < 20 ms on LAN, < 80 ms over VPN)

## Latency Test (Command Line)

**Windows:**
```
ping 8.8.8.8 -n 20
tracert 8.8.8.8
```

**Mac/Linux:**
```bash
ping -c 20 8.8.8.8
traceroute 8.8.8.8
```

## What to Look For

| Metric | Good | Problem |
|--------|------|---------|
| Ping | < 20 ms (LAN) | > 100 ms |
| Packet loss | 0% | > 1% |
| Jitter | < 5 ms | > 20 ms |

High jitter or packet loss usually indicates a hardware fault (cable, NIC, or switch port).

## Report to IT

Attach your `ping` and `tracert`/`traceroute` output when submitting a network performance ticket.
"""
        },
    ],
    "Software": [
        {
            "id": "KB-S001",
            "title": "Clearing application cache on Windows",
            "summary": "How to clear cache for common business applications to resolve crashes and slow performance.",
            "content": """# Clearing Application Cache on Windows

Stale cache files can cause applications to crash, freeze, or display outdated data.

## General Steps

1. Close the application completely (check the system tray).
2. Press **Win + R**, type `%appdata%`, press Enter.
3. Find the folder for your application and delete the `Cache` subfolder.
4. Reopen the application.

## Application-Specific

### Microsoft Teams
```
%appdata%\\Microsoft\\Teams\\Cache
%appdata%\\Microsoft\\Teams\\blob_storage
%appdata%\\Microsoft\\Teams\\databases
```
Delete all files in these folders, then restart Teams.

### Google Chrome
1. Press **Ctrl + Shift + Delete**.
2. Set time range to **All time**.
3. Check **Cached images and files**.
4. Click **Clear data**.

### Outlook
1. Close Outlook.
2. Navigate to `%localappdata%\\Microsoft\\Outlook`.
3. Delete files with `.ost` extension (they will be rebuilt on next launch — this may take time on large mailboxes).

## Warning

Do not delete files you are unsure about. If in doubt, submit a ticket and an agent will assist remotely.
"""
        },
        {
            "id": "KB-S002",
            "title": "Software installation fails — common causes",
            "summary": "Troubleshoot failed software installations including permission errors and missing dependencies.",
            "content": """# Software Installation Fails — Common Causes

## Error: "You don't have permission to install"

- You need local administrator rights. Contact IT to install approved software.
- Use the **Self-Service Portal** for pre-approved software that can be installed without admin rights.

## Error: "Missing prerequisite" or "Dependency not found"

- Install the required runtime first (e.g., .NET Framework, Visual C++ Redistributable).
- Download from Microsoft's official site or the Self-Service Portal.

## Error: "Installation package corrupt"

- Delete the downloaded installer and re-download from the official source.
- Verify the SHA256 checksum if provided.

## Error: "Another installation is in progress"

- Wait 5 minutes and retry.
- Restart the Windows Installer service: `net stop msiserver && net start msiserver` (Admin CMD).

## Error: Installer hangs

1. Open Task Manager → Details tab.
2. End `msiexec.exe` processes.
3. Retry the installation.

## Still Failing?

Submit a ticket with:
- Application name and version
- Full error message (screenshot preferred)
- Whether you have local admin rights
"""
        },
        {
            "id": "KB-S003",
            "title": "Microsoft Office not responding",
            "summary": "Steps to fix Office apps freezing or crashing, including repair tool usage and safe mode startup.",
            "content": """# Microsoft Office Not Responding

## Quick Fixes

1. **Wait** — Office may be processing a large file. Give it 60 seconds.
2. **Force quit** — Press **Ctrl + Alt + Delete** → Task Manager → End Task on the Office app.
3. **Reopen** — If Office crashed, it will offer to recover your document.

## Safe Mode Test

Run Office in safe mode to check if an add-in is causing the issue:
```
winword /safe      (Word)
excel /safe        (Excel)
powerpnt /safe     (PowerPoint)
```
If it works in safe mode, an add-in is the culprit. Go to **File → Options → Add-ins** and disable them one by one.

## Repair Office

1. Open **Control Panel** → **Programs and Features**.
2. Select **Microsoft 365** (or Office 20xx).
3. Click **Change** → **Quick Repair** (runs offline).
4. If Quick Repair fails, choose **Online Repair** (requires internet, takes ~20 min).

## Clear Office Cache

```
%localappdata%\\Microsoft\\Office\\16.0\\OfficeFileCache
```
Delete all files in this folder, then restart Office.

## When to Escalate

If Office crashes immediately on launch even after repair, submit a ticket. Include:
- Office version (File → Account → About)
- Windows version
- Whether the issue is on one file or all files
"""
        },
        {
            "id": "KB-S004",
            "title": "How to roll back a recent software update",
            "summary": "Instructions for reverting to a previous version if a new update caused issues.",
            "content": """# How to Roll Back a Recent Software Update

## Windows Updates

1. Open **Settings** → **Windows Update** → **Update History**.
2. Click **Uninstall updates**.
3. Find the problematic update (sorted by date), right-click → **Uninstall**.
4. Restart your computer.

Note: Not all Windows updates can be uninstalled.

## Microsoft Office Updates

1. Open any Office app → **File** → **Account**.
2. Click **Update Options** → **Disable Updates** (prevents further updates first).
3. To revert: Office doesn't natively downgrade — contact IT for deployment of a specific version via SCCM/Intune.

## Third-Party Applications

Most apps don't support rollback natively. Options:
- Check if the vendor provides older installers on their website.
- Uninstall the current version and install the previous one.
- Restore from a system restore point (Windows):
  1. Search "Create a restore point" in Start.
  2. Click **System Restore** and follow the wizard.

## Before Rolling Back

Document the issue clearly (screenshots, error messages) and submit a ticket. IT may be able to push a hotfix or provide a targeted solution without a full rollback.
"""
        },
    ],
    "Hardware": [
        {
            "id": "KB-H001",
            "title": "Monitor not displaying — troubleshooting guide",
            "summary": "Diagnose and fix issues with monitors not turning on, showing no signal, or flickering.",
            "content": """# Monitor Not Displaying — Troubleshooting Guide

## No Power (Monitor Won't Turn On)

- Check the power cable is firmly connected at both ends.
- Try a different power outlet.
- Look for an indicator light on the monitor — if none, the monitor may be faulty.

## No Signal

1. Confirm the correct input source is selected (use the monitor's menu button: HDMI, DisplayPort, VGA).
2. Reseat the video cable at both the monitor and PC ends.
3. Try a different cable.
4. Try a different port on the PC (if you have a dedicated GPU, use its ports, not the motherboard's).
5. Connect the monitor to a different PC to isolate whether the issue is the monitor or the PC.

## Flickering / Distorted Image

- Update your graphics driver:
  - Right-click Desktop → **Display settings** → **Advanced display** → **Display adapter properties** → **Driver** tab → **Update Driver**.
- Check the cable for physical damage (kinks, bent pins).
- Try lowering the refresh rate: **Display settings** → **Advanced display** → **Choose a refresh rate**.

## Multiple Monitors

- Press **Win + P** to cycle through display modes (PC screen only, Duplicate, Extend, Second screen only).
- Right-click Desktop → **Display settings** → **Detect** if the second monitor isn't recognized.

## Submit a Ticket If

- Monitor makes clicking or burning smell.
- Dead pixels or permanent discoloration.
- Issue persists after all steps above.
"""
        },
        {
            "id": "KB-H002",
            "title": "Laptop keyboard keys not working",
            "summary": "Common fixes for unresponsive or stuck keyboard keys including driver reinstall steps.",
            "content": """# Laptop Keyboard Keys Not Working

## Basic Checks

- **Restart** the laptop — a simple reboot resolves many driver glitches.
- Check if **Filter Keys** or **Sticky Keys** are enabled: Settings → Accessibility → Keyboard → turn them off.
- Check if **Num Lock** is toggled on (affects number pad keys on some layouts).

## External Keyboard Test

Connect a USB or Bluetooth keyboard. If it works, the issue is with the built-in keyboard hardware or driver.

## Reinstall Keyboard Driver

1. Open **Device Manager** (right-click Start).
2. Expand **Keyboards**.
3. Right-click the keyboard device → **Uninstall device**.
4. Restart the laptop — Windows will reinstall the driver automatically.

## Physical Issues

- Inspect keys for debris. Use compressed air to blow out dust.
- For liquid damage: power off immediately, remove battery if possible, and contact IT — do not attempt to dry with heat.
- Keys that are physically broken (popped off, snapped mechanism) require hardware repair.

## BIOS Test

Boot into BIOS (usually F2 or Del at startup). If keys work in BIOS but not Windows, the issue is software/driver related. If keys don't work in BIOS either, it's a hardware fault.

## Contact IT For

- Physical key replacement
- Liquid damage assessment
- Keyboard replacement quote
"""
        },
        {
            "id": "KB-H003",
            "title": "Computer running slow — hardware checks",
            "summary": "How to check RAM, CPU, and storage health to identify hardware-related performance issues.",
            "content": """# Computer Running Slow — Hardware Checks

## Check CPU and RAM Usage

1. Press **Ctrl + Shift + Esc** to open Task Manager.
2. Click the **Performance** tab.
3. Check:
   - **CPU**: Sustained > 90% indicates a runaway process or underpowered hardware.
   - **Memory**: If usage is consistently > 85%, you may need more RAM.
   - **Disk**: 100% disk usage (especially on HDDs) causes severe slowdowns.

## Check Storage Health

**Windows (built-in):**
```
wmic diskdrive get model,status
```
A status of `OK` is expected. `Pred Fail` means imminent failure — back up immediately.

**Free tool:** CrystalDiskInfo (ask IT to install) shows S.M.A.R.T. data.

## Check for Thermal Throttling

If your CPU is overheating, it will reduce its speed to cool down:
- Listen for the fan running at full speed.
- Use HWMonitor (ask IT) to check CPU temperature. Over 90°C under normal load is a problem.
- Clean laptop vents with compressed air.

## RAM Test

Run Windows Memory Diagnostic:
1. Search "Windows Memory Diagnostic" in Start.
2. Restart now and check for problems.
3. Results appear after reboot in the notification area.

## When to Submit a Ticket

- Disk showing `Pred Fail` status — urgent, risk of data loss.
- Temperatures consistently over 90°C.
- RAM test reports errors.
- Performance has degraded significantly with no software explanation.
"""
        },
        {
            "id": "KB-H004",
            "title": "Printer not detected by computer",
            "summary": "Steps to troubleshoot printers that aren't recognized, including driver and port checks.",
            "content": """# Printer Not Detected by Computer

## Basic Checks

- Ensure the printer is powered on and not showing any error lights.
- For USB printers: try a different USB port on the PC; try a different USB cable.
- For network printers: confirm the printer's IP address hasn't changed (print a test page from the printer's control panel).

## Reinstall Printer Driver

1. Open **Settings** → **Bluetooth & devices** → **Printers & scanners**.
2. Find the printer, click it, and select **Remove device**.
3. Click **Add a printer or scanner** and follow the wizard.

For network printers, select "The printer that I want isn't listed" and enter the IP address manually.

## Check Print Spooler Service

A stuck spooler prevents all printing:
1. Open **Services** (search in Start).
2. Find **Print Spooler**, right-click → **Restart**.
3. Navigate to `C:\Windows\System32\spool\PRINTERS` and delete all files (not the folder).
4. Start the Print Spooler service again.

## Shared / Network Printer

- Ping the printer's IP: `ping 192.168.x.x` — if no response, the printer may be offline or on a different subnet.
- Verify you are connected to the corporate network or VPN (remote workers).
- Check if others in your area can print — may be a server-side queue issue.

## Contact IT If

- Printer shows error codes on its display.
- Driver installation fails repeatedly.
- You need a new printer or printer mapping added.
"""
        },
    ],
    "Security": [
        {
            "id": "KB-SEC001",
            "title": "What to do if you clicked a phishing link",
            "summary": "Immediate steps to take after clicking a suspicious link, including password resets and IT notification.",
            "content": """# What to Do If You Clicked a Phishing Link

**Act immediately.** The faster you respond, the better your chances of limiting damage.

## Step 1 — Disconnect from the Network

- Disable WiFi or unplug the Ethernet cable on the affected device.
- This stops malware from communicating with attackers or spreading.

## Step 2 — Report to IT Security Immediately

Call the IT Security hotline or submit a **Critical** priority ticket right now. Do not wait.

Provide:
- The link you clicked (copy it from your browser history — do not click again)
- What happened after clicking (did a page load? did anything download?)
- Time of the incident

## Step 3 — Change Your Passwords

From a **different, unaffected device**:
- Change your email password immediately.
- Change your Active Directory / Windows login password.
- Change passwords for any accounts you were logged into at the time.

## Step 4 — Do Not Use the Device

Leave the potentially compromised device powered on and disconnected. IT Security will need to forensically examine it.

## Step 5 — Watch for Suspicious Activity

Monitor your email for sent items you didn't send, and notify IT if you see anything unusual in your accounts.

## What IT Will Do

- Scan the device for malware.
- Review network logs for data exfiltration.
- Determine if credentials were harvested.
- Guide you through a full remediation.
"""
        },
        {
            "id": "KB-SEC002",
            "title": "How to report a suspicious email",
            "summary": "Step-by-step guide to reporting phishing and spam emails to the security team.",
            "content": """# How to Report a Suspicious Email

Never click links, download attachments, or reply to suspicious emails before reporting.

## Indicators of a Phishing Email

- Sender address doesn't match the display name or uses a lookalike domain.
- Urgent language: "Your account will be suspended in 24 hours."
- Unexpected attachments, especially `.zip`, `.exe`, `.docm`.
- Links that hover to a different URL than displayed.
- Poor grammar and unusual formatting.

## Reporting in Microsoft Outlook

1. Select the suspicious email (do not open attachments).
2. Click **Report Message** in the toolbar (Home tab).
3. Select **Phishing**.
4. Outlook forwards it to Microsoft and our security team automatically.

## If You Don't Have the Report Message Button

1. Forward the email **as an attachment** to `security@yourcompany.com`.
   - In Outlook: Home → More → Forward as Attachment.
2. Include any context (why it seems suspicious) in the forwarding email body.

## After Reporting

- Delete the email from your inbox and Deleted Items.
- If you clicked anything before reporting, follow the steps in **KB-SEC001**.

## False Positives

If you reported a legitimate email by mistake, don't worry — security staff review each report before taking action.
"""
        },
        {
            "id": "KB-SEC003",
            "title": "Setting up multi-factor authentication (MFA)",
            "summary": "How to enable and configure MFA for company accounts to improve account security.",
            "content": """# Setting Up Multi-Factor Authentication (MFA)

MFA adds a second verification step when you sign in, dramatically reducing the risk of account compromise even if your password is stolen.

## Supported MFA Methods (in order of preference)

1. **Authenticator App** (Microsoft Authenticator — recommended)
2. **FIDO2 Security Key** (hardware key, e.g. YubiKey)
3. **SMS code** (least secure — use only if no other option)

## Setup: Microsoft Authenticator App

1. Install **Microsoft Authenticator** from the App Store or Google Play.
2. On your computer, go to `https://aka.ms/mysecurityinfo`.
3. Sign in with your work account.
4. Click **Add sign-in method** → **Authenticator app**.
5. Follow the on-screen QR code scan instructions.
6. Test by signing out and back in — you should receive an approval push notification.

## Setup: SMS Code

1. Go to `https://aka.ms/mysecurityinfo`.
2. Click **Add sign-in method** → **Phone**.
3. Enter your mobile number and verify with the code sent to you.

## Troubleshooting

- **App not receiving push notifications**: Ensure notifications are enabled for the Authenticator app in phone settings.
- **Lost your phone**: Contact IT immediately to reset your MFA to a new device.
- **Code doesn't match**: Ensure your phone's time is set to automatic (time sync). TOTP codes are time-sensitive.

## Adding a Backup Method

Always add a backup MFA method (e.g., SMS as backup to authenticator app) so you aren't locked out if your primary method fails.
"""
        },
        {
            "id": "KB-SEC004",
            "title": "Malware detected on your device — next steps",
            "summary": "What to do when your antivirus detects malware, including isolation and remediation steps.",
            "content": """# Malware Detected on Your Device — Next Steps

## Immediate Actions

### 1. Do Not Dismiss the Alert

Read the full alert from your antivirus/EDR tool. Note:
- Malware name (e.g., `Trojan.GenericKD.xxx`)
- File path where it was found
- Action taken (quarantined, blocked, removed)

### 2. Disconnect from the Network

If the malware was not automatically quarantined/removed, disconnect immediately:
- Unplug Ethernet or disable WiFi.

### 3. Report to IT Security

Submit a **Critical** priority ticket or call the security hotline. Include:
- Screenshot of the antivirus alert
- Malware name and file path
- When you first noticed the alert

### 4. Do Not Attempt Self-Remediation

Do not try to manually delete malware files or run unauthorized removal tools. You may accidentally:
- Destroy forensic evidence needed for the investigation.
- Remove the wrong files and cause system damage.

## What IT Security Will Do

1. Remotely isolate the device if still networked.
2. Perform a full forensic scan.
3. Determine the infection vector (how it got in).
4. Remediate or reimage the device.
5. Check for lateral movement to other systems.

## After Remediation

- Change all passwords from a clean device.
- Review recent financial transactions if banking was performed on the infected device.
- Enable MFA on all accounts if not already done (see KB-SEC003).
"""
        },
    ],
    "Access": [
        {
            "id": "KB-A001",
            "title": "How to request access to a shared drive",
            "summary": "The process for requesting read or write access to shared network drives and folders.",
            "content": """# How to Request Access to a Shared Drive

## Before You Submit a Ticket

Confirm:
- The exact path of the shared drive or folder (e.g., `\\\\fileserver\\DepartmentShares\\Finance`).
- Whether you need **read-only** or **read/write** access.
- The name of your manager who can approve the request (all access changes require manager approval).

## How to Submit the Request

1. Create a new helpdesk ticket with category **Access** and priority **Medium** (or **High** if urgent).
2. In the description, include:
   - Your full name and employee ID
   - The exact share path
   - Access level required (read / read-write)
   - Business justification (why you need access)
   - Your manager's name and email

## Approval Process

1. IT Admin receives the ticket and routes it to your manager for approval.
2. Manager approves via email reply or the helpdesk portal.
3. IT Admin provisions access (typically within 1 business day of approval).
4. You receive a confirmation email.

## Temporary Access

If you need access for a limited time (e.g., for a project), note the end date in the ticket. IT will set an expiry on the access.

## Troubleshooting Existing Access

If you had access previously and it was revoked:
- Your account may have been moved to a different OU during a reorganization.
- Submit a ticket with the same details above and note "previously had access."
"""
        },
        {
            "id": "KB-A002",
            "title": "Resetting your Active Directory password",
            "summary": "Self-service and IT-assisted options for resetting your Windows domain password.",
            "content": """# Resetting Your Active Directory Password

## Self-Service Reset (Preferred)

If you enrolled in the Self-Service Password Reset (SSPR) portal:

1. Go to `https://passwordreset.microsoftonline.com`.
2. Enter your work email and complete the CAPTCHA.
3. Verify your identity using your registered MFA method.
4. Set a new password following the complexity requirements.

**Password requirements:**
- Minimum 12 characters
- At least one uppercase, one lowercase, one number, one symbol
- Cannot reuse the last 10 passwords

## Reset from the Windows Login Screen

If your password has expired, you may be prompted to change it at the Windows login screen:
- Press **Ctrl + Alt + Delete** → **Change a password**.

## IT-Assisted Reset

If you are locked out and cannot use SSPR:

1. Call the IT helpdesk or submit a ticket with category **Access** and priority **High**.
2. Verify your identity with your employee ID and answers to security questions.
3. IT will provide a temporary password valid for 24 hours — change it immediately on first login.

## After Resetting

Update saved passwords in:
- VPN client
- Email client (Outlook, Mail)
- Mobile devices syncing work email
- Any apps using SSO (the new password propagates automatically, but some cached credentials need updating)
"""
        },
        {
            "id": "KB-A003",
            "title": "Account locked out — how to unlock",
            "summary": "Steps to unlock your account after too many failed login attempts.",
            "content": """# Account Locked Out — How to Unlock

Active Directory accounts lock automatically after **5 failed login attempts** within 30 minutes.

## Why Did It Lock?

Common causes:
- Typing the wrong password too many times.
- An old password saved on a mobile device or app still trying to authenticate.
- A script or scheduled task using outdated credentials.

## Self-Unlock via SSPR

1. Wait 30 minutes — the lockout resets automatically.
2. Or go to `https://passwordreset.microsoftonline.com` and choose **Unlock my account** (if SSPR is enrolled).

## IT-Assisted Unlock

If you cannot wait or use SSPR:
1. Submit a ticket with category **Access** and priority **High**, or call the helpdesk directly.
2. IT can unlock the account in Active Directory within minutes.

## Preventing Future Lockouts

After unlocking, check all devices that sync your work account:
- **Smartphones**: Settings → Accounts → your work account → update credentials.
- **Outlook on mobile**: re-enter your password in the mail app settings.
- **Mapped drives**: right-click → Disconnect, then remap with the new password.
- **Scheduled tasks** (for developers): update the service account credentials in Task Scheduler.

If the lockout recurs frequently without obvious cause, IT can run a lockout source diagnostic to identify the rogue authentication attempt.
"""
        },
        {
            "id": "KB-A004",
            "title": "Requesting new software license or tool access",
            "summary": "How to submit a request for access to licensed software or internal tools.",
            "content": """# Requesting New Software License or Tool Access

## Check the Self-Service Portal First

Many commonly used applications can be installed without a ticket:
1. Open the **Company Self-Service Portal** (shortcut on your desktop or Start menu).
2. Browse or search for the application.
3. Click **Install** — it deploys automatically within 15 minutes.

## If It's Not in the Self-Service Portal

Submit a ticket with category **Access** and priority **Medium**.

Include:
- Application name and version (if specific)
- Vendor/publisher
- Business justification (what you will use it for)
- Whether a license needs to be purchased or if you just need access assigned
- Your manager's name for approval

## License Types

| Type | Process |
|------|---------|
| Existing pool license | IT assigns within 1 business day |
| New license purchase | Requires manager + budget approval; 3-5 business days |
| Subscription (SaaS) | May require procurement review; 5-10 business days |

## Enterprise Tools (Jira, Confluence, Salesforce, etc.)

For enterprise tool access:
1. Your manager must approve the request.
2. The tool owner (department admin) provisions access.
3. IT is not always involved — check with your manager first.

## After Access Is Granted

You will receive an email confirmation. If you do not receive access within the stated timeframe, reply to your ticket to follow up.
"""
        },
    ],
    "Other": [
        {
            "id": "KB-O001",
            "title": "How to submit an IT support request",
            "summary": "Overview of the IT helpdesk ticketing process and what information to include in your request.",
            "content": """# How to Submit an IT Support Request

A well-written ticket gets resolved faster. Here's how to do it right.

## What to Include

| Field | Tips |
|-------|------|
| **Title** | Short, specific (e.g., "Outlook crashes when opening attachments") |
| **Category** | Choose the closest match — it determines which team handles your ticket |
| **Priority** | See priority guide below |
| **Description** | Detailed explanation of the issue, steps to reproduce, and what you've already tried |

## Priority Guide

| Priority | Use When |
|----------|----------|
| **Critical** | Complete work stoppage; security incident; data loss |
| **High** | Major function unavailable; affects multiple users |
| **Medium** | Degraded but workable; single user impacted |
| **Low** | Minor inconvenience; enhancement request |

## After Submitting

- You will receive a confirmation email with your ticket number.
- An agent will respond within the SLA for your priority level:
  - Critical: 1 hour
  - High: 4 hours
  - Medium: 1 business day
  - Low: 3 business days
- You can check your ticket status and reply to the agent in the portal.

## Tips for Faster Resolution

- Include screenshots or screen recordings whenever possible.
- Note the exact error message text.
- Specify when the issue started and whether anything changed recently.
- List any troubleshooting steps you have already taken.
"""
        },
        {
            "id": "KB-O002",
            "title": "IT equipment request process",
            "summary": "How to request new hardware such as laptops, monitors, keyboards, and peripherals.",
            "content": """# IT Equipment Request Process

## Standard Equipment (Pre-Approved)

New employees receive standard equipment automatically. If you need a replacement or upgrade:

1. Submit a ticket with category **Other** and priority **Medium**.
2. Include:
   - Type of equipment needed
   - Business justification
   - Your manager's name for approval

## Standard Equipment List

| Item | Refresh Cycle |
|------|--------------|
| Laptop | 4 years |
| Monitor | 5 years |
| Keyboard/Mouse | As needed |
| Headset | As needed |
| Docking Station | With laptop |

## Non-Standard Equipment

Equipment not on the standard list (e.g., drawing tablets, specialized peripherals, ergonomic keyboards) requires:
1. Manager approval
2. Budget code
3. Procurement review if over $500

Submit a ticket with all three pieces of information to avoid delays.

## Loaner Equipment

Short-term loaners are available for:
- Traveling employees
- Devices under repair
- New hires waiting for equipment

Request via ticket or visit the IT desk directly. Loaners must be returned within the agreed period.

## Equipment Return

When leaving the company or upgrading devices, IT will arrange collection. Do not dispose of IT equipment yourself — it contains data and must be properly wiped.
"""
        },
        {
            "id": "KB-O003",
            "title": "Remote work setup checklist",
            "summary": "Everything you need to set up a secure and productive remote working environment.",
            "content": """# Remote Work Setup Checklist

## Before You Work Remotely

- [ ] **VPN access** — Confirm your VPN credentials work (see KB-N002 if issues).
- [ ] **MFA configured** — Set up on your mobile device (see KB-SEC003).
- [ ] **Company laptop** — Use only company-managed devices for work. Personal devices must be approved.
- [ ] **Secure WiFi** — Use your home network; avoid public WiFi. If necessary, use a VPN on public WiFi.

## Home Network Security

- [ ] Change your router's default admin password.
- [ ] Ensure your WiFi uses WPA3 or WPA2 encryption (check router settings).
- [ ] Keep your router firmware updated.
- [ ] Use a separate guest network for personal/IoT devices.

## Physical Security

- [ ] Position your screen to prevent visual eavesdropping (use a privacy screen if needed).
- [ ] Lock your screen when stepping away (**Win + L** / **Ctrl + Cmd + Q** on Mac).
- [ ] Keep company devices secured when not in use.

## Productivity Setup

- [ ] Test audio and video before your first meeting.
- [ ] Use a wired Ethernet connection for important calls when possible.
- [ ] Ensure your home internet plan meets minimum speeds: 25 Mbps down, 5 Mbps up.

## Reporting Issues Remotely

- Use the helpdesk portal to submit tickets.
- For urgent issues, call the helpdesk directly — agents can connect remotely via approved screen-sharing tools.
- Critical security incidents: call the security hotline immediately.
"""
        },
        {
            "id": "KB-O004",
            "title": "How to escalate an urgent IT issue",
            "summary": "When and how to escalate a support ticket for faster resolution of critical issues.",
            "content": """# How to Escalate an Urgent IT Issue

## When to Escalate

Escalate when:
- Your ticket has not been responded to within the SLA timeframe.
- The issue is worsening or spreading to other users.
- A Critical or High ticket was downgraded and you disagree.
- The resolution provided did not fix the issue.

## How to Escalate

### Option 1 — Update Your Ticket

Reply to your existing ticket with:
- Current status of the issue
- Business impact (who is affected, what work is blocked)
- Request for escalation to a senior engineer or manager

### Option 2 — Call the Helpdesk

For Critical issues, always call rather than waiting for ticket responses.

Provide:
- Your ticket number
- Your name and department
- Current impact (e.g., "entire department cannot access email")

### Option 3 — Contact Your IT Manager

If the helpdesk is unresponsive, escalate to the IT manager. Your manager can escalate internally on your behalf.

## Escalation SLA

| Priority | Standard Response | Escalation Threshold |
|----------|------------------|---------------------|
| Critical | 1 hour | 2 hours |
| High | 4 hours | 8 hours |
| Medium | 1 business day | 2 business days |
| Low | 3 business days | 5 business days |

## What Escalation Is Not

Escalation is for genuinely urgent or stalled issues. Repeated escalation of Low/Medium tickets without business justification may slow resolution for all users.
"""
        },
    ],
}

# Flat lookup for fast article retrieval
_ARTICLES_BY_ID = {a["id"]: a for arts in KNOWLEDGE_ARTICLES.values() for a in arts}

# ---------------------------------------------------------------------------
# Team / agent assignment
# ---------------------------------------------------------------------------

TEAM_MAP = {
    "Network":  {"team": "Network Operations",  "agent": "Alex Chen"},
    "Software": {"team": "Software Support",    "agent": "Sarah Johnson"},
    "Hardware": {"team": "Hardware Support",    "agent": "Mike Torres"},
    "Security": {"team": "Security Team",       "agent": "Lisa Park"},
    "Access":   {"team": "IT Admin",            "agent": "David Kim"},
    "Other":    {"team": "General IT Support",  "agent": "James Wilson"},
}

# Context-aware first-reply templates per category
FIRST_REPLIES = {
    "Network":  "I'm looking into the network issue now. Can you confirm if the problem affects all devices or just one?",
    "Software": "I can help with that software issue. Have you tried restarting the application or clearing the cache?",
    "Hardware": "I'll arrange for a hardware inspection. Is the device completely non-functional or intermittently failing?",
    "Security": "This has been flagged as high priority. I'm escalating to our security incident response team immediately.",
    "Access":   "I'm checking your access permissions in our system. This typically takes 10-15 minutes to process.",
    "Other":    "Thanks for reaching out. I'm reviewing your request and will provide an update shortly.",
}

FOLLOW_UP_REPLIES = [
    "We're still working on this. Could you provide any additional details?",
    "I've escalated this internally. Expect a resolution within 2 hours.",
    "Good news — we believe we have a fix. Can you try the suggested steps and confirm if it resolves the issue?",
]

# ---------------------------------------------------------------------------
# In-memory store
# ---------------------------------------------------------------------------

tickets_db: dict[str, Ticket] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_id() -> str:
    return str(uuid.uuid4())


def _make_ticket(title: str, description: str, category: str, priority: str) -> Ticket:
    assignment = TEAM_MAP.get(category, TEAM_MAP["Other"])
    ticket_id = _make_id()
    created_at = _now()

    system_msg = Message(
        id=_make_id(),
        sender="System",
        sender_type="system",
        content=f"Ticket created and assigned to {assignment['team']}. {assignment['agent']} will be assisting you.",
        timestamp=created_at,
    )

    return Ticket(
        id=ticket_id,
        title=title,
        description=description,
        category=category,
        priority=priority,
        status="Open",
        assigned_team=assignment["team"],
        assigned_agent=assignment["agent"],
        created_at=created_at,
        messages=[system_msg],
    )


# ---------------------------------------------------------------------------
# Seed data — 3 sample tickets
# ---------------------------------------------------------------------------

def _seed():
    samples = [
        ("Cannot connect to VPN", "Since this morning I am unable to connect to the company VPN. I get an error saying authentication failed even though my password is correct.", "Network", "High"),
        ("Excel keeps crashing on large files", "Microsoft Excel crashes every time I open a file larger than 5 MB. This started after the latest Windows update yesterday.", "Software", "Medium"),
        ("Laptop screen flickering", "My laptop screen has been flickering randomly since last week. Sometimes it goes completely black for a few seconds before coming back.", "Hardware", "Low"),
    ]
    for title, desc, cat, pri in samples:
        t = _make_ticket(title, desc, cat, pri)
        tickets_db[t.id] = t


_seed()

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/api/tickets", response_model=List[Ticket])
def list_tickets():
    return list(tickets_db.values())


@app.post("/api/tickets", response_model=Ticket, status_code=201)
def create_ticket(body: CreateTicketBody):
    if body.category not in TEAM_MAP:
        raise HTTPException(status_code=422, detail=f"Invalid category: {body.category}")
    ticket = _make_ticket(body.title, body.description, body.category, body.priority)
    tickets_db[ticket.id] = ticket
    return ticket


@app.get("/api/tickets/{ticket_id}", response_model=Ticket)
def get_ticket(ticket_id: str):
    ticket = tickets_db.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.patch("/api/tickets/{ticket_id}/status", response_model=Ticket)
def update_status(ticket_id: str, body: UpdateStatusBody):
    ticket = tickets_db.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    valid_statuses = {"Open", "In Progress", "Resolved", "Closed"}
    if body.status not in valid_statuses:
        raise HTTPException(status_code=422, detail=f"Invalid status: {body.status}")
    ticket.status = body.status
    return ticket


@app.post("/api/tickets/{ticket_id}/messages", response_model=List[Message])
def send_message(ticket_id: str, body: SendMessageBody):
    ticket = tickets_db.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Count how many user messages already exist (before this one)
    user_msg_count = sum(1 for m in ticket.messages if m.sender_type == "user")

    now = _now()

    # Save the user message
    user_msg = Message(
        id=_make_id(),
        sender="You",
        sender_type="user",
        content=body.content,
        timestamp=now,
    )
    ticket.messages.append(user_msg)

    # Determine agent reply
    if user_msg_count < 2:
        # First or second user message — use category-specific reply
        reply_content = FIRST_REPLIES.get(ticket.category, FIRST_REPLIES["Other"])
    else:
        # Cycle through follow-up replies (0-based index offset by 2)
        idx = (user_msg_count - 2) % len(FOLLOW_UP_REPLIES)
        reply_content = FOLLOW_UP_REPLIES[idx]

    agent_msg = Message(
        id=_make_id(),
        sender=ticket.assigned_agent,
        sender_type="agent",
        content=reply_content,
        timestamp=_now(),
    )
    ticket.messages.append(agent_msg)

    return [user_msg, agent_msg]


# ---------------------------------------------------------------------------
# Knowledge endpoints
# ---------------------------------------------------------------------------

@app.get("/api/knowledge")
def get_knowledge_articles(category: Optional[str] = None, q: Optional[str] = None):
    """Get knowledge articles. If q is provided, search by keywords across all articles.
    Otherwise filter by category."""
    if q:
        # Keyword search: search across all articles regardless of category
        all_articles = [a for arts in KNOWLEDGE_ARTICLES.values() for a in arts]
        keywords = [kw.lower() for kw in q.split() if len(kw) >= 2]
        if not keywords:
            return []
        # Score articles by how many keywords match title or summary
        scored = []
        for article in all_articles:
            text = (article["title"] + " " + article["summary"]).lower()
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scored.append((score, article))
        scored.sort(key=lambda x: x[0], reverse=True)
        # Return summary view (no content field) to keep list response light
        return [{"id": a["id"], "title": a["title"], "summary": a["summary"]} for _, a in scored[:4]]
    elif category and category in KNOWLEDGE_ARTICLES:
        return [{"id": a["id"], "title": a["title"], "summary": a["summary"]} for a in KNOWLEDGE_ARTICLES[category]]
    else:
        return [{"id": a["id"], "title": a["title"], "summary": a["summary"]} for a in _ARTICLES_BY_ID.values()]


@app.get("/api/knowledge/{article_id}")
def get_knowledge_article(article_id: str):
    """Get a single knowledge article including its full content."""
    article = _ARTICLES_BY_ID.get(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
