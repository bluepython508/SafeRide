# SidePi.py
# A part of SafeRide
# This file is written for the recording unit of SafeRide
import argparse
import os
import subprocess
import time

import gpiozero
import picamera
import requests

DEFAULT_FLAG_TIME = 120
DEFAULT_PASS_TIME = 30
DEFAULT_OUTPUT_DIR = "/home/video/SafetyVideo"
DEFAULT_WIFI_SSID = "SafeRide"
DEFAULT_SERVER_HOSTNAME = "saferide.local"
DEFAULT_SAVE_DIR = "/home/pi/Video"
DEFAULT_CHIP_SELECT = 25
DEFAULT_MOSI = 22
DEFAULT_MISO = 10
DEFAULT_CLK = 9

def getDistance(x):
        return 3714 * x ** 2 - 4212* x + 1275

def threshholdIter(values, threshhold, operation=lambda x: x):
    for val in values:
        value = operation(val)
        #print(val)
        #print(value)
        yield 0 if (value > threshhold) else 1


def runIter(values, func, *args, **kwargs):
    for value in values:
        if value > 0:
            #thread = threading.Thread(target=func, args=args, kwargs=kwargs)
            #thread.start()
            func(*args, **kwargs)
        yield value


class SidePi:
    def __init__(self, args):
        self.args = args
        print('init')
        self.flag_button = gpiozero.Button(2)
        self.ride_button = gpiozero.Button(21)
        self.flag_signal = gpiozero.LED(3)
        self.pass_signal = gpiozero.LED(4)
        self.ride_signal = gpiozero.LED(5)
        self.range_sensor = gpiozero.MCP3008(select_pin=args.chip_select, mosi_pin=args.mosi, miso_pin=args.miso, clock_pin=args.clk)
        self.recording_led = gpiozero.LED(20)
        self.recording_led.blink(n=1, background=True)
        self.ride_button.wait_for_press()
        self.startRide()

    def finishRide(self):
        print('Finished')
        #subprocess.run(("wifi", "connect", "--ad-hoc", self.args.network))  # Connect to WiFi
        subprocess.run(('ifup', 'wlan0'))
        # Copy video over to a unique filename
        try:
            print(' '.join(("scp","-i /home/pi/.ssh/id_rsa", self.args.save_dir + "/*", "video@{}:{}/SidePi".format(self.args.server, self.args.output_dir))))
            subprocess.run(
                 (' '.join(("scp","-i /home/pi/.ssh/id_rsa", self.args.save_dir + "/*", "video@{}:{}/SidePi".format(self.args.server, self.args.output_dir))),), shell=True, check=True)
        except:
            pass
        else:
            subprocess.run(("rm -rf", self.args.save_dir), shell=True)
            print(' '.join(("mkdir", self.args.save_dir)))
            subprocess.run(' '.join(("mkdir -p", self.args.save_dir)), shell=True)
            self.flag_signal.on()
            time.sleep(0.01)
            self.flag_signal.off()
            requests.get('http://{}/rideDone'.format(self.args.server))
            subprocess.run("kill -9 {}".format(os.getpid()), shell=True)
            #subprocess.run(("poweroff",))  # Shutdown

    def onPass(self):
        print('Unsafe pass')
        self.recording_led.blink(on_time=self.args.pass_length, off_time=0, n=1, background=True)
        self.stream.clear()
        self.camera.wait_recording(self.args.pass_length)
        print(self.get_path())
        self.stream.copy_to(self.get_path(), seconds=self.args.pass_length)

    def onFlag(self):
        print('Flag')
        self.recording_led.blink(background=True, n=1)
        self.flag_signal.blink(on_time=0.1, background=True, n=1)
        print(self.get_path())
        self.stream.copy_to(self.get_path(), seconds=self.args.flag_length)

    def startRide(self):
        print('Starting ride')
        self.camera = picamera.PiCamera(sensor_mode=2)
        self.stream = picamera.PiCameraCircularIO(self.camera,
                                                  seconds=max(self.args.flag_length, self.args.pass_length) + 1)
        self.camera.start_recording(self.stream, 'h264')
        self.pass_signal.source = runIter(threshholdIter(self.range_sensor.values, 150, getDistance), self.onPass)
        self.flag_button.when_activated = lambda: self.onFlag()
        self.ride_button.wait_for_release()
        self.ride_button.wait_for_press()
        self.camera.stop_recording()
        self.camera.close()
        print("Ride done")
        self.flag_button.when_pressed = lambda: self.finishRide()
        self.pass_signal.source = None
        self.ride_button.wait_for_release()
        self.ride_button.wait_for_press()
        self.startRide()

    def get_path(self):
        return self.args.save_dir + "/{}.h264".format(time.strftime('%Y-%m-%dT%H:%M:%S'))
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--flag-length", default=DEFAULT_FLAG_TIME, type=int)
    parser.add_argument("-p", "--pass-length", default=DEFAULT_PASS_TIME, type=int)
    parser.add_argument("-o", "--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("-n", "--network", default=DEFAULT_WIFI_SSID)
    parser.add_argument("-s", "--server", default=DEFAULT_SERVER_HOSTNAME)
    parser.add_argument("-d", "--save-dir", default=DEFAULT_SAVE_DIR)
    parser.add_argument("--chip-select", default=DEFAULT_CHIP_SELECT, type=int)
    parser.add_argument("--miso", default=DEFAULT_MISO, type=int)
    parser.add_argument("--mosi", default=DEFAULT_MOSI, type=int)
    parser.add_argument("--clk", default=DEFAULT_CLK, type=int)
    
    
    args = parser.parse_args()
    subprocess.run("rm -rf {}".format(args.save_dir), shell=True)
    subprocess.run("mkdir -p {}".format(args.save_dir), shell=True)
    try:
        pi = SidePi(args)
    except BaseException:
        pass
