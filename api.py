from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify,send_file,Blueprint,current_app
from flask_session import Session
from flask_login import current_user
from flask_socketio import SocketIO, emit, join_room
from helpers import grabclasses, checkclass, check, connectdb, time_difference, login_hac_required, update_hac, hac_executions,get_hashed_password,check_password,grab_user_id,send_mail_confirm
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
import requests
import botocore
import json
import stat
import os
import sqlite3
import boto3
from dotenv import load_dotenv
import psycopg2
from threading import Thread
from oauthlib.oauth2 import WebApplicationClient
import zipfile
import glob
import shutil 
from zipfile import ZipFile
import bcrypt
from itsdangerous.url_safe import URLSafeTimedSerializer
from flask_mail import Mail, Message
from flask import current_app
from hacapi import hac_api_main
from uuid import uuid4
import binascii

from datetime import date

api = Blueprint('api', __name__, subdomain='api')
www = Blueprint('www', __name__, subdomain='www')

s_api = URLSafeTimedSerializer('Thisisasecret!')

# @api.before_request
# def default_login_required():
#     login_valid = 'username' in session
#     if (request.endpoint and 
#     'static' not in request.endpoint and 
#     not login_valid and 
#     not getattr(current_app.view_functions[request.endpoint], 'is_public', False) ) :
#         flash("Login to Continue with Your Session")
#         return redirect(url_for('api.api_main'))

def api_public_endpoint(function):
    function.is_public = True
    return function

@api_public_endpoint
@api.route('/', methods=["GET","POST"])
def api_main():
    print("Registered Endpoints:", api.view_functions.keys())
    if request.method == "POST":
    #Get password/confirmation information
        form = request.form.get("form-name")
        if form == "signupform":
            agreement_privacy_policy = request.form.get("privacy_policy_agreement")
            email = request.form.get("email")
            username = request.form.get("username")      
            password = request.form.get("password")
            confirmation = request.form.get("confirmation")

            #if information not filled in
            if password == "" or username == "" or email == "":
                formsubmission = False
                flash('Sign Up Form missing an element')
                return render_template("api/api_intro.html")

            #if password does not match confirmation of password
            if password != confirmation:
                formsubmission = False
                flash('Confirmation Password and Password do not match')
                return render_template("api/api_intro.html")

            #checks if email is writen correctly
            emailvalidation = check(email)
            if emailvalidation == "invalid":
                formsubmission = False
                error = "invalid email address"
                flash('invalid email address')
                return render_template("api/api_intro.html")

            #goes to function that connects db
            db_info = connectdb()
            db = db_info[0]
            db_conn = db_info[1]
            #seperate list into db objects

            #checks if email is already in the system | cant be 2 of the same email
            # userinfocursor.execute("SELECT email FROM users WHERE email = ?", (email, ));
            # stored_email = userinfocursor.fetchone()
            db.execute('SELECT * FROM "API_Users" WHERE email = %s', (email, ))
            users = db.fetchall()
            count = len(users)
            if count != 0:
                error = "invalid email address"
                flash('email already has been used')
                return redirect(url_for('api.api_main'))

            #checks if username is already in the system | cant be 2 of same username
            # userinfocursor.execute("SELECT username FROM users WHERE username = ?", (username, ));
            # stored_username = userinfocursor.fetchone()
            # userinfoconnect.close()
            db.execute('SELECT username FROM "API_Users" WHERE username = %s', (username, ))
            users = db.fetchall()
            count = len(users)
            if count != 0:
                error = "invalid email address"
                flash("username already has been used")
                return redirect(url_for('api.api_main'))
            send_mail_confirm(username,email)
            password = get_hashed_password(password)
            null = "null"
            db.execute('INSERT INTO "API_Users"(username, password, email, gradeappusername, gradeapppassword, google_auth, is_confirmed, auth_try_on) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',(username,password,email,null,null,"False",False,datetime.now(timezone.utc)))
            db_conn.commit()
            db.close()
            db_conn.close()
            flash("Verify your email! An Email Has been sent to you!")
            return redirect(url_for('api.api_main'))

        if form == "loginform":
            db_info = connectdb()
            db = db_info[0]
            db_conn = db_info[1]
            email = request.form.get("email")
            password = request.form.get("password")
            #if email is not in system, return error
            db.execute('SELECT * FROM "API_Users" WHERE email=%s',(email,))
            users = db.fetchall()
            count = len(users)
            if count == 0:
                flash("Email and User not found")
                return render_template("api/api_intro.html")
            #grabs the database to see if an account has been google authenticated
            db.execute('SELECT google_auth FROM "API_Users" WHERE email=%s',(email,));
            google_auth = db.fetchall()[0][0]
            db.execute('SELECT password FROM "API_Users" WHERE email=%s',(email,));
            db_password = db.fetchall()[0][0]
            db.execute('SELECT is_confirmed FROM "API_Users" WHERE email=%s',(email,));
            confirmation_status = db.fetchall()[0][0]
            db.execute('SELECT auth_try_on FROM "API_Users" WHERE email=%s',(email,));
            auth_try_on = db.fetchall()[0][0]
            db.execute('SELECT username FROM "API_Users" WHERE email=%s',(email,));
            username = db.fetchall()[0][0]
            if confirmation_status == False:
                if auth_try_on != None:
                    flash("Verify your account with your Email!")
                    send_mail_confirm(username,email)
                    return redirect(url_for('api.api_main'))
                else:
                    flash("Email has already been sent, check your email")
                #else, continue to authenticate password
            verify_password = check_password(password,db_password)
            db.execute('SELECT username FROM "API_Users" WHERE email=%s',(email,));
            username = db.fetchall()
            count = len(username)
            db.close()
            db_conn.close()
            #if password is not the same as the user with the email, return error
            if verify_password != True:
                flash("Password is Incorrect")
                return render_template("api/api_intro.html")
            #set the session
            session["username"] = username[0][0]
            session["hacattendancetimeupdated"] =''
            session["hacgradestimeupdated"] = ''
            session["HacStatus"]=False
            session["runninggethac"] = False
            #Empty bots from Database
            db_info = connectdb()
            db = db_info[0]
            db_conn = db_info[1]
            db.execute('SELECT *  FROM "API_Users" WHERE is_confirmed = %s',("False",))
            users = db.fetchall()
            for user in users:
                if user[9] != None:
                    hours = (datetime.now(timezone.utc).hour-user[9].hour)*60
                    minute_difference = datetime.now(timezone.utc).minute - user[9].minute + hours
                    if minute_difference > 10:
                        db.execute('DELETE FROM "API_Users" WHERE is_confirmed = %s and id=%s',("False",user[0]))
            db_conn.commit()
            db.close()
            db_conn.close()
            return redirect(url_for('api.dashboard'))
    else:
        db_info = connectdb()
        db = db_info[0]
        db_conn = db_info[1]
        db.execute('SELECT *  FROM "API_Users" WHERE is_confirmed = %s',("False",))
        users = db.fetchall()
        for user in users:
            if user[9] != None:
                hours = (datetime.now(timezone.utc).hour-user[9].hour)*60
                minute_difference = datetime.now(timezone.utc).minute - user[9].minute + hours
                if minute_difference > 10:
                    db.execute('DELETE FROM "API_Users" WHERE is_confirmed = %s and id=%s',("False",user[0]))
        db_conn.commit()
        db.close()
        db_conn.close()
        return render_template("api/api_intro.html")
    return render_template("api/api_intro.html")

#try
@api.route("/dashboard", methods=["POST","GET"])
def dashboard():
    page_identifier = "dashboard"
    return render_template("api/dashboard.html",page_identifier = page_identifier)

@api.route("/documentation", methods=["POST","GET"])
def documentation():
    page_identifier = "documentation"
    return render_template("api/documentation.html",page_identifier = page_identifier)

@api_public_endpoint
@api.route('/confirm_email/<token>/<username>', methods=['GET','POST'])
def confirm_email(token,username):
    #checks to see if the token works, if it does, then it 
    try:
        email = s_api.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        flash("Token Has Expired! Try to Login again to try another Email Confirmation!")
        return redirect(url_for('api.index'))
    #updates the database so that it is known that is a verified account
    db_info = connectdb()
    db = db_info[0]
    db_conn = db_info[1]
    db.execute('UPDATE "API_Users" SET is_confirmed=%s WHERE username=%s',("True",username,))
    db_conn.commit()
    db.close()
    db_conn.close()
    flash("Email Confirmed!")
    return redirect(url_for('api.api_main'))

def send_mail_confirm(username,email):
    from app import mail
    #grabs the token, and nessary info to make the email work, and sends
    token = s_api.dumps(email, salt='email-confirm')
    msg = Message('Confirm Email', sender='studysquawk@gmail.com', recipients=[email])
    link = url_for('api.confirm_email', token=token,username=username, _external=True)
    msg.html = render_template("confirm.html",link=link)
    mail.send(msg)
    session["user_id_to_confirm"] = username
    # message = Mail(
    # from_email='studysquawk@gmail.com',
    # to_emails=email,
    # subject='Confirmation Email',
    # html_content=render_template("confirm.html",link=link))
    # try:
    #     sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    #     response = sg.send(message)
    # except Exception as e:
        # print(e.message)


@api_public_endpoint
@api.route('/grades', methods=['GET','POST'])
def grades():
    username = request.args.get('username')
    password = request.args.get('password')
    token = request.args.get('token')
    token_check = check_token(token)
    if token_check == "0":
        grades = hac_executions("grades",True,username,password)
        return grades
    else:
        return token_check

@api_public_endpoint
@api.route('/attendance', methods=['GET','POST'])
def attendance():
    username = request.args.get('username')
    password = request.args.get('password')
    token = request.args.get('token')
    token_check = check_token(token)
    if token_check ==  "0":
        attendance = hac_executions("attendance",True,username,password)
        return attendance
    else:
        return token_check

@api_public_endpoint
@api.route('/both', methods=['GET','POST'])
def both():
    username = request.args.get('username')
    password = request.args.get('password')
    token = request.args.get('token')
    token_check = check_token(token)
    if token_check == "0":
        both = hac_executions("both",True,username,password)
        return both
    else:
        return token_check


@api.route('/create_token', methods=["POST"])
def create_token():
    db_info = connectdb()
    db = db_info[0]
    db_conn = db_info[1]
    #seperate list into db objects
    username = session["username"]
    #checks if email is already in the system | cant be 2 of the same email
    db.execute('SELECT * FROM "API_Users_Tokens" WHERE userid = %s', (username, ));
    usernames = db.fetchall()
    if len(usernames) >= 1:
        flash("There is already a Token Associated with this Account")
        return redirect(url_for('api.dashboard'))
    apikey = str(generate_key())
    db.execute('INSERT INTO "API_Users_Tokens"(userid, apitoken, date_renew, usesnum) VALUES (%s, %s, %s, %s)',(username,apikey,date.today(),0))
    db_conn.commit()
    db.close()
    db_conn.close()
    return render_template("api/apicode_display.html",apikey=apikey)
    
def check_token(token):
    db_info = connectdb()
    db = db_info[0]
    db_conn = db_info[1]
    db.execute('SELECT * FROM "API_Users_Tokens" WHERE apitoken = %s', (token, ));
    token_results = db.fetchall()
    if len(token_results) > 1:
        return "There is an error with this token| A Duplicate"
    elif len(token_results) == 0:
        return "This Token does not exist, Please create a new API Key through https://api.studysquawk.tech/dashboard"
    elif int(token_results[0][4]) > 500:
        return "You have exceeded your limit in StudySquawk API Use"
    else:
        db.execute('SELECT date_renew FROM "API_Users_Tokens" WHERE apitoken = %s', (token, ));
        daterenw = db.fetchone()[0]
        date_compare = (date.today() - daterenw).days
        if date_compare > 31:
            db.execute('UPDATE "API_Users_Tokens" SET usesnum = 0 WHERE apitoken = %s', (token, ))
            db_conn.commit()
        db.execute('UPDATE "API_Users_Tokens" SET usesnum = usesnum+1 WHERE apitoken = %s', (token, ))
        db_conn.commit()
        db.close()
        db_conn.close()
        return "0"
    return "0"

def generate_key():
    return binascii.hexlify(os.urandom(20)).decode()