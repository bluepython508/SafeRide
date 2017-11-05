from openalpr import Alpr
from contextlib import closing
from videosequence import VideoSequence
from os import listdir, makedirs, symlink, unlink
from os.path import exists
import shelve
import datetime
# import time
from shutil import copy


class AlprError(Exception):
    pass


def ordinal_number(number):
    if str(number)[-1] == '1' and not (number == 11):
        suffix = "st"
    elif str(number)[-1] == '2' and not (number == 12):
        suffix = "nd"
    elif str(number)[-1] == '3' and not (number == 13):
        suffix = "rd"
    else:
        suffix = "th"
    return str(number) + suffix


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
    now = datetime.datetime.now()
    ride_data = {'href': ride.replace('/mnt/', '/ride/'), 'date': ordinal_number(now.day)}
    if not 'rides' in mainshelf:
        mainshelf['rides'] = {}
    if not now.year in mainshelf['rides']:
        mainshelf['rides'][now.year] = {now.month: [ride_data]}
    elif not now.month in mainshelf['rides'][now.year]:
        mainshelf['rides'][now.year][now.month] = [ride_data]
    else:
        mainshelf['rides'][now.year][now.month].append(ride_data)
    mainshelf.sync()
    mainshelf.close()
    shelf['incidents'] = []
    if exists('/mnt/latest'):
        unlink('/mnt/latest')
    symlink(ride, '/mnt/latest')
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
                    shelf['incidents'].append(
                        {'page': ride.replace('/mnt', '') + video.replace('.h264', ''), 'plate': plate})
                    break
                oldlicense = plate

    shelf.sync()
    shelf.close()


if __name__ == "__main__":
    main()
