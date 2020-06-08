#! /usr/bin/python
import datetime
import os
import re

from flask import Flask, render_template, request, jsonify, flash, redirect
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

ALLOWED_EXTENSIONS = ['txt', 'csv']

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
    if request.method == 'POST':
        filename = request.form['files']
        records = db.session.query(Formdata).filter_by(filename=filename).first()
        if filename.endswith('.txt'):
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
        if file and allowed_file(file.filename):
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