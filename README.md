# MIRA.py: Monitoring Invisible Remote Activity - A Stealthy Startup Script for Activity Exfiltration
Stealthy startup script that monitors network traffic, keystrokes, and screen snapshots of a victim machine from a remote machine. This shall be used to ethically simulate persistence, defense evasion, and exfiltration techniques.

## Setup (MIRA.py)
- Foremost, change the value of TARGET_IP in the script to the intended IP address where the keylogs, screenshots, and network activity of the victim machine are to be transmitted. By default, this is set to 127.0.0.1.
- Foremost, ensure that the victim machine and TARGET_IP machine can reach each other (i.e. in the same network).
- Optionally, you may change the time intervals for each activity exfiltration (for keylogging, this interval specifies the duration before a new line of log is created in the generated log file of the keystrokes).

## Setup (MIRA_Listener.py)
- Foremost, specify the directories where each type of file regarding the exfiltrated activity are to be stored in the TARGET_IP machine. By default, these are set to Downloads, if you intend to use this directory you MUST change "User" into the corresponding user of the TARGET_IP machine.
- Foremost, execute this script in the TARGET_IP machine. While this script is running, it will accept the transmitted files regarding the exfiltrated activity data of the victim machine.

## Mechanism
1. Upon execution of the script in the victim machine, it will create a value in the Run key of HKCU to become a startup script, with a Name that imitates an existing Value in the key appended with "...".
2. Upon every startup, the script's file will be renamed to imitate other existing files in its current directory for stealth (appended with a '.' before the file extension in order to make this possible).
3. Upon every renaming of the script's filename, its corresponding Value in the Run key is updated to reflect this change, specifically its Data field.
4. Upon every execution (and startup of the system), the script will exfiltrate keystrokes, screenshots of the screen, and network activity of the victim machine, to be transmitted to the specified TARGET_IP. This follows the specified time interval for each exfiltration activity as well.
5. Upon the deletion of the script's corresponding Value in the Run key, the script will attempt to restore it.

## Notes
- The pertinent files regarding the exfiltrated activities can be found in the specified directories in the TARGET_IP machine.
