#! /usr/bin/python
import datetime
import os
import re

from flask import Flask, render_template, request, jsonify, flash, redirect
from werkzeug import SharedDataMiddleware
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy

ALLOWED_EXTENSIONS = ['txt', 'csv']

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///formdata.db'
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploads':  app.config['UPLOAD_FOLDER']})
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
        filename = request.form['selectFile']
        data = db.session.query(Formdata).filter_by(filename = filename).data
        if filename.endswith('.txt'):
            points = data.split('\n')
            y_data = [re.findall(r'[0-9]+', point)[0] for point in points]
            x_data = [re.findall(r'[0-9]+', point)[1] for point in points]
        elif filename.endswith('.csv'):
            points = data.split('\n')[1:]
            x_data = [point[0] for point in points]
            y_data = [point[1] for point in points]
        else:
            flash('Format pliku nieobsługiwany')
            x_data = None
            y_data = None
    else:
        x_data = None
        y_data = None
    return render_template('results.html', files=files, x_data=x_data, y_data=y_data)


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