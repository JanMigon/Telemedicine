#! /usr/bin/python

from flask import Flask, render_template, request, jsonify
import flask_excel as excel

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


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        return jsonify({"result": request.get_array(field_name='file')})
    return render_template('upload.html')


if __name__ == "__main__":
    app.run()