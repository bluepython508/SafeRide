import datetime
import shelve
from contextlib import closing
from os import listdir, makedirs, symlink, unlink, chdir
from os.path import exists
from shutil import copy
from subprocess import run

from openalpr import Alpr
from videosequence import VideoSequence


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
    all_videos = listdir('/home/video/SafetyVideo/SidePi')
    for video in all_videos:
        makedirs(ride + video.replace('.mp4', ''), exist_ok=True)
        # copy('/home/video/SafetyVideo/FrontPi/' + video, ride + video.replace('.mp4', '/') + 'FrontPi.mp4')
        copy('/home/video/SafetyVideo/SidePi/' + video, ride + video.replace('.mp4', '/') + 'SidePi.mp4')
    shelf = shelve.open(ride + 'data', writeback=True)
    mainshelf = shelve.open('/mnt/data', writeback=True)
    now = datetime.datetime.now()
    ride_data = {'href': ride.replace('/mnt/', '/ride/'), 'date': ordinal_number(now.day)}
    if 'rides' not in mainshelf:
        mainshelf['rides'] = {}
    if now.year not in mainshelf['rides']:
        mainshelf['rides'][now.year] = {now.month: [ride_data]}
    elif now.strftime('%b') not in mainshelf['rides'][now.year]:
        mainshelf['rides'][now.year][now.strftime('%b')] = [ride_data]
    else:
        mainshelf['rides'][now.year][now.strftime('%b')].append(ride_data)
    mainshelf.sync()
    mainshelf.close()
    shelf['incidents'] = {}
    unlink('/mnt/latest')
    symlink(ride, '/mnt/latest')
    alpr = Alpr('eu', '/etc/openalpr/openalpr.conf', '/usr/share/openalpr/runtime_data')
    if not alpr.is_loaded():
        raise AlprError('Couldn\'t load OpenALPR.')
    videos = listdir('/home/video/SafetyVideo/SidePi')
    chdir('/home/video/SafetyVideo/SidePi')
    for video in videos:
        try:
            with closing(VideoSequence(video)) as sequence:
                oldlicense = None
                for frame in sequence:

                    try:
                        plate = alpr.recognise_ndarray(frame.to_array())['results'][0]['candidates']['plate']
                    except:
                        plate = ''
                    if not plate == oldlicense:
                        shelf['incidents'][video.replace('.mp4', '')] = \
                            {'page': ride.replace('/mnt', '/incidents') + video.replace('.mp4', ''), 'plate': plate}
                        break
                    oldlicense = plate
        except:
            pass

    shelf.sync()
    shelf.close()
    for video in [x for x in listdir('/mnt/latest') if 'data' not in x]:
        chdir('/mnt/latest/{}'.format(video))
        for side in ('SidePi',):
            run('ffmpeg -i {}.mp4 {}.ogg'.format(side, side), shell=True)
            run('ffmpeg -i {}.mp4 {}.webm'.format(side, side), shell=True)


if __name__ == "__main__":
    main()
