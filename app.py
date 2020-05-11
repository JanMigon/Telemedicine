#! /usr/bin/python

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wyniki.db'
#
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)
# manager = Manager(app)
#
# manager.add_command('db', MigrateCommand)


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

