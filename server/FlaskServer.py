from datetime import datetime
from os.path import realpath
from shelve import open as shelf
from subprocess import run

from flask import Flask, render_template, redirect, Response

app = Flask(__name__)

MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def get_basic_dict():
    now = datetime.now()
    shelve = shelf('/mnt/data')
    return dict(curyear=now.year, months=MONTHS[:now.month], rides=shelve['rides'][now.year],
                years=[{'display': year, 'months': MONTHS, 'rides': shelve['rides'][year]} for year in shelve['rides']
                       if not year == now.year])


@app.route('/static/<filename>')
def files(filename):
    with open('static/%s' % filename, 'rb') as file:
        return file.read()


@app.route('/videos/<path:path>')
def video(path):
    with open('/mnt/%s.h264' % path, 'rb') as file:
        return file.read()


@app.route('/incidents/<path:args>/fix', methods=['GET', 'POST'])
def fix(args, request=None):
    shelve = shelf('/mnt/' + '/'.join(args.split('/')[:-1]) + '/data', writeback=True)
    newplate = request.values.get('plate', default=shelve['incidents'][args.split('/')[-1]]['plate'])
    shelve['incidents'][args.split('/')[-1]]['plate'] = newplate
    videos = '/mnt/' + args
    shelve.sync()
    shelve.close()
    if request.method == 'POST':
        return redirect('/incidents/' + args, 303)
    return render_template('fixpage.html', video={'front': videos + '/FrontPi.h264', 'side': videos + '/SidePi.h264'},
                           plate=newplate, videotime=args.split('/')[-1],
                           ** get_basic_dict())


@app.route('/incidents/<path:args>')
def incident(args):
    shelve = shelf('/mnt/' + '/'.join(args.split('/')[:-1]) + '/data')
    videos = '/mnt/' + args
    plate = shelve['incidents'][args.split('/')[-1]]['plate']
    shelve.close()
    return render_template('fixpage.html', video={'front': videos + '/FrontPi.h264', 'side': videos + '/SidePi.h264'},
                           plate=plate, videotime=args.split('/')[-1], url=args,
                           **get_basic_dict())


@app.route('/ride/<path:date>')
def ride(date):
    if date == 'latest':
        path = realpath('/mnt/latest')
    else:
        path = '/mnt/' + date
    shelve = shelf(path + '/data')
    return render_template('ridepage.html', **get_basic_dict(),
                           incidents=shelve['incidents'],
                           ride=(date == 'latest'),
                           date=datetime.now().strftime('%d/%m/%Y')
                           )


@app.route('/')
def index():
    return redirect('/ride/latest', 303)


@app.route('/rideDone')
def upload():
    run("python3", '/home/video/finishRide.py')


@app.route('/main.html')
def main():
    return render_template('main.html', **get_basic_dict())


@app.route('/stylesheet.css')
def style():
    with open('static/stylesheet.css') as stylesheet:
        return Response(stylesheet.read(), mimetype='text/css')


app.run(debug=True, host='127.0.0.1', port=8080)
