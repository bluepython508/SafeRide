from flask import Flask, render_template, redirect
from subprocess import run
from os.path import realpath
from shelve import open as shelf
from datetime import datetime

app = Flask(__name__)


def get_basic_dict():
    return dict(curyear=2017,
                months=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                rides={
                    "Jan": [{"href": "/", "date": "8th"}],
                    "Feb": [{"href": "/", "date": "7th"}],
                    "Mar": [{"href": "/", "date": "7th"}],
                    "Apr": [{"href": "/", "date": "7th"}],
                    "May": [{"href": "/", "date": "7th"}],
                    "Jun": [{"href": "/", "date": "7th"}],
                    "Jul": [{"href": "/", "date": "7th"}],
                    "Aug": [{"href": "/", "date": "7th"}],
                    "Sep": [{"href": "/", "date": "7th"}],
                    "Oct": [{"href": "/", "date": "7th"}],
                    "Nov": [{"href": "/", "date": "7th"}],
                    "Dec": [{"href": "/", "date": "7th"}, {"href": "/", "date": "7th"},
                            {"href": "/", "date": "7th"}],
                },
                years=[
                    {'display': 2016,
                     'months': ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                     'rides': {"Jan": [{"href": "/", "date": "8th"}],
                               "Feb": [{"href": "/", "date": "7th"}],
                               "Mar": [{"href": "/", "date": "7th"}],
                               "Apr": [{"href": "/", "date": "7th"}],
                               "May": [{"href": "/", "date": "7th"}],
                               "Jun": [{"href": "/", "date": "7th"}],
                               "Jul": [{"href": "/", "date": "7th"}],
                               "Aug": [{"href": "/", "date": "7th"}],
                               "Sep": [{"href": "/", "date": "7th"}],
                               "Oct": [{"href": "/", "date": "7th"}],
                               "Nov": [{"href": "/", "date": "7th"}],
                               "Dec": [{"href": "/", "date": "7th"}, {"href": "/", "date": "7th"},
                                       {"href": "/", "date": "7th"}], }},
                    {'display': 2015,
                     'months': ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
                                "Dec"],
                     'rides': {"Jan": [{"href": "/", "date": "8th"}],
                               "Feb": [{"href": "/", "date": "7th"}],
                               "Mar": [{"href": "/", "date": "7th"}],
                               "Apr": [{"href": "/", "date": "7th"}],
                               "May": [{"href": "/", "date": "7th"}],
                               "Jun": [{"href": "/", "date": "7th"}],
                               "Jul": [{"href": "/", "date": "7th"}],
                               "Aug": [{"href": "/", "date": "7th"}],
                               "Sep": [{"href": "/", "date": "7th"}],
                               "Oct": [{"href": "/", "date": "7th"}],
                               "Nov": [{"href": "/", "date": "7th"}],
                               "Dec": [{"href": "/", "date": "7th"}, {"href": "/", "date": "7th"},
                                       {"href": "/", "date": "7th"}], }},
                    {'display': 2014,
                     'months': ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
                                "Dec"],
                     'rides': {"Jan": [{"href": "/", "date": "8th"}],
                               "Feb": [{"href": "/", "date": "7th"}],
                               "Mar": [{"href": "/", "date": "7th"}],
                               "Apr": [{"href": "/", "date": "7th"}],
                               "May": [{"href": "/", "date": "7th"}],
                               "Jun": [{"href": "/", "date": "7th"}],
                               "Jul": [{"href": "/", "date": "7th"}],
                               "Aug": [{"href": "/", "date": "7th"}],
                               "Sep": [{"href": "/", "date": "7th"}],
                               "Oct": [{"href": "/", "date": "7th"}],
                               "Nov": [{"href": "/", "date": "7th"}],
                               "Dec": [{"href": "/", "date": "7th"}, {"href": "/", "date": "7th"},
                                       {"href": "/", "date": "7th"}], }},
                    {'display': 2013,
                     'months': ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
                                "Dec"],
                     'rides': {"Jan": [{"href": "/", "date": "8th"}],
                               "Feb": [{"href": "/", "date": "7th"}],
                               "Mar": [{"href": "/", "date": "7th"}],
                               "Apr": [{"href": "/", "date": "7th"}],
                               "May": [{"href": "/", "date": "7th"}],
                               "Jun": [{"href": "/", "date": "7th"}],
                               "Jul": [{"href": "/", "date": "7th"}],
                               "Aug": [{"href": "/", "date": "7th"}],
                               "Sep": [{"href": "/", "date": "7th"}],
                               "Oct": [{"href": "/", "date": "7th"}],
                               "Nov": [{"href": "/", "date": "7th"}],
                               "Dec": [{"href": "/", "date": "7th"}, {"href": "/", "date": "7th"},
                                       {"href": "/", "date": "7th"}], }}
                ])


@app.route('/files/<filename>')
def files(filename):
    with open('files/%s' % filename, 'rb') as file:
        return file.read()


@app.route('/videos/<path:path>')
def video(path):
    with open('/mnt/%s.h264' % path, 'rb') as file:
        return file.read()


@app.route('/incidents/<path:args>')
def incident(args):
    videos = '/mnt/' + args
    return render_template('videopage.html', video={'front': videos + '/FrontPi.h264', 'side': videos + '/SidePi.h264'},
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


@app.route('/favicon.ico')
def favicon():
    with open("files/favicon.ico", 'rb') as fav:
        return fav.read()


@app.route('/style.css')
def stylesheet():
    with open("files/stylesheet.css", 'r') as style:
        return style.read()


@app.route('/main.html')
def main():
    return render_template('main.html', **get_basic_dict())


app.run(debug=True, host='127.0.0.1', port=8080)
