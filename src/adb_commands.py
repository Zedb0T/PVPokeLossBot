import os


import os

def send_adb_tap(x: int, y: int, device_serial: str = None) -> bool:
    """
    Sends an adb tap command to simulate a touch event on the specified coordinates.
    Returns True if the adb command was successful, False otherwise.
    """
    adb_command = "adb"
    if device_serial:
        adb_command += f" -s {device_serial}"
    adb_command += f" shell input tap {x} {y}"
    error_code = os.system(adb_command)
    return error_code == 0



def turn_screen_off() -> bool:
    adb_command = "adb shell input keyevent 26"
    error_code = os.system(adb_command)
    return error_code == 0
