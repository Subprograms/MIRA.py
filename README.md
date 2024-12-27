# MIRA.py: Monitoring Invisible Remote Activity - A Stealthy Startup Script for Activity Exfiltration
Stealthy startup script that monitors network traffic, keystrokes, and screen snapshots of a victim machine from a remote machine. This shall be used to ethically simulate persistence, defense evasion, and exfiltration techniques.

## Setup
- Foremost, change the value of TARGET_IP in the script to the intended IP address where the keylogs, screenshots, and network activity of the victim machine are to be transmitted.
- Optionally, you may change the time intervals for each activity exfiltration (for keylogging, this interval specifies the duration before a new line of log is created in the generated log file of the keystrokes).

## Mechanism
- 1. Upon execution of the script in the victim machine, it will create a value in the Run key of HKCU to become a startup script, with a Name that imitates an existing Value in the key appended with "...".
- 2. Upon every startup, the script's file will be renamed to imitate other existing files in its current directory for stealth (appended with a '.' before the file extension in order to make this possible).
- 3. Upon every renaming of the script's filename, its corresponding Value in the Run key is updated to reflect this change, specifically its Data field.
- 4. Upon every execution (and startup of the system), the script will exfiltrate keystrokes, screenshots of the screen, and network activity of the victim machine, to be transmitted to the specified TARGET_IP. This follows the specified time interval for each exfiltration activity as well.
- 5. Upon the deletion of the script's corresponding Value in the Run key, the script will attempt to restore it.
