import sqlite3
from datetime import datetime,timedelta
import re
import os
import requests
import urllib.parse
from flask import redirect, render_template, request, session
from app import session
from datetime import datetime, timezone
from functools import wraps
import csv
import psycopg2
import bcrypt
import json
from hacapi import hac_api_main

def login_hac_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        db_info = connectdb()
        db = db_info[0]
        db_conn = db_info[1]
        username = session["username"]
        db.execute('SELECT * FROM "Users" WHERE username = %s', (username, ))
        user_info = db.fetchone()
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
        if course == courses[i]:
            availible = True
    if availible != True:
        return False;

def check(email):

    # pass the regular expression
    # and the string into the fullmatch() method
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, email)):
        return("valid")

    else:
        return("invalid")

def grab_user_id(username):
    db_info = connectdb()
    db = db_info[0]
    db_conn = db_info[1]
    db.execute('SELECT id FROM "Users" WHERE username = %s', (username, ))
    user_id = db.fetchone()[0]
    db.close()
    db_conn.close()
    return user_id

def time_difference(postedtime,posteddate):
    now = datetime.now()
    nowdate = now.strftime("%m/%d/%Y")
    nowdate = datetime.strptime(nowdate,"%m/%d/%Y")
    nowtime = now.strftime("%H:%M:%S")
    nowtime = datetime.strptime(nowtime,"%H:%M:%S")
    postedtime = datetime.strptime(postedtime, "%H:%M:%S")
    differencetime = nowtime - postedtime
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


def update_hac():
    username = session["user_id_hac"]
    password = session["password_hac"]
    if session["error"] != True:
        current_time = datetime.now(timezone.utc)
        if session["hacgradestimeupdated"] == '':
            session["hacgradestimeupdated"] = datetime.now(timezone.utc)
            hac_executions('grades',username,password)
        if  session["error"] != True:
            duration = current_time - session["hacgradestimeupdated"]
            duration_in_s = duration.total_seconds()  
            minutes = divmod(duration_in_s, 60)[0]
            if minutes > 5:
                session["hacgradestimeupdated"] = datetime.now(timezone.utc)
                hac_executions('grades',username,password)
        if session["hacattendancetimeupdated"] == '':
            session["hacattendancetimeupdated"] = datetime.now(timezone.utc)
            hac_executions('attendance',username,password)
        if  session["error"] != True:
            duration = current_time - session["hacattendancetimeupdated"]
            duration_in_s = duration.total_seconds()  
            minutes = divmod(duration_in_s, 60)[0]
            if minutes >  5:
                session["hacattendancetimeupdated"] = datetime.now(timezone.utc)
                hac_executions('attendance',username,password)
        
    

def hac_executions(runfunction,username,password):
    print("running",runfunction)
    if username != "NULL" and password != "NULL":
        if session["runninggethac"] == False:
            session["runninggethac"] = True
            if runfunction == "both":
                data = hac_api_main("both",username, password)
                session["hacattendance"] = data[3]
                session["hacattendancetimeupdated"] = datetime.now(timezone.utc)
                class_names = data[0]

                grades_request = {"class_names":data[0],"grade_summary":data[1],"assignment_grades":data[2]}
                for course in class_names:
                    if course.find('/')!=-1:
                        new_course_name  = course.replace("/","|")
                        grades_request["class_names"].remove(course)
                        grades_request["class_names"].append(new_course_name)
                        grades_request["grade_summary"][new_course_name] = grades_request["grade_summary"][course]
                        grades_request["assignment_grades"][new_course_name] = grades_request["assignment_grades"][course]
                        del grades_request["grade_summary"][course]
                        del grades_request["assignment_grades"][course]
                session["hacgrades"] = grades_request
                session["hacgradestimeupdated"] = datetime.now(timezone.utc)
            elif runfunction == "attendance":
                attendance_data = hac_api_main("attendance",username, password)
                session["hacattendance"] = attendance_data
                session["hacattendancetimeupdated"] = datetime.now(timezone.utc)
            else:
                grades_data = hac_api_main("grades",username, password)

                class_names = grades_data[0]

                grades_request = {"class_names":grades_data[0],"grade_summary":grades_data[1],"assignment_grades":grades_data[2]}
                for course in class_names:
                    if course.find('/')!=-1:
                        new_course_name  = course.replace("/","|")
                        grades_request["class_names"].remove(course)
                        grades_request["class_names"].append(new_course_name)
                        grades_request["grade_summary"][new_course_name] = grades_request["grade_summary"][course]
                        grades_request["assignment_grades"][new_course_name] = grades_request["assignment_grades"][course]
                        del grades_request["grade_summary"][course]
                        del grades_request["assignment_grades"][course]
                session["hacgrades"] = grades_request
                session["hacgradestimeupdated"] = datetime.now(timezone.utc)
            return 0
    else:
        return 1
    session["runninggethac"] = False

def attendance_update(username, password):
    params = {"username":username,"password":password}
    params = json.dumps(params)
    headers = {'Content-Type': 'application/json'}
    attedance_request = requests.post("https://2o5vn3b0m9.execute-api.us-east-1.amazonaws.com/attendance/"+ username +"/" +password)
    #converts output to a json format(dictionary)
    attendance_data = attedance_request.json()
    if "error" in attendance_data.keys():
        session["error"] = True
    session["hacattendance"] = attendance_data
    session["hacattendancetimeupdated"] = datetime.now(timezone.utc)

def grades_update(username, password):
    params = {"username":username,"password":password}
    params = json.dumps(params)
    headers = {'Content-Type': 'application/json'}
    grades_request = requests.post("https://2o5vn3b0m9.execute-api.us-east-1.amazonaws.com/grades/" + username +"/" +password)
    grades_request = grades_request.json()
    print(grades_request)
    if "error" in grades_request.keys():
        session["error"] = True
    else:
        class_names = list(grades_request["class_names"])
        for course in class_names:
            if course.find('/')!=-1:
                new_course_name  = course.replace("/","|")
                grades_request["class_names"].remove(course)
                grades_request["class_names"].append(new_course_name)
                grades_request["grade_summary"][new_course_name] = grades_request["grade_summary"][course]
                grades_request["assignment_grades"][new_course_name] = grades_request["assignment_grades"][course]
                del grades_request["grade_summary"][course]
                del grades_request["assignment_grades"][course]
        session["hacgrades"] = grades_request
        session["hacgradestimeupdated"] = datetime.now(timezone.utc)

def get_hashed_password(plain_text_password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())

def check_password(plain_text_password, hashed_password):
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(plain_text_password, hashed_password)