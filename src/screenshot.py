import os
import platform

def capture_screenshot(filename: str, device_serial: str = None) -> bool:
    """
    Captures a screenshot of the Android screen using adb and saves it to a file.
    Returns True if the adb command was successful, False otherwise.
    """
    adb_command = "adb"
    if device_serial:
        adb_command += f" -s {device_serial}"
    if platform.system() == "Windows":
        adb_command += f" exec-out screencap -p > \"{filename}\""
    else:
        adb_command += f" exec-out screencap -p > \"{filename}\" 2> /dev/null"
    error_code = os.system(adb_command)
    if error_code == 0:
        # print(f"Screenshot saved at: {filename}")
        return True
    else:
        print("Failed to capture screenshot.")
        return False
