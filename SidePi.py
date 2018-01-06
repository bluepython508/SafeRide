# SidePi.py
# A part of SafeRide
# This file is written for the recording unit of SafeRide
import argparse
import signal
import subprocess
import threading
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


def getDistance(val):
    mv = (val * 5) * 1000  # 0-1 x5-> 0-5 Volts -> x1000 = mV
    distance_mm = 1420000 / (mv - 1091)
    return distance_mm / 10  # Cm


def threshholdIter(values, threshhold, operation=lambda x: x):
    for val in values:
        value = operation(val)
        yield 0 if (value < threshhold) else 1


def runIter(values, func, *args, **kwargs):
    for value in values:
        if value:
            thread = threading.Thread(target=func, args=args, kwargs=kwargs)
            thread.start()
        yield value


class SidePi:
    def __init__(self, args):
        self.args = args

        self.flag_button = gpiozero.Button(2)
        self.ride_button = gpiozero.Button(21)
        self.flag_signal = gpiozero.LED(3)
        self.pass_signal = gpiozero.LED(4)
        self.ride_signal = gpiozero.LED(5)
        self.range_sensor = gpiozero.MCP3008()
        self.recording_led = gpiozero.LED(20)
        self.ride_button.when_pressed = lambda: self.startRide()

    def finishRide(self):
        subprocess.run(("wifi", "connect", "--ad-hoc"), self.args.ssid)  # Connect to WiFi
        # Copy video over to a unique filename
        try:
            subprocess.run(
                ("scp", "-r", self.args.save_dir,
                 "video@{}:{}/SidePi".format(self.args.server, self.args.output_dir)), shell=True, check=True)
        except:
            pass
        else:
            subprocess.run(("rm -rf ", self.args.save_dir), shell=True)
            subprocess.run(("mkdir -p", self.args.save_dir), shell=True)
        self.flag_signal.on()
        time.sleep(0.01)
        self.flag_signal.off()
        requests.get('{}/rideDone'.format(self.args.server))
        subprocess.run(("poweroff",))  # Shutdown

    def onPass(self):
        self.recording_led.on()
        self.stream.clear()
        self.camera.wait_recording(self.args.pass_length)
        self.stream.copy_to(self.get_path(), seconds=self.args.pass_length, first_frame=picamera.PiVideoFrameType.frame)
        self.recording_led.off()

    def onFlag(self):
        self.recording_led.blink(background=True, n=1)
        self.flag_signal.blink(on_time=0.1, background=True, n=1)
        self.stream.copy_to(self.get_path(), seconds=self.args.flag_length, first_frame=picamera.PiVideoFrameType.frame)

    def startRide(self):
        self.camera = picamera.PiCamera(sensor_mode=2)
        self.stream = picamera.PiCameraCircularIO(self.camera,
                                                  seconds=max(self.args.flag_length, self.args.pass_length))
        self.camera.start_recording(self.stream, format="h264")
        self.pass_signal.source = runIter(threshholdIter(self.range_sensor.values, 150, getDistance), self.onPass)
        self.ride_button.when_pressed = exitLoop
        self.flag_button.when_pressed = self.onFlag
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
    pi = SidePi(args)
    signal.pause()
