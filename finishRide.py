from openalpr import Alpr
from contextlib import closing
from videosequence import VideoSequence
from os import listdir, makedirs
from os.path import exists
import shelve
import datetime
import time

class AlprError(Exception):
    pass


def main():
    ride = datetime.datetime.now().strftime('/mnt/%Y/%m/%d-%H')
    makedirs(ride, exist_ok=True)
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
                        license = alpr.recognise_ndarray(frame.to_array())['results'][0]['candidates']['plate']
                    except:
                        license = ''
                    if not license == oldlicense:
                        break
                    oldlicense = license



if __name__ == "__main__":
    main()
