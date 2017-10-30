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
    shelf = shelve.open(ride + 'data', writeback=True)
    mainshelf = shelve.open('/mnt/data', writeback=True)
    mainshelf['rides'].append(ride.replace('/mnt/', ''))
    mainshelf.sync()
    mainshelf.close()
    shelf['licenses'] = {}
    alpr = Alpr('eu', '/etc/openalpr/openalpr.conf', '/usr/share/openalpr/runtime_data')
    if not alpr.is_loaded():
        raise AlprError('Couldn\'t load OpenALPR.')
    for pi in ('/home/video/SafetyVideo/SidePi', '/home/video/SafetyVideo/FrontPi'):
        # TODO: Restructure so processing both videos at same time
        videos = listdir(pi) + listdir(o)
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

    shelf.sync()
    shelf.close()

if __name__ == "__main__":
    main()
