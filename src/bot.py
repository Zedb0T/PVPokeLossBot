import sys
import time
import logging

from src import constants
from src import screenshot
from src.adb_commands import send_adb_tap, turn_screen_off
from src.game_action import GameActions
from src.image_decision_maker import make_decision
from src.image_template_loader import load_image_templates


import subprocess

def get_connected_devices():
    """
    Function to get the serial numbers of connected Android devices.
    Returns a list of device serial numbers.
    """
    # Get USB-connected devices
    result_usb = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
    output_lines_usb = result_usb.stdout.split('\n')[1:]
    devices_usb = [line.split('\t')[0] for line in output_lines_usb if line.strip() != '']

    # Get Wi-Fi-connected devices
    result_wifi = subprocess.run(['adb', 'devices'], capture_output=True, text=True,
                                 env={"ANDROID_ADB_SERVER_PORT": "5037", "ADB_VENDOR_KEYS": "path/to/adb_keys"})
    output_lines_wifi = result_wifi.stdout.split('\n')[1:]
    devices_wifi = [line.split('\t')[0] for line in output_lines_wifi if line.strip() != '']

    # Combine USB and Wi-Fi devices
    devices = devices_usb + devices_wifi

    return devices

def run():
    # Get connected devices
    connected_devices = get_connected_devices()

    if not connected_devices:
        logging.error("No devices connected.")
        return

    # Populate DEVICE_SERIALS with connected devices
    constants.DEVICE_SERIALS = connected_devices

    # Time the bot will stay in game until it forfeits
    time_to_stay_in_game = 5

    # Start the timer until bot forfeits the game
    start_time = time.time()

    template_images = load_image_templates()

    game_entered = False
    waiting_for_device = False

    while True:
        # Iterate over each device connected
        for device_serial in constants.DEVICE_SERIALS:
            # Capture a screenshot for each device and save it to a file
            if not screenshot.capture_screenshot(constants.SCREENSHOT_FILE_NAME, device_serial):
                if waiting_for_device:
                    print(".", end="", flush=True)
                else:
                    logging.info(f"Error capturing screenshot for device {device_serial}. Waiting until phone is connected.")
                    waiting_for_device = True
                time.sleep(0.5)
                continue

            if waiting_for_device:
                waiting_for_device = False
                print()

            # Check if the timer has run out
            elapsed_time = time.time() - start_time
            if game_entered and elapsed_time > time_to_stay_in_game:
                logging.info("Timer has run out. Forfeit the game.")
                send_adb_tap(75, 460, device_serial)
                time.sleep(1)
                send_adb_tap(429, 1254, device_serial)
                time.sleep(1)

            next_action = make_decision(template_images, constants.SCREENSHOT_FILE_NAME)

            if next_action.action == GameActions.tap_position:
                # If not ingame reset timer
                if next_action.is_ingame:
                    if not game_entered:
                        start_time = time.time()
                        game_entered = True
                else:
                    start_time = time.time()
                    game_entered = False

                send_adb_tap(next_action.position[0], next_action.position[1], device_serial)

            elif next_action.action == GameActions.exit_program:
                turn_screen_off(device_serial)
                logging.info(f"Max number of games played for device {device_serial}. Exit program.")
                sys.exit(1)

            time.sleep(2)

if __name__ == "__main__":
    run()
