#! /usr/bin/python
import datetime
import pickle
import numpy as np
import re
import scipy.io as sio

from biosppy.signals import ecg
from flask import Flask, render_template, request, jsonify, flash, redirect
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sklearn.externals import joblib

ALLOWED_EXTENSIONS = ['txt', 'csv', 'mat']

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///formdata.db'
app.secret_key = "janekjestsuperowy"

db = SQLAlchemy(app)

class Formdata(db.Model):
    __tablename__ = 'ekgdata'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.now())
    filename = db.Column(db.String)
    data = db.Column(db.String)

    def __init__(self, filename, data):
        self.filename = filename
        self.data = data


class Matdata(db.Model):
    __tablename__ = 'matdata'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.now())
    filename = db.Column(db.String)
    data = db.Column(db.PickleType)

    def __init__(self, filename, data):
        self.filename = filename
        self.data = data


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/results', methods=['GET', 'POST'])
def results():
    files = db.session.query(Formdata).all()
    files = files + db.session.query(Matdata).all()
    if request.method == 'POST':
        filename = request.form['files']
        records = db.session.query(Formdata).filter_by(filename=filename).first()
        if filename.endswith('.mat'):
            records = db.session.query(Matdata).filter_by(filename=filename).first()
            y = pickle.loads(records.data)['val'][0]
            x = np.linspace(0, 10*1000, len(y))  # 10s 360 Hz
            data = [[int(x[i]), int(y[i])] for i in range(len(y))]
            ts, filtered, rpeaks, templates_ts, templates, heart_rate_ts, heart_rate\
                = calculate_ecg_characteristics(y, 360)
            templates = np.swapaxes(templates,0,1)
            # concatenate with ts and imitate column names for google chart
            templates_data = np.concatenate((templates_ts.reshape(216, 1), templates), axis=1).tolist()
            templates_data = [[str(i) for i in range(len(templates_data[0]))]] + templates_data
            heart_rate_data = [[int(heart_rate_ts[i]), int(heart_rate[i])] for i in range(len(heart_rate))]
            filtered_data = [[int(x[i]), int(filtered[i])] for i in range(len(ts))]
            return render_template('results.html', files=files, data=data, filtered=filtered_data, rpeaks=rpeaks,
                                   templates=templates_data, heart_rate=heart_rate_data)
        elif filename.endswith('.txt'):
            points = records.data.decode('utf-8').split('\n')
            data = [list(map(lambda x: float(x), re.findall(r'[0-9]+', point)[::-1]))
                    for point in points if point.strip() != ""]

        elif filename.endswith('.csv'):
            points = records.data.decode('utf-8').split('\n')[1:]
            data = [list(map(lambda x: float(x), point.split(','))) for point in points if point.strip() != ""]
        else:
            flash('Format pliku nieobsługiwany')
            data = None
    else:
        data = None

    return render_template('results.html', files=files, data=data)


def calculate_ecg_characteristics(ecg_signal, sampling_rate):
    ts, filtered, rpeaks, templates_ts, templates, heart_rate_ts, heart_rate = \
        ecg.ecg(signal=ecg_signal, sampling_rate=sampling_rate, show=False)
    return ts, filtered, rpeaks, templates_ts, templates, heart_rate_ts, heart_rate


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('Nie wybrano pliku')
            return redirect('/upload-form')
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('Nie wybrano pliku')
            return redirect('/upload-form')
        if allowed_file(file.filename):
            if file.filename.endswith('.mat'):
                filename = secure_filename(file.filename)
                file.save('temp/matfile.mat')
                mat = sio.loadmat('temp/matfile.mat')
                mat_blob = pickle.dumps(mat)
                new_record = Matdata(filename=filename, data=mat_blob)
                db.session.add(new_record)
                db.session.commit()
                flash('Wgrano plik')
            else:
                filename = secure_filename(file.filename)
                new_record = Formdata(filename=filename, data=file.read())
                db.session.add(new_record)
                db.session.commit()
            flash('Wgrano plik')
        else:
            flash('Niedozwolony format pliku')
            return redirect('/upload-form')

    return redirect('/upload-form')


@app.route('/upload-form')
def upload_data():
    return render_template('upload.html')


if __name__ == "__main__":
    app.run(debug=True)
    #results()