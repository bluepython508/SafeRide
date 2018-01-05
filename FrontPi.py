# FrontPi.py
# A part of SafeRide
# This file is written for the recording unit of SafeRide
import argparse
import signal
import subprocess
import time

import gpiozero
import picamera
import requests

DEFAULT_FLAG_TIME = 120
DEFAULT_PASS_TIME = 60
DEFAULT_OUTPUT_DIR = "/home/video/SafetyVideo"
DEFAULT_WIFI_SSID = "SafeRide"
DEFAULT_SERVER_HOSTNAME = "saferide.local"
DEFAULT_SAVE_DIR = "/home/pi/Video"


class LoopExit(Exception):
    pass


def exitLoop():
    raise LoopExit()


class FrontPi:
    def __init__(self, args):
        self.args = args
        self.flag_button = gpiozero.Button(3)
        self.ride_button = gpiozero.Button(4)
        self.pass_button = gpiozero.Button(21)
        self.ride_button.when_pressed = lambda: self.startRide()

    def finishRide(self):
        subprocess.run(("wifi", "connect", "--ad-hoc"), self.args.ssid)  # Connect to WiFi
        # Copy video over to a unique filename
        try:
            subprocess.run(
                ("scp", "-r", self.args.save_dir,
                 "video@{}:{}/FrontPi".format(self.args.server, self.args.output_dir)), shell=True, check=True)
        except:
            pass
        else:
            subprocess.run(("rm -rf ", self.args.save_dir), shell=True)
            subprocess.run(("mkdir -p", self.args.save_dir), shell=True)
        requests.get("{}/rideDone".format(self.args.server))  # Tell server to analyse video.
        subprocess.run(("poweroff",))  # Shutdown

    def onPass(self):
        self.stream.clear()
        self.camera.wait_recording(self.args.pass_length)
        self.stream.copy_to(self.get_path(), seconds=self.args.pass_length, first_frame=picamera.PiVideoFrameType.frame)

    def onFlag(self):
        self.stream.copy_to(self.get_path(), seconds=self.args.flag_length, first_frame=picamera.PiVideoFrameType.frame)

    def startRide(self):
        self.camera = picamera.PiCamera(sensor_mode=2)
        self.stream = picamera.PiCameraCircularIO(self.camera,
                                                  seconds=max(self.args.flag_length, self.args.pass_length))
        self.camera.start_recording(self.stream, format="h264")
        self.ride_button.when_pressed = exitLoop
        self.pass_button.when_pressed = lambda: self.onPass()
        self.flag_button.when_pressed = lambda: self.onFlag()
        try:
            while True:
                self.camera.wait_recording(1)
        except LoopExit:
            pass
        finally:
            self.camera.stop_recording()
            self.camera.close()
            self.ride_button.when_pressed = lambda: self.startRide()
            self.flag_button.when_pressed = lambda: self.finishRide()

    def get_path(self):
        self.args.save_dir + "/{}.mp4".format(time.strftime('%Y-%m-%dT%H:%M:%S'))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--flag-length", default=DEFAULT_FLAG_TIME)
    parser.add_argument("-p", "--pass-length", default=DEFAULT_PASS_TIME)
    parser.add_argument("-o", "--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("-n", "--network", default=DEFAULT_WIFI_SSID)
    parser.add_argument("-s", "--server", default=DEFAULT_SERVER_HOSTNAME)
    parser.add_argument("-d", "--save-dir", default=DEFAULT_SAVE_DIR)

    args = parser.parse_args()

    pi = FrontPi(args)
    signal.pause()
