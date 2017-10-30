from openalpr import Alpr
from contextlib import closing
from videosequence import VideoSequence
from os import listdir, makedirs
# from os.path import exists
import shelve
import datetime
# import time
from shutil import copytree

class AlprError(Exception):
    pass


def main():
    ride = datetime.datetime.now().strftime('/mnt/%Y/%m/%d-%H/')
    makedirs(ride, exist_ok=True)
    copytree('/home/video/SafetyVideo', ride)
    shelf = shelve.open(ride + 'data')
    shelf['licenses'] = {}
    alpr = Alpr('eu', '/etc/openalpr/openalpr.conf', '/usr/share/openalpr/runtime_data')
    if not alpr.is_loaded():
        raise AlprError('Couldn\'t load OpenALPR.')
    for pi in ('/home/video/SafetyVideo/SidePi', '/home/video/SafetyVideo/FrontPi'):
        videos = listdir(pi)
        for video in videos:
            with closing(VideoSequence(video)) as sequence:
                oldlicense = None
                for frame in sequence:
                    try:
                        plate = alpr.recognise_ndarray(frame.to_array())['results'][0]['candidates']['plate']
                    except:
                        plate = ''
                    if not plate == oldlicense:
                        shelf['licenses'][video] = plate
                        break
                    oldlicense = plate



if __name__ == "__main__":
    main()
