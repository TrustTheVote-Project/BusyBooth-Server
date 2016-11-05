from . import main
from flask import request, jsonify, redirect, url_for, Flask, send_from_directory, flash, render_template
import re
from ..models import User, WaitTime, PollingBooth
import json
import datetime
from .. import db
import urllib2
import os
import csv
import hashlib

################################################
#   Return format: {"code": X, "data": Y}      #
#   0: all is well                             #
#   1: error                                   #
################################################


# sets which files are allowed by the website.
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] == 'csv'


# Reads the uploaded documents and stores the hashes in our database.
@main.route('/', methods=['GET', 'POST'])
def read_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            flash('Reading File...')
            process_file(file)
            return render_template('done.html')
        else:
            flash('Invalid file type')
    return render_template('main.html')


# Processes the file that they uploaded
def process_file(file):
    reader = csv.DictReader(file)
    for line in reader:
        boothAddress = line['Polling Booth']
        hashVal = line['Hash']
        if(line['PollingPlaceSupervisor'] == '1'):
            polling_place_supervisor = "true"
        else:
            polling_place_supervisor = "false"



        # Creating the new_booth if it needs to be created.
        new_booth = PollingBooth.query.filter_by(address=boothAddress).first()
        if new_booth == None:
            new_booth = PollingBooth(
                address = boothAddress
            )
            db.session.add(new_booth)
            db.session.commit()

        # Creating the new_user if it needs to be created.
        if User.query.filter_by(hashVal=hashVal).first() == None:
            new_user = User(
                hashVal = hashVal,
                polling_booth = new_booth.id,
                is_admin = polling_place_supervisor
            )
            db.session.add(new_user)
            db.session.commit()


# Validating the user. Returns the polling booth information if user exists.
@main.route('/validate_user', methods=['GET', 'POST'])
def validate_user():
    if request.method == "POST":
        hashVal = request.form['hashVal']
        user = User.query.filter_by(hashVal=hashVal).first()
        if  user == None:
            return jsonify({"code": 1, "data": "Cannot find individual"})
        else:
            booth = PollingBooth.query.filter_by(id=user.polling_booth).first()
            return jsonify({"code": 0, "data": {"id": user.polling_booth,
                                                "address": booth.address, 
                                                "is_admin": user.is_admin}});

@main.route('/booths', methods=['GET', 'POST'])
def get_booths():
    if request.method == "POST":
        zipcode = request.form['zip']
        booths = [(booth.address, booth.id) for booth in PollingBooth.query.filter_by(zipCode=zipcode)]
        return jsonify({"code": 0, "data":booths})


# Logging the amount of time a user spent at the polling booth.
@main.route('/log_time/<int:booth_id>', methods=['GET', 'POST'])
def set_time(booth_id):
    if request.method == "POST":
        polling_booth = PollingBooth.query.filter_by(id=booth_id).first()
        if polling_booth:
            # Creating a wait_time
            ## /TODO CHECK FOR REASONABLE INPUT.
            new_waittime = WaitTime(
                elapsed = request.form['elapsed'],
                polling_booth = booth_id
            )
            db.session.add(new_waittime)
            db.session.commit()
            return jsonify({"code": 0, "data": "Submitted Succesfully"})

        return jsonify({"code": 2, "data": "Polling booth does not exist."})
    return jsonify({"code": 2, "data": "You need to send an elapsed time in the post."})


# Get historical wait times from polling_booths
@main.route('/history_wait/<int:booth_id>')
def history_wait(booth_id):
    polling_place = PollingBooth.query.filter_by(id=booth_id).first()
    if polling_place:
        # calculate start of hourly increments of time
        now = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
        past_hours = {}
        for i in range(6):
            past_hours[(now - datetime.timedelta(hours=i)).hour] = []

        for time in polling_place.wait_times:
            if time.end_time.hour in past_hours:
                if time.elapsed and float(time.elapsed).is_integer():
                    past_hours[time.end_time.hour].append(time.elapsed)
        
        averages = []
        for i in range(6):
            hour = (now - datetime.timedelta(hours=i)).hour
            if len(past_hours[hour]) == 0:
                averages.append({"hour": hour, "time": -1})
            else:
                average = sum(past_hours[hour]) / len(past_hours[hour])
                averages.append({"hour": hour, "time": int(average)})
        return jsonify({"code": 0, "data": averages})

    else:
        return jsonify({"code": 2, "data": "Polling booth does not exist."})
    
