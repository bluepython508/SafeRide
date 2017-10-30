import picamera
import signal
import time
import datetime
import gpiozero
import subprocess
import argparse
import os.path
import requests

DEFAULT_FLAG_TIME = 60
DEFAULT_OUTPUT_DIR = "/home/video/SafetyVideo"
DEFAULT_WIFI_SSID = "SafeRideNetwork"
DEFAULT_SERVER_HOSTNAME = "saferide.local"


class LoopExit(Exception):
    pass


def exitLoop():
    raise LoopExit()


def finishRide(args, finish_output):
    finish_output.on()
    time.sleep(0.01)
    finish_output.off()
    subprocess.run("wifi", "connect", "--ad-hoc", args.ssid, shell=True) # Connect to WiFi
    subprocess.run(
        "scp", "-r", args.output_dir,
        "video@{host}:{location}/{pi}".format(host=args.server, location=DEFAULT_OUTPUT_DIR,
                                              pi=os.path.basename(
                                                                                __file__
                                                                            ).split(
                                                                                '.'
                                                                            )[0]),
        shell=True) # Copy video over to a unique filename
    requests.get('%s/rideDone' % args.server)
    subprocess.run("sudo", "poweroff") # Shutdown

def getDistance(val):
    mv = (val * 5) * 1000  # 0-1 x5-> 0-5 Volts -> x1000 = mV
    distance_mm = 1420000 / (mv - 1091)
    return distance_mm / 10  # Cm


def threshholdIter(values, threshhold, operation=lambda x: x):
    for val in values:
        value = operation(val)
        yield (value < threshhold)


def passed(args, stream, pass_output):
    filename = os.path.join(
        args.output_dir,
        datetime.datetime.now().strftime("%H:%M:%S")
    )
    ".h264"
    pass_output.on()
    time.sleep(0.01)
    pass_output.off()
    stream.clear()
    time.sleep(60)
    stream.copy_to(filename)


def flag(args, stream, flag_output):
    filename = os.path.join(
        args.output_dir,
        datetime.datetime.now().strftime("%H:%M:%S")
    )
    ".h264"
    stream.copy_to(filename)
    flag_output.on()
    time.sleep(0.01)
    flag_output.off()


def ride(args, flag_button, ride_button, flag_output, range_sensor, pass_output, finish_output, ride_output):
    camera = picamera.PiCamera()
    stream = picamera.PiCameraCircularIO(camera, seconds=args.clip_length)
    flag_button.when_pressed = lambda: flag(args, stream, flag_output)
    camera.start_recording(stream, format='h264')
    pass_output.values = threshholdIter(range_sensor.values, 150, getDistance)
    try:
        ride_button.when_pressed = exitLoop
        while True:
            camera.wait_recording(1)
    except LoopExit:
        camera.stop_recording()
        camera.unload()
        ride_button.when_pressed = lambda: ride(args, flag_button, ride_button, flag_output, range_sensor, pass_output, ride_output)
        flag_button.when_pressed = lambda: finishRide(args, finish_output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--clip-length", default=DEFAULT_FLAG_TIME)
    parser.add_argument("-o", "-output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("-n", "--network", default=DEFAULT_WIFI_SSID)
    parser.add_argument("-s", "--server", default=DEFAULT_SERVER_HOSTNAME)

    args = parser.parse_args()

    flag_button = gpiozero.Button(2)
    ride_button = gpiozero.Button(21)
    flag_output = gpiozero.LED(3)
    pass_output = gpiozero.LED(4)
    ride_output = gpiozero.LED(5)
    range_sensor = gpiozero.MCP3008()
    ride_button.when_pressed = lambda: ride(args, flag_button, ride_button, flag_output, range_sensor, pass_output, ride_output)
    signal.pause()


if __name__ == "__main__":
    main()
