#! /usr/bin/python

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/results')
def results():
    return render_template('results.html')


@app.route('/upload')
def upload():
    return render_template('upload.html')

if __name__ == "__main__":
    app.run()