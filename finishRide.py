from openalpr import Alpr
from contextlib import closing
from videosequence import VideoSequence
from os import listdir, makedirs
# from os.path import exists
import shelve
import datetime
# import time
from shutil import copy


class AlprError(Exception):
    pass


def main():
    ride = datetime.datetime.now().strftime('/mnt/%Y/%m/%d-%H/')
    makedirs(ride, exist_ok=True)
    all_videos = listdir('/home/video/SafetyVideo/FrontPi')
    for video in all_videos:
        makedirs(ride + video.replace('.h264', ''), exist_ok=True)
        copy('/home/video/SafetyVideo/FrontPi/' + video, ride + video.replace('.h264', '/') + 'FrontPi.h264')
        copy('/home/video/SafetyVideo/SidePi/' + video, ride + video.replace('.h264', '/') + 'SidePi.h264')
    shelf = shelve.open(ride + 'data', writeback=True)
    mainshelf = shelve.open('/mnt/data', writeback=True)
    mainshelf['rides'].append(ride.replace('/mnt/', ''))
    mainshelf.sync()
    mainshelf.close()
    shelf['licenses'] = {}
    alpr = Alpr('eu', '/etc/openalpr/openalpr.conf', '/usr/share/openalpr/runtime_data')
    if not alpr.is_loaded():
        raise AlprError('Couldn\'t load OpenALPR.')
    videos = listdir('/home/video/SafetyVideo/FrontPi')
    for video in videos:
        with closing(VideoSequence(video)) as sequence:
            oldlicense = None
            for frame in sequence:
                try:
                    plate = alpr.recognise_ndarray(frame.to_array())['results'][0]['candidates']['plate']
                except:
                    plate = ''
                if not plate == oldlicense:
                    shelf['licenses'][video.replace('.h264', '')] = plate
                    break
                oldlicense = plate

    shelf.sync()
    shelf.close()


if __name__ == "__main__":
    main()
