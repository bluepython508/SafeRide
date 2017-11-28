import argparse
import os.path
import signal
import subprocess
import time

import gpiozero
import picamera
import requests

DEFAULT_FLAG_TIME = 120
DEFAULT_PASS_TIME = 60
DEFAULT_OUTPUT_DIR = "/home/video/SafetyVideo"
DEFAULT_WIFI_SSID = "SafeRideNetwork"
DEFAULT_SERVER_HOSTNAME = "saferide.local"


class LoopExit(Exception):
    pass


def exitLoop():
    raise LoopExit()


def finishRide(args):
    args.finish_output.on()
    time.sleep(0.01)
    args.finish_output.off()
    subprocess.run("wifi", "connect", "--ad-hoc", args.ssid)  # Connect to WiFi
    subprocess.run(
        "scp", "-r", '/home/pi/Video',
        "video@{host}:{location}/{pi}".format(host=args.server, location=args.output_dir,
                                              pi=os.path.basename(
                                                                                __file__
                                                                            ).split(
                                                                                '.'
                                                                            )[0]),
        shell=True)  # Copy video over to a unique filename
    subprocess.run('rm -rf /home/pi/Video', shell=True)
    subprocess.run('mkdir -p /home/pi/Video', shell=True)
    requests.get('%s/rideDone' % args.server)
    subprocess.run("poweroff")  # Shutdown


def getDistance(val):
    mv = (val * 5) * 1000  # 0-1 x5-> 0-5 Volts -> x1000 = mV
    distance_mm = 1420000 / (mv - 1091)
    return distance_mm / 10  # Cm


def threshholdIter(values, threshhold, operation=lambda x: x):
    for val in values:
        value = operation(val)
        yield (value < threshhold)


def flag(args):
    args.pass_signal.blink(on_time=0.1, background=True, n=1)


def ride(args):
    args.camera = picamera.PiCamera()
    args.stream = picamera.PiCameraCircularIO(seconds=max(args.flag_length, args.pass_length))
    args.camera.start_recording(args.stream, 'mp4')
    args.pass_signal.values = threshholdIter(args.range_sensor.values, 150, getDistance)
    try:
        while True:
            args.camera.wait_recording(1)
    finally:
        args.camera.stop_recording()
        args.camera.close()
        args.ride_button.when_pressed = lambda: ride(args)
        args.flag_button.when_pressed = lambda: finishRide(args)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--flag-length", default=DEFAULT_FLAG_TIME)
    parser.add_argument("-p", "--pass-length", default=DEFAULT_PASS_TIME)
    parser.add_argument("-o", "--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("-n", "--network", default=DEFAULT_WIFI_SSID)
    parser.add_argument("-s", "--server", default=DEFAULT_SERVER_HOSTNAME)

    args = parser.parse_args()

    args.flag_button = gpiozero.Button(2)
    args.ride_button = gpiozero.Button(21)
    args.flag_signal = gpiozero.LED(3)
    args.pass_signal = gpiozero.LED(4)
    args.ride_signal = gpiozero.LED(5)
    args.range_sensor = gpiozero.MCP3008()
    args.recording_led = gpiozero.LED(20)
    args.ride_button.when_pressed = lambda: ride(args)


if __name__ == "__main__":
    main()
    signal.pause()
