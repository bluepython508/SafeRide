from flask import Flask, render_template
from subprocess import run

app = Flask(__name__)


@app.route('/files/<filename>')
def files(filename):
    with open('files/%s' % filename, 'rb') as file:
        return file.read()


@app.route('/videos/<date>/<time>')
def video(date, time):
    with open('/mnt/RideDrive/%s/%s' % (date, time), 'rb') as file:
        return file.read()


@app.route('/ride/<date>')
def ride(date):
    return render_template('ride.html', date=date)


@app.route('/')
def index():
    return render_template('ridepage.html', curyear=2017,
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
                                {'display':2016, 'months':["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                                 'rides':{"Jan": [{"href": "/", "date": "8th"}],
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
                                       {"href": "/", "date": "7th"}],}},
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


app.run(debug=True, host='127.0.0.1', port=5000)
