import argparse
import datetime
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
        "scp", "-r", "/home/pi/Video",
        "video@{}:{}/FrontPi".format(args.server, args.output_dir),
        shell=True)  # Copy video over to a unique filename
    subprocess.run("rm -rf /home/pi/Video", shell=True)
    subprocess.run("mkdir -p /home/pi/Video", shell=True)
    requests.get("{}/rideDone".format(args.server))
    subprocess.run("poweroff")  # Shutdown


def passed(args):
    args.stream.clear()
    args.camera.wait_recording(args.pass_length)
    args.stream.copy_to("/home/pi/Video/{}.mp4".format(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')),
                        seconds=args.pass_length, first_frame=picamera.PiVideoFrameType.frame, format='h264')


def flag(args):
    args.flag_signal.blink(on_time=0.1, background=True, n=1)
    args.stream.copy_to("/home/pi/Video/{}.mp4".format(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')),
                        seconds=args.flag_length, first_frame=picamera.PiVideoFrameType.frame, format='h264')


def ride(args):
    args.camera = picamera.PiCamera(sensor_mode=2)
    args.stream = picamera.PiCameraCircularIO(args.camera, seconds=max(args.flag_length, args.pass_length))
    args.camera.start_recording(args.stream, "mp4")
    args.ride_button.when_pressed = exitLoop
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

    args.flag_button = gpiozero.Button(3)
    args.ride_button = gpiozero.Button(4)
    args.pass_button = gpiozero.Button(21)
    args.ride_button.when_pressed = lambda: ride(args)


if __name__ == "__main__":
    main()
    signal.pause()
