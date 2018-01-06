from datetime import datetime
from os.path import realpath
from shelve import open as shelf
from subprocess import run

from flask import Flask, render_template, redirect, Response, abort, send_file, request

app = Flask(__name__)

MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def get_basic_dict():
    now = datetime.now()
    shelve = shelf('/mnt/data', writeback=True)
    if now.year not in shelve['rides']:
        shelve['rides'][now.year] = {}
    shelve.sync()
    shelve.close()
    shelve = shelf('/mnt/data')
    result = dict(curyear=now.year, months=MONTHS[:now.month], rides=shelve['rides'][now.year],
                years=[{'display': year, 'months': MONTHS, 'rides': shelve['rides'][year]} for year in
                       shelve['rides'].keys()
                       if not year == now.year])
    shelve.sync()
    return result


@app.route('/static/<filename>')
def files(filename):
    if '.js' in filename:
        with open('static/%s' % filename, 'rb') as file:
            return Response(file.read(), mimetype='text/javascript')
    with open('static/%s' % filename, 'rb') as file:
        return file.read()


@app.route('/videos/<path:path>')
def video(path):
    return send_file('/mnt/' + path, as_attachment=True)


@app.route('/incidents/<path:args>/fix', methods=['GET', 'POST'])
def fix(args):
    shelve = shelf('/mnt/' + '/'.join(args.split('/')[:-1]) + '/data', writeback=True)
    videos = '/videos/' + args

    if request.method == 'POST':
        newplate = request.values.get('plate', default=shelve['incidents'][args.split('/')[-1]]['plate'])
        shelve['incidents'][args.split('/')[-1]]['plate'] = newplate
        shelve.sync()
        shelve.close()
        return redirect('/incidents/' + args, 303)
    plate = shelve['incidents'][args.split('/')[-1]]['plate']
    shelve.sync()
    shelve.close()
    return render_template('fixpage.html', video={'front': videos + '/FrontPi', 'side': videos + '/SidePi'},
                           plate=plate, videotime=args.split('/')[-1],
                           **get_basic_dict())


@app.route('/incidents/<path:args>')
def incident(args):
    shelve = shelf('/mnt/' + '/'.join(args.split('/')[:-1]) + '/data')
    videos = '/videos/' + args
    plate = shelve['incidents'][args.split('/')[-1]]['plate']
    shelve.close()
    return render_template('videopage.html', video={'front': videos + '/FrontPi', 'side': videos + '/SidePi'},
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
                           incidents=shelve['incidents'].values(),
                           ride=(date == 'latest'),
                           date=path.replace('/mnt/', '')
                           )


@app.route('/')
def index():
    return redirect('/ride/latest', 303)


@app.route('/rideDone')
def upload():
    run("python3 ../finishRide.py", shell=True)
    abort(401)


@app.route('/main.html')
def main():
    return render_template('main.html', **get_basic_dict())


@app.route('/stylesheet.css')
def style():
    with open('static/stylesheet.css') as stylesheet:
        return Response(stylesheet.read(), mimetype='text/css')


@app.route('/bootstrap.css')
def stylebootstrap():
    with open('static/bootstrap.min.css') as stylesheet:
        return Response(stylesheet.read(), mimetype='text/css')

@app.route('/jquery')
def js():
    with open('static/jquery.min.js') as stylesheet:
        return Response(stylesheet.read(), mimetype='text/javascript')



app.run(debug=True, host='0.0.0.0', port=80)
