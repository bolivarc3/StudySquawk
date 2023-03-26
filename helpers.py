import sqlite3
from datetime import datetime,timedelta
import re
import os
import requests
import urllib.parse
from flask import redirect, render_template, request, session
from functools import wraps
import csv
import psycopg2

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def login_hac_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        db_info = connectdb()
        db = db_info[0]
        db_conn = db_info[1]
        username = session["user_id"]
        db.execute('SELECT * FROM "Users" WHERE username = %s', (username, ))
        user_info = db.fetchone()
        grade_viewer_username = user_info[4]
        grade_viewer_password = user_info[5]
        db.close()
        db_conn.close()
        if grade_viewer_username=="null":
            return redirect("/grade_viewer_signup")
        return f(*args, **kwargs)
    return decorated_function


def connectdb():
    ENV = os.environ.get('APPLICATION_ENV')
    if ENV == 'dev':
        conn = psycopg2.connect(
            host=os.environ.get('POSTGRES_DEV_HOSTNAME'),
            database=os.environ.get('POSTGRES_DEV_DB_NAME'),
            user=os.environ.get('POSTGRES_DEV_USERNAME'),
            password=os.environ.get('POSTGRES_DEV_PASSWORD')
        )
    else:
        conn = psycopg2.connect(
            host=os.environ.get('RDS_HOSTNAME'),
            database=os.environ.get('RDS_DB_NAME'),
            user=os.environ.get('RDS_USERNAME'),
            password= os.environ.get('RDS_PASSWORD')
        )
    cursor = conn.cursor()
    list = [cursor,conn]
    return list;



def grabclasses():
    #grabs all the classes and converts it to an array
    courses = []
    with open('databases/classes.csv', newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            if row[2] != "name":
                courses.append(row[2])
    return courses;


def checkclass(course, courses):
    availible = False
    for i in range(len(courses)):
        print(courses[i])
        if course == courses[i]:
            availible = True
    if availible != True:
        return False;

def check(email):

    # pass the regular expression
    # and the string into the fullmatch() method
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, email)):
        print("Valid Email")
        return("valid")

    else:
        print("Invalid Email")
        return("invalid")


def time_difference(postedtime,posteddate):
    now = datetime.now()
    nowdate = now.strftime("%m/%d/%Y")
    nowdate = datetime.strptime(nowdate,"%m/%d/%Y")
    nowtime = now.strftime("%H:%M:%S")
    nowtime = datetime.strptime(nowtime,"%H:%M:%S")
    postedtime = datetime.strptime(postedtime, "%H:%M:%S")
    print(nowtime)
    print(postedtime)
    differencetime = nowtime - postedtime
    print(differencetime)
    seconds = differencetime.seconds
    hours = (seconds//3600)-18
    minutes = (seconds//60)%60
    seconds = seconds%60
    differencetime = ""
    if hours != 0:
        differencetime = str(hours) + " hours "
    if minutes != 0:
        differencetime = str(differencetime) + str(minutes) + " minutes "
    if seconds != 0:
        differencetime = differencetime + str(seconds) + " seconds "
    print(differencetime)

def upload(filespath,filename):
    if request.method == 'POST':
        img = request.files['file']
        if img:
            filename = secure_filename(img.filename)
            s3.upload_file(
                Bucket = BUCKET_NAME,
                Filename=filename,
                Key = filename
            )
            msg = "Upload Done ! "
    return render_template("file_upload_to_s3.html",msg =msg)
    
