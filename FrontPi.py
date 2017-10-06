import picamera
import signal
import time
import datetime
import gpiozero
import subprocess
import argparse
import os.path

DEFAULT_FLAG_TIME = 60
DEFAULT_OUTPUT_DIR = "/home/pi/SafetyVideo"
DEFAULT_WIFI_SSID = "SafeRideNetwork"
DEFAULT_SERVER_HOSTNAME = "saferide.local"


class LoopExit(Exception):
    pass


def exitLoop():
    raise LoopExit()


def finishRide(args):
    subprocess.run("wifi", "connect", "--ad-hoc", args.ssid, shell=True) # Connect to WiFi
    subprocess.run(
        "scp", "-r", args.output_dir, "video@{host}:{location}/{pi}".format(host=args.server, location=args.output_dir,
                                                                            pi=os.path.basename(
                                                                                __file__
                                                                            ).split(
                                                                                '.'
                                                                            )[0]),
        shell=True) # Copy video over to a unique filename
    subprocess.run("sudo", "poweroff") # Shutdown

def getDistance(val):
    mv = (val * 5) * 1000  # 0-1 x5-> 0-5 Volts -> x1000 = mV
    distance_mm = 1420000 / (mv - 1091)
    return distance_mm / 10  # Cm


def threshholdIter(values, threshhold, operation=lambda x: x):
    for val in values:
        value = operation(val)
        yield (value < threshhold)


def passed(args, stream):
    filename = os.path.join(
        args.output_dir,
        datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    )
    ".h264"
    stream.clear()
    time.sleep(60)
    stream.copy_to(filename)


def flag(args, stream):
    filename = os.path.join(
        args.output_dir,
        datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    )
    ".h264"
    stream.copy_to(filename)


def ride(args, flag_button, ride_button):
    camera = picamera.PiCamera()
    stream = picamera.PiCameraCircularIO(camera, seconds=args.clip_length)
    flag_button.when_pressed = lambda: flag(args, stream)
    camera.start_recording(stream, format='h264')
    try:
        ride_button.when_pressed = exitLoop
        while True:
            camera.wait_recording(1)
    except LoopExit:
        camera.stop_recording()
        camera.unload()
        ride_button.when_pressed = lambda: ride(args, flag_button, ride_button)
        flag_button.when_pressed = lambda: finishRide(args)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--clip-length", default=DEFAULT_FLAG_TIME)
    parser.add_argument("-o", "-output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("-n", "--network", default=DEFAULT_WIFI_SSID)
    parser.add_argument("-s", "--server", default=DEFAULT_SERVER_HOSTNAME)

    args = parser.parse_args()

    pass_button = gpiozero.Button(4)
    flag_button = gpiozero.Button(3)
    ride_button = gpiozero.Button(21)
    ride_button.when_pressed = lambda: ride(args, flag_button, ride_button)
    signal.pause()


if __name__ == "__main__":
    main()
