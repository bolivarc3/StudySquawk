from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify,send_file
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room
from helpers import grabclasses, checkclass, check, connectdb, time_difference, login_hac_required, update_hac, hac_executions,get_hashed_password,check_password,grab_user_id
from werkzeug.utils import secure_filename
from sqlalchemy import *
from flask_sqlalchemy import SQLAlchemy
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
from functools import wraps
from flask_migrate import Migrate
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import redis
from datetime import timedelta, time
from bs4 import BeautifulSoup
import platform
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail



#change
app = Flask(__name__)
load_dotenv()
s3 = boto3.client('s3',
    aws_access_key_id = os.environ.get('AWS_S3_ACCESS_KEY'),
    aws_secret_access_key = os.environ.get('AWS_S3_SECRET_ACCESS_KEY'),
        )
app.secret_key = os.urandom(100)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_COOKIE_SECURE'] = True  # Ensure cookies are only sent over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent client-side JavaScript from accessing cookies
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_REDIS'] = redis.from_url(os.environ.get('SESSION_REDIS'))
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
Session(app)
app.config["SESSION_PERMANENT"] = False
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USE_TLS'] = True
mail = Mail(app)
socketio = SocketIO(app)

app.config.from_pyfile('config.cfg')
s = URLSafeTimedSerializer('Thisisasecret!')

ENV = os.environ.get('APPLICATION_ENV')
if ENV == 'dev':
    conn = psycopg2.connect(
        host=os.environ.get('POSTGRES_DEV_HOSTNAME'),
        database=os.environ.get('POSTGRES_DEV_DB_NAME'),
        user=os.environ.get('POSTGRES_DEV_USERNAME'),
        password=os.environ.get('POSTGRES_DEV_PASSWORD')
    )
    cursor = conn.cursor()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}:{}/{}'.format(
        os.environ.get('POSTGRES_DEV_USERNAME'),
        os.environ.get('POSTGRES_DEV_PASSWORD'),
        os.environ.get('POSTGRES_DEV_HOSTNAME'),
        os.environ.get('POSTGRES_DEV_PORT'),
        os.environ.get('POSTGRES_DEV_DB_NAME')
    )
    BUCKET_NAME='studyist-dev'
    DEBUG_STATUS=True
else:
    conn = psycopg2.connect(
        host=os.environ.get('RDS_HOSTNAME'),
        database=os.environ.get('RDS_DB_NAME'),
        user=os.environ.get('RDS_USERNAME'),
        password= os.environ.get('RDS_PASSWORD')
    )
    cursor = conn.cursor()
    BUCKET_NAME='studyist'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}:{}/{}?sslmode=require'.format(
        os.environ.get('RDS_USERNAME'),
        os.environ.get('RDS_PASSWORD'),
        os.environ.get('RDS_HOSTNAME'),
        os.environ.get('RDS_PORT'),
        os.environ.get('RDS_DB_NAME')
    )
    DEBUG_STATUS=False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_creation = SQLAlchemy(app)
app.app_context().push()
migrate = Migrate(app, db_creation)
from models import Users, posts, images, files, replies, replyfiles, replyimages, materials
db_creation.create_all()
db_creation.session.commit()

#needed info for google authentication
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
client = WebApplicationClient(GOOGLE_CLIENT_ID)

UPLOAD_FOLDER = '/Studyist/userfiles'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from aws import upload, download_file, download_folder, delete_aws_files,delete_aws_files_post
# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.errorhandler(404)
def page_not_found(e):
    error = "Page not found, return to the bright side"
    url = "/homepage"
    return render_template('error.html', error = error, url = url), 404

@app.before_request
def default_login_required():
    login_valid = 'username' in session
    if (request.endpoint and 
        'static' not in request.endpoint and 
        not login_valid and 
        not getattr(app.view_functions[request.endpoint], 'is_public', False) ) :
        flash("Login to Continue with Your Session")
        return redirect(url_for("index"))

def public_endpoint(function):
    function.is_public = True
    return function

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

#the intro homepage for the user
#test1
@public_endpoint
@app.route("/", methods=["GET", "POST"])
def index():
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
                return render_template("intro.html")

            #if password does not match confirmation of password
            if password != confirmation:
                formsubmission = False
                flash('Confirmation Password and Password do not match')
                return render_template("intro.html")

            #checks if email is writen correctly
            emailvalidation = check(email)
            if emailvalidation == "invalid":
                formsubmission = False
                error = "invalid email address"
                flash('invalid email address')
                return render_template("intro.html")

            #goes to function that connects db
            db_info = connectdb()
            db = db_info[0]
            db_conn = db_info[1]
            #seperate list into db objects

            #checks if email is already in the system | cant be 2 of the same email
            # userinfocursor.execute("SELECT email FROM users WHERE email = ?", (email, ));
            # stored_email = userinfocursor.fetchone()
            db.execute('SELECT * FROM "Users" WHERE email = %s', (email, ))
            users = db.fetchall()
            count = len(users)
            if count != 0:
                error = "invalid email address"
                flash('email already has been used')
                return redirect(url_for('index'))

            #checks if username is already in the system | cant be 2 of same username
            # userinfocursor.execute("SELECT username FROM users WHERE username = ?", (username, ));
            # stored_username = userinfocursor.fetchone()
            # userinfoconnect.close()
            db.execute('SELECT username FROM "Users" WHERE username = %s', (username, ))
            users = db.fetchall()
            count = len(users)
            if count != 0:
                error = "invalid email address"
                flash("username already has been used")
                return redirect(url_for('index'))
            send_mail_confirm(username,email)
            password = get_hashed_password(password)
            null = "null"
            db.execute('INSERT INTO "Users"(username, password, email, gradeappusername, gradeapppassword, google_auth, is_confirmed, auth_try_on) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',(username,password,email,null,null,"False",False,datetime.now(timezone.utc)))
            db_conn.commit()
            db.close()
            db_conn.close()
            flash("Verify your email! An Email Has been sent to you!")
            return redirect("/")

        if form == "loginform":
            db_info = connectdb()
            db = db_info[0]
            db_conn = db_info[1]
            email = request.form.get("email")
            password = request.form.get("password")
            #if email is not in system, return error
            db.execute('SELECT * FROM "Users" WHERE email=%s',(email,))
            users = db.fetchall()
            count = len(users)
            if count == 0:
                flash("Email and User not found")
                return render_template("intro.html")
            #grabs the database to see if an account has been google authenticated
            db.execute('SELECT google_auth FROM "Users" WHERE email=%s',(email,));
            google_auth = db.fetchall()[0][0]
            db.execute('SELECT password FROM "Users" WHERE email=%s',(email,));
            db_password = db.fetchall()[0][0]
            db.execute('SELECT is_confirmed FROM "Users" WHERE email=%s',(email,));
            confirmation_status = db.fetchall()[0][0]
            db.execute('SELECT auth_try_on FROM "Users" WHERE email=%s',(email,));
            auth_try_on = db.fetchall()[0][0]
            db.execute('SELECT username FROM "Users" WHERE email=%s',(email,));
            username = db.fetchall()[0][0]
            if confirmation_status == False:
                if auth_try_on != None:
                    flash("Verify your account with your Email!")
                    send_mail_confirm(username,email)
                    return redirect(url_for("index"))
                else:
                    flash("Email has already been sent, check your email")
            #if an account with the same email has
            if google_auth == "True":
                #if the password is not already set to something
                if db_password == "null":
                    session["attempted_password"] = password
                    flash("redirecting to the login")
                    return redirect(url_for("login"))
                #else, continue to authenticate password
            verify_password = check_password(password,db_password)
            db.execute('SELECT username FROM "Users" WHERE email=%s',(email,));
            username = db.fetchall()
            count = len(username)
            db.close()
            db_conn.close()
            #if password is not the same as the user with the email, return error
            if verify_password != True:
                flash("Password is Incorrect")
                return render_template("intro.html")
            #set the session
            session["username"] = username[0][0]
            session["hacattendancetimeupdated"] =''
            session["hacgradestimeupdated"] =''
            return redirect(url_for("studyist"))
    else:
        db_info = connectdb()
        db = db_info[0]
        db_conn = db_info[1]
        db.execute('SELECT *  FROM "Users" WHERE is_confirmed = %s',("False",))
        users = db.fetchall()
        for user in users:
            if user[9] != None:
                hours = (datetime.now(timezone.utc).hour-user[9].hour)*60
                minute_difference = datetime.now(timezone.utc).minute - user[9].minute + hours
                print(minute_difference)
                if minute_difference > 10:
                    db.execute('DELETE FROM "Users" WHERE is_confirmed = %s and id=%s',("False",user[0]))
        db_conn.commit()
        db.close()
        db_conn.close()
        return render_template("intro.html")
    return render_template("intro.html")

@public_endpoint
@app.route('/confirm_email/<token>/<username>', methods=['GET','POST'])
def confirm_email(token,username):
    #checks to see if the token works, if it does, then it 
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        flash("Token Has Expired! Try to Login again to try another Email Confirmation!")
        return redirect(url_for('index'))
    #updates the database so that it is known that is a verified account
    db_info = connectdb()
    db = db_info[0]
    db_conn = db_info[1]
    db.execute('UPDATE "Users" SET is_confirmed=%s WHERE username=%s',("True",username,))
    db_conn.commit()
    db.close()
    db_conn.close()
    flash("Email Confirmed!")
    return redirect(url_for('index'))

def send_mail_confirm(username,email):
    #grabs the token, and nessary info to make the email work, and sends
    token = s.dumps(email, salt='email-confirm')
    # msg = Message('Confirm Email', sender='studysquawk@gmail.com', recipients=[email])
    link = url_for('confirm_email', token=token,username=username, _external=True)
    # msg.html = render_template("confirm.html",link=link)
    # mail.send(msg)
    session["user_id_to_confirm"] = username
    message = Mail(
    from_email='studysquawk@gmail.com',
    to_emails=email,
    subject='Confirmation Email',
    html_content=render_template("confirm.html",link=link))
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
    except Exception as e:
        print(e.message)

@public_endpoint
@app.route('/login')
def login():
    session["hacattendancetimeupdated"] =''
    session["hacgradestimeupdated"] =''
        # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@public_endpoint
@app.route("/login/callback")
def callback():
    session["hacattendancetimeupdated"] =''
    session["hacgradestimeupdated"] =''
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400
    #grabs the database to fetch the user with the email that the user had in the google account
    db_info = connectdb()
    db = db_info[0]
    db_conn = db_info[1]
    # Doesn't exist? Add it to the database.
    db.execute('SELECT * FROM "Users" WHERE email = %s', (users_email, ))
    users = db.fetchall()
    count = len(users)
    
    #checks if username is already in the system | cant be 2 of same username
    if count == 0:
        db.execute('SELECT username FROM "Users" WHERE username = %s', (users_name, ))
        users = db.fetchall()
        count = len(users)
        if count == 0:
            null = "null"
            db.execute('INSERT INTO "Users"(username, password, email, gradeappusername, gradeapppassword, google_auth, is_confirmed, auth_try_on) VALUES (%s, %s, %s, %s, %s, %s, %s)',(users_name,null,users_email,null,null,"True",True,True))
            # Send user back to homepage
            db_conn.commit()
            db.close()
            db_conn.close()
            return redirect(url_for("studyist"))
    else:
        db.execute('SELECT username FROM "Users" WHERE email = %s', (users_email, ))
        users = db.fetchall()
        users_name = users[0][0]
    session["username"] = users_name
    #adds the attempted password if the user doesn't already have one
    if "attempted_password" in session:
        db_info = connectdb()
        db = db_info[0]
        db_conn = db_info[1]
        password = get_hashed_password(session["attempted_password"])
        db.execute('UPDATE "Users" SET password=%s, google_auth=%s WHERE username=%s',(password,"True",session["username"]))
    db_conn.commit()
    db.close()
    db_conn.close()
    session["hacattendancetimeupdated"] =''
    session["hacgradestimeupdated"] =''
    return redirect(url_for("studyist"))


@app.route("/homepage", methods=["GET", "POST"])
def studyist():
    page_identifier = "homepage"
    courses = grabclasses()
    if request.method == "POST":
        #looks in the classes db to find all of the classes
        course = request.form.get("name")
        courseavailible = checkclass(course, courses)
        if courseavailible == False:
            flash('Class is not availible. Select Class from Options')
            return redirect(url_for('studyist'))
        #checks if the course requested is the same as one in the array
        return redirect(course)
    else:
        db_info = connectdb()
        db = db_info[0]
        db_conn = db_info[1]
        db.execute('SELECT * FROM "posts" ORDER BY date DESC, time DESC')
        postings = db.fetchall()
        db_conn.close()
        #return object looking like <posts> which is an object
        #index into it and . insert what you are looking for
        course = "homepage"
        page_identifier = "homepage"
        return render_template("homepage.html", page_identifier = page_identifier, course = course, courses = courses,postings = postings)


@app.route('/<course>', methods=["GET", "POST"])
def course(course):
    page_identifier = course

    #grabs the classes and checks if class is a class in db
    courses = grabclasses()
    courseavailible = checkclass(course, courses)
    userid = grab_user_id(session["username"])

    #if the class is not in the list, it will render an apology
    if courseavailible == False:
        error = 'Class is not availible. Select Class from Options'
        url = "/homepage"
        return render_template("error.html", error = error, url = url)
    #if there is a post request, it will redirect to a page where you can post
    # else it will render the course page requested
    checkclass(course, courses)

    if request.method == "POST":
        #gathers information for database entry
        title = request.form.get("title")
        title = str(title)
        body = request.form.get("text")
        body = str(body)
        username = session["username"]
        now = datetime.now()
        date = now.strftime("%m/%d/%Y")
        time = now.strftime("%H:%M:%S")

        #if there is no inputs, return an error
        if title == "" or body == "":
            flash('No input to the post')
            return redirect(request.url)

        #check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        filedata = request.files.getlist("file")
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        db_info = connectdb()
        db = db_info[0]
        db_conn = db_info[1]
        db.execute('SELECT * FROM "posts"')
        id = len(db.fetchall())+1
        #grabs the postid
        # #makes a new folder for the images. This makes it so that it can conserve it's name
        filespath = "userfiles/" + str(id)
        for file in filedata:
            if file.filename != "":
                split_tup = os.path.splitext(file.filename)

                # extract the file name and extension
                file_name = split_tup[0]
                file_extension = split_tup[1]
                imagefileextensions = ['.png', '.PNG', '.jpg', '.jpeg', '.bmp' '.tiff', '.gif', '.webp']
                #checks if image
                if file_extension in imagefileextensions:
                    filename = secure_filename(file.filename)
                    fileupload = upload(filespath,filename,file)
                    db.execute('INSERT INTO "images"(postid, images,user_id) VALUES (%s, %s, %s)',(id,filename,userid,))
                    db_conn.commit()
                else:
                    filename = secure_filename(file.filename)
                    fileupload = upload(filespath,filename,file)
                    db.execute('INSERT INTO "files"(postid, files,user_id) VALUES (%s, %s,%s)',(id,filename,userid,))
                    db_conn.commit()
        db.execute('INSERT INTO "posts"(postid, course, username, title, body, time, date, user_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)',(id, course, username, title, body, time, date, userid,))            
        db_conn.commit()
        db_conn.close()
        db.close()
        return redirect(url_for('course', course = course))
    db_info = connectdb()
    db = db_info[0]
    db_conn = db_info[1]
    db.execute('SELECT * FROM "posts" WHERE course=%s ORDER BY date DESC, time DESC',(course,))
    postings = db.fetchall()
    return render_template("coursemain.html", page_identifier=page_identifier, course = course, courses = courses, postings = postings)


@app.route('/<course>/postcreation', methods=["GET", "POST"])

def post(course):
    page_identifier= course
    return render_template("post.html", course = course, page_identifier=page_identifier)


@app.route('/<course>/post/<postid>', methods=["GET", "POST"])
def viewpost(course, postid):
    userid = grab_user_id(session["username"])
    page_identifier = course
    postid = int(postid)

    if request.method == "POST":
        formname = request.form.get("formname")
        formname = str(formname)

        if formname == "replyform":
            title = request.form.get("title")
            title = str(title)
            body = request.form.get("text")
            body = str(body)
            username = session["username"]
            now = datetime.now()
            now = datetime.now()
            date = now.strftime("%m/%d/%Y")
            time = now.strftime("%H:%M:%S")
            if title == "" or body == "":
                error = "No input to the post"
                flash('No input to the post')
                return redirect(request.url)
            db_info = connectdb()
            db = db_info[0]
            db_conn = db_info[1]
            db.execute('SELECT * from "replies" ORDER BY date DESC, time DESC')
            repliesquery = db.fetchall()
            replieslength = len(repliesquery)
            id = replieslength + 1

            db.execute('INSERT INTO "replies"(replyid, postid, course, username, title, body, time, date,user_id) VALUES(%s,%s, %s, %s,%s, %s, %s,%s,%s)',(id, postid, course, username, title, body, time, date,userid,))
            db_conn.commit()
            file = request.files['file']
            filedata = request.files.getlist("file")
            filespath = "userfiles-replies/" + str(id)
            #for every file, it will save it
            for file in filedata:
                if file.filename != "":
                    split_tup = os.path.splitext(file.filename)

                    # extract the file name and extension
                    file_name = split_tup[0]
                    file_extension = split_tup[1]
                    imagefileextensions = ['.png', 'PNG', '.jpg', '.jpeg','.JPG', '.bmp' '.tiff', '.gif','.webp']
                    #checks if image
                    if file_extension in imagefileextensions:
                        filename = secure_filename(file.filename)
                        fileupload = upload(filespath,filename,file)
                        db.execute('INSERT INTO "replyimages"(replyid, postid, images,user_id) VALUES (%s, %s, %s, %s)',(id,postid,filename,userid,))
                        db_conn.commit()

                    else:
                        filename = secure_filename(file.filename)
                        fileupload = upload(filespath,filename,file)
                        db.execute('INSERT INTO "replyfiles"(replyid, postid, files,user_id) VALUES (%s, %s, %s, %s)',(id,postid,filename,userid))
                        db_conn.commit()
            db.close()
            db_conn.close()

        return redirect(url_for('viewpost', page_identifier = page_identifier, course = course, postid = postid))


    #grab all of the courses
    courses = grabclasses()
    db_info = connectdb()
    db = db_info[0]
    db_conn = db_info[1]
    db.execute('SELECT * FROM "posts" WHERE postid=%s',(postid,))
    postinfo = db.fetchone()

    #If there is no post found
    if postinfo == None:
        error = 'post not availible'
        url = "/" + str(course)
        return render_template("error.html", error = error, url = url)

    db.execute('SELECT * FROM "images" WHERE postid=%s',(postid,))
    imagesinfo = db.fetchall()
    #looks like -> {id,postid,images}
    db.execute('SELECT * FROM "files" WHERE postid=%s',(postid,))
    filesinfo = db.fetchall()
             
    # postduration = time_difference(post[5],post[6])
    db.execute('SELECT * FROM "replies" WHERE postid=%s ORDER BY date DESC, time DESC',(postid,))
    repliesinfo = db.fetchall()

    db.execute('SELECT * FROM "replyimages" WHERE postid=%s',(postid,))
    repliesimagesinfo = db.fetchall()

    db.execute('SELECT * FROM "replyfiles" WHERE postid=%s',(postid,))
    repliesfilesinfo = db.fetchall()

    db.close()
    db_conn.close()
    userid = session["username"]
    page_identifier = "homepage"
    return render_template("viewpost.html", postid = postid, postinfo = postinfo, imagesinfo = imagesinfo, filesinfo = filesinfo, repliesinfo = repliesinfo, repliesimagesinfo = repliesimagesinfo, repliesfilesinfo = repliesfilesinfo, courses = courses, course = course, userid = userid,BUCKET_NAME = BUCKET_NAME)




@app.route('/resources/<route>', methods=["GET", "POST"])
def resources(route):
    #saves route created and checks if peson put in a correct course
    #route to the folder
    userid = grab_user_id(session["username"])
    currentfolderrouteurl = route
    #route to the folder

    #splits the routes into parts and creates an array of the parts
    routeparts = route.split(">")
    route = str()
    for i in range(len(routeparts)):
        route = route + "/" + routeparts[i]
    #splits the routes into parts and creates an array of the parts
    course = routeparts[0]
    courses = grabclasses()
    #checks to see if the person put in a valid course
    courseavailible = checkclass(course, courses)

    #access tells if the user has access to do changes to the folder
    access=''
    #route base is the varibale that is the route with the foldername within it 
    route = ""
    #if the routepart does not only contain a class, create the route base with the route parts
    if len(routeparts) != 1:
        folder_name = routeparts[len(routeparts)-1]
        for route_index in range(len(routeparts)):
            route = route + "/" + routeparts[route_index]
    #else, it will be the current folder_url which includes the class
    else:
        route = "/" + currentfolderrouteurl
    #saves route created and checks if peson put in a correct course
    db_info = connectdb()
    db = db_info[0]
    db_conn = db_info[1]
    
    root_route = ""
    if len(routeparts) > 1:

        for route_part in range(len(routeparts)-1):
            root_route = root_route + "/" + routeparts[route_part]
        db.execute('SELECT * FROM "materials" WHERE (objectroute = %s AND objecttype = %s AND name = %s)',(root_route,'folder',routeparts[len(routeparts)-1]),)
        count = len(db.fetchall())
        if count == 0:
            error = 'this folder does not exist. Please go back'
            url = "/resources/"+ routeparts[0]
            return render_template("error.html", error = error, url = url)
    # if the class is not in the list, it will render an apology
    if courseavailible == False:
        error = 'Class is not availible. Select Class from Options'
        url = "/homepage"
        return render_template("error.html", error = error, url = url)

    if request.method == "POST":
        #gathers information for database entry
        type_of_form = request.form.get("type_of_form")
        username = session["username"]
        objectroute = route

        now = datetime.now()
        date = now.strftime("%m/%d/%Y")
        time = now.strftime("%H:%M:%S")
        db.execute('SELECT * FROM "materials"')
        id = len(db.fetchall())

        #grabs the postid

        if type_of_form == "uploadfile":
            title = request.form.get("title")
            body = request.form.get("body")
            title = str(title)
            body = str(body)

            #if there is no inputs, return an error
            if title == "":
                flash('No input to required parts')
                return redirect(request.url)

            #check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.


            #makes a new folder for the images. This makes it so that it can conserve it's name
            filespath = "static/resources/" + str(course)
                
            #makes a new upload folder if the upload folder does not exist
            UPLOAD_FOLDER = "static/resources/" + str(route)
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
            filedata = request.files.getlist("file")
            username = session["username"]
            #makes a new upload folder if the upload folder does not exist

            filespath = "resources" + str(route)
            for file in filedata:
                if file.filename != "":
                    split_tup = os.path.splitext(file.filename)

                    # extract the file name and extension
                    file_name = split_tup[0]
                    file_extension = split_tup[1]
                    imagefileextensions = ['.png', '.PNG', '.jpg', '.jpeg', '.bmp' '.tiff', '.gif', '.webp']
                    #checks if image
                    if file_extension in imagefileextensions:
                        objecttype = "image"
                        filename = secure_filename(file.filename)
                        fileupload = upload(filespath,filename,file)

                        db.execute('''INSERT INTO "materials"(resourceid, objectroute, objecttype, course, username, name, time, date, title, body,user_access_names,user_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                        ,(id,objectroute,objecttype,course,username,filename,time,date,title,body,"-",userid))

                        db_conn.commit()
                    else:
                        objecttype = "file"
                        filename = secure_filename(file.filename)
                        fileupload = upload(filespath,filename,file)

                        db.execute('''INSERT INTO "materials"(resourceid, objectroute, objecttype, course, username, name, time, date, title, body,user_access_names,user_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                        ,(id,objectroute,objecttype,course,username,filename,time,date,title,body,"-",userid))

                        db_conn.commit()
        if type_of_form == "newfolder":
            #grabs the folder_name for the new folder
            foldername = request.form.get("name_of_folder")
            foldername = str(foldername)

            #checks if the folder exist in the object route
            db.execute('SELECT name FROM "materials" WHERE objectroute = %s AND objecttype= %s AND name=%s',(route,"folder",foldername,))
            count = len(db.fetchall())
            if count != 0:
                flash('Folder already exist')
                return redirect(request.url)
            #checks if the folder exist in the object route

            #grabs from the form the inputed user access names and converts into a list
            user_access_names  = str(request.form.get("user_access_names"))
            user_access_names = user_access_names.split(",")
            user_access_names.append(username)
            user_access_string = ""
            for user_access_name in user_access_names:
                if user_access_name=="+-" or user_access_name=="-":
                    user_access_string = user_access_string + user_access_name + ","
                else:
                    if user_access_name != "":
                        userid = grab_user_id(user_access_name)
                        user_access_string = user_access_string + str(userid) + ","
            #grabs from the form the inputed user access names and converts into a list

            #if no upload folder, return error
            if foldername == "":
                flash('No input to required parts')
                return redirect(request.url)
            #if no upload folder, return error

            #gives permission to parent path
            parentpath = os.getcwd()
            staticpath = str(parentpath) + '/static'
            os.chmod(parentpath, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            os.chmod(staticpath, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            #gives permission to parent path

            #makes a new folder for the images. This makes it so that it can conserve it's name
            s3filepath = "resources" + str(route) + "/" + str(foldername) + "/"
            s3.put_object(Bucket = BUCKET_NAME, Key=s3filepath)
            objecttype = "folder"

            #enter folder information into database
            db.execute('''INSERT INTO "materials"(resourceid, objectroute, objecttype, course, username, name, time, date, title, body, user_access_names,user_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                        ,(id,objectroute,objecttype,course,username,foldername,time,date,"","",str(user_access_string),userid,))
            db_conn.commit()
    #grabs the username
    userid = str(grab_user_id(session["username"]))
    #if it is at the root path, grant everyone permission
    if len(routeparts) == 1:
        access="granted"
    else: 
        #grabs the materials with the root path of the current folder path
        db.execute('SELECT user_access_names FROM "materials" WHERE objectroute = %s  AND name=%s',(root_route,folder_name,))
        user_access_names = (db.fetchall()[0][0])
        user_access_names_split = user_access_names.split(",")
        #if one of the access users consist of this symbol, it is granted to everyone(public)
        if ("+-" in user_access_names_split):
            access="granted"
        #else, it will continue and grant access to the select users
        else:
            #if this symbol is within the access users, then grant the user's of the parent folder access also to this folder
            if "-" in user_access_names_split:
                parent_route_parts = root_route.split("/") 
                parent_route_parts.pop(0)
                parent_route_root = ""
                parent_folder_name = parent_route_parts[len(parent_route_parts)-1]
                for part_index in range(len(parent_route_parts)-1):
                    parent_route_root = parent_route_root + "/" + parent_route_parts[part_index]
                db.execute('SELECT user_access_names FROM "materials" WHERE objectroute = %s  AND name=%s AND objecttype=%s',(parent_route_root,parent_folder_name,"folder"))
                username_parent = db.fetchall()
                username_parent = username_parent[0][0]
                user_access_names = user_access_names + username_parent
                user_access_names = user_access_names.split(",")
            #checks if the user is in the user is in the user names
            if userid not in user_access_names:
                access="denied"
            else:
                access="granted"
    #grab the materials
    db.execute('SELECT * FROM "materials" WHERE (objecttype=%s OR objecttype=%s) AND objectroute=%s',('image','file', route,))
    materialsinfo = db.fetchall()
    materialsinfocount = len(materialsinfo)
    db.execute('SELECT * FROM "materials" WHERE objecttype=%s AND objectroute=%s',('folder', route,))
    foldersinfo = db.fetchall()
    db.execute('SELECT username FROM "Users" ORDER BY username ASC')
    db_usernames = db.fetchall()
    usernames = []
    for i in range(len(db_usernames)):
        if db_usernames[i][0] != session["username"]:
            usernames.append(db_usernames[i][0])
    db.close()
    db_conn.close()
    #grab the folders
    aws_resource_list = []
    count = 0
    for i in range(len(materialsinfo)):
        material_info_data = []
        if materialsinfo[i][3] != "folder":
            material_info_data.append(materialsinfo[i][6])
            material_info_data.append(materialsinfo[i][8])
            material_info_data.append(materialsinfo[i][5])
            aws_course = materialsinfo[i][2].replace(" ", "+")
            aws_key = materialsinfo[i][6].replace(" ", "+")
            aws__route = "resources" + str(aws_course) + "/" + str(aws_key)
            material_info_data.append(aws__route)
            material_info_data.append(materialsinfo[i][9])
            material_info_data.append(materialsinfo[i][10])
            material_info_data.append(materialsinfo[i][1])
            material_info_data.append(materialsinfo[i][0])
            count+=1
        aws_resource_list.append(material_info_data)
    #grab the materials
    page_identifier=course
    return render_template("resources.html", access = access, usernames=usernames, BUCKET_NAME= BUCKET_NAME,aws_resource_list = aws_resource_list, currentfolderrouteurl = currentfolderrouteurl, page_identifier = page_identifier, course = course, foldersinfo = foldersinfo, materialsinfo = materialsinfo, route = route,)


@app.route('/grade_viewer', methods=["GET","POST"])
@login_hac_required
def grade_viewer():
    session_key_list = list(session.keys())
    if "user_id_hac" not in session_key_list:
        return redirect(url_for('grade_viewer_signup'))
    #grab information for grades
    session["error"] = False
    if "error" in session.keys():
        error = session["error"]
        if error == True:
            session["error"] = False
            flash("Error Occured. Your username and password may be wrong!")
            return redirect(url_for("grade_viewer_signup"))
        #grabs data from dictionary
    if "hacgrades" in session.keys():
        grades_data = session["hacgrades"]
        class_names = grades_data['class_names']
        #returns as ['class 1', 'class 2', 'class 3', 'class 4', 'class 5']
        grade_summary = grades_data['grade_summary']
        assignment_grades = grades_data['assignment_grades']
        iterate = [1,2,3,4,5]
    else:
        return redirect("/grade_viewer_signup")
    course="homepage"
    page_identifier="grade_viewer"
# for i in range()
    return render_template("grade_viewer.html", course=course, page_identifier=page_identifier, class_names=class_names, grade_summary=grade_summary, assignment_grades=assignment_grades, iterate=iterate)

@app.route('/grade_viewer_signup', methods=["GET","POST"])
def grade_viewer_signup():
    #if the request is post, grab the form elements and password and grab nessasary information for hac
    if request.method == "POST":
        grade_username = request.form.get('gradeusername')
        gradepassword = request.form.get('gradepassword')
        session["user_id_hac"] = grade_username
        session["password_hac"] = gradepassword
        hac_executions('grades')
        return redirect('/grade_viewer')
    #else, load the page where these peices of info must be inputted
    session["user_id_hac"] = "NULL"
    session["password_hac"] = "NUll"
    return render_template("grade_viewer_signup.html")

@app.route('/grade_viewer/<selectedcourse>', methods=["GET","POST"])

def grade_viewer_course(selectedcourse):
    username = session["username"]
    grade_viewer_username = session["user_id_hac"]
    grade_viewer_password = session["password_hac"]
    grades_data = session["hacgrades"]

    #grabs data from dictionary
    class_names = grades_data['class_names']
    #returns as ['class 1', 'class 2', 'class 3', 'class 4', 'class 5']
    if selectedcourse in grades_data['grade_summary'].keys():
        grade_summary = grades_data['grade_summary'][selectedcourse]
        percentage=grade_summary[0][3]
        assignment_grades = grades_data['assignment_grades'][selectedcourse]
        course="homepage"
        page_identifier="grade_viewer"
        return render_template("grade_viewer_selected_course.html", percentage=percentage, course=course, page_identifier=page_identifier, selectedcourse = selectedcourse, class_names=class_names, grade_summary=grade_summary, assignment_grades=assignment_grades)
    else:
        error = 'Class Information Not Availible'
        url = "/" + "grade_viewer"
        return render_template("error.html", error = error, url = url)
    # for i in range()

@app.route('/Attendance', methods=["GET","POST"])
@login_hac_required
def calendar():
    course = "homepage"
    page_identifier = "attendance"

    return render_template("attendance.html", course=course, page_identifier=page_identifier)

@app.route('/announcements', methods=["GET","POST"])
@public_endpoint
def announcements():
    html = requests.get("https://bentonvillek12.org/StudentAnnouncements/BHS").text
    soup = BeautifulSoup(html)
    html = soup.find('div', {'class':'container body-content'})
    return render_template("announcements.html",html=html)

@app.route('/getcourses', methods=["GET", "POST"])
def getcoursesapi():
    #grab the course lists through Javascript
    courses = jsonify(grabclasses())
    return(courses)


@app.route('/getcourseposts', methods=["GET", "POST"])
def getcourseposts():
    #grab the posts infomation of the specific class provided
    course = request.json
    #if it is displaying the homepage, grab all the posts
    if course == "homepage":
        now = datetime.now()
        nowdate = now.strftime("%m/%d/%Y")
        nowdate = datetime.strptime(nowdate,"%m/%d/%Y")
        db_info = connectdb()
        db = db_info[0]
        db_conn = db_info[1]
        db.execute('SELECT * FROM "posts" ORDER BY date DESC, time DESC')
        postings = db.fetchall()
        db.close()
        db_conn.close()
    else:
        db_info = connectdb()
        db = db_info[0]
        db_conn = db_info[1]
        db.execute('SELECT * FROM "posts" WHERE course=%s ORDER BY date DESC, time DESC',(course,))
        postings = db.fetchall()
        db.close()
        db_conn.close()
    postlist = [tuple(row) for row in postings]
    postings = json.dumps(postlist, indent=4, sort_keys=True, default=str)
    return(postings)

@app.route('/getresources', methods=["GET", "POST"])
def getresources():
    course = request.json
    #grab the materials
    db_info = connectdb()
    db = db_info[0]
    db_conn = db_info[1]
    db.execute('SELECT * FROM "materials" WHERE objecttype=%s OR objecttype=%s AND course=%s',('image','file',course, ))
    #grab the materials
    materialsinfo = db.fetchall()
    db.close()
    db_conn.close()
    resources = jsonify(materialsinfo)
    return(resources)

@app.route('/getfolders', methods=["GET", "POST"])
def getfolders():
    db_info = connectdb()
    db = db_info[0]
    db_conn = db_info[1]
    course = request.json
    db.execute('SELECT * FROM "materials" WHERE (objecttype=%s and course=%s)',('folder',course, ))
    #grab the materials
    foldersinfo = db.fetchall()
    db.close()
    db_conn.close()
    folders = jsonify(foldersinfo)
    return(folders)

@app.route('/gethacattendance', methods=['GET', 'POST'])
def gethaclogin():
    update_hac()
    attendance_data = session["hacattendance"]
    return jsonify(attendance_data)

@app.route('/update_hac', methods=['GET', 'POST'])
def update_hac_function():
    if "hacgrades" not in session.keys():
        flash('Enter in a Username and Password')
        return redirect("/grade_viewer_signup")
    update_hac()
    response = "good"
    return (response)

@app.route('/grade_save_calculations', methods=['GET','POST'])
def grade_save_calculations():
    grade_info_change = request.json
    response = "good"
    return (response)

@app.route("/zip_download_files", methods=['POST'])
def get_zip():
    #grab the files to zip
    file_elements = request.json
    parentpath = os.getcwd()
    root_path = str(parentpath) + "/static/zip/"
    #if the directory is not there, create it
    if not os.path.isdir(root_path):
        os.makedirs(root_path)
    zip_folder_number = str(0)
    current_folders = os.listdir(root_path)
    #make a new folder name for the path if there are multiple
    for index in range(len(current_folders)):
        if str(zip_folder_number) != str(current_folders[index]):
            zip_folder_number = str(index)
        if str(index) == str(current_folders[index]):
            zip_folder_number = str(index + 1)
    # for each file names
    for file_element in file_elements:
        file_element = str(file_element)
        #find the file route
        file_route_split = file_element.split("/")
        filename = file_route_split[len(file_route_split)-1]
        route = file_route_split[3]
        #download the file in the file route 
        for routing_index in range(4,len(file_route_split)):
            route = route + "/" + file_route_split[routing_index]
        route = route.replace("+"," ")
        download_file(route,filename, BUCKET_NAME, zip_folder_number)
    return jsonify(zip_folder_number)

def zipdir(dirPath=None, zipFilePath=None, includeDirInZip=True):

    if not zipFilePath:
        zipFilePath = dirPath + ".zip"
    if not os.path.isdir(dirPath):
        raise OSError("dirPath argument must point to a directory. "
            "'%s' does not." % dirPath)
    parentDir, dirToZip = os.path.split(dirPath)
    #Little nested function to prepare the proper archive path
    def trimPath(path):
        archivePath = path.replace(parentDir, "", 1)
        if parentDir:
            archivePath = archivePath.replace(os.path.sep, "", 1)
        if not includeDirInZip:
            archivePath = archivePath.replace(dirToZip + os.path.sep, "", 1)
        return os.path.normcase(archivePath)

    outFile = zipfile.ZipFile(zipFilePath, "w",
        compression=zipfile.ZIP_DEFLATED)
    for (archiveDirPath, dirNames, fileNames) in os.walk(dirPath):
        for fileName in fileNames:
            filePath = os.path.join(archiveDirPath, fileName)
            outFile.write(filePath, trimPath(filePath))
        #Make sure we get empty directories as well
        if not fileNames and not dirNames:
            zipInfo = zipfile.ZipInfo(trimPath(archiveDirPath) + "/")
            #some web sites suggest doing
            #zipInfo.external_attr = 16
            #or
            #zipInfo.external_attr = 48
            #Here to allow for inserting an empty directory.  Still TBD/TODO.
            outFile.writestr(zipInfo, "")
    outFile.close()

@app.route("/zipit", methods=['POST'])
def zipit():
    #create the zip file
    zip_number = str(request.json)
    parentpath = os.getcwd()
    zip_folder_root = str(parentpath) + "/static/zip/" + zip_number
    base_folder_target =  str(parentpath) +'/static/zip_files/' + zip_number + "/"
    #create base directory
    if not os.path.isdir(base_folder_target):
        os.makedirs(base_folder_target)
    #create the target to where the files should be stored and zip that target
    target = str(parentpath) +'/static/zip_files/' + zip_number + '/file.zip'
    zipdir(zip_folder_root, target, False)
    return jsonify(0)
    

@app.route("/folder_zip_download", methods=['POST'])
def get_folder_zip():
    #grab the json with the folder_information on which folders to download
    folder_info = request.json
    folder_elements = folder_info["folder_elements"]
    zip_folder_number = folder_info["zip_number"]
    #creates the folder number if there are multiple folders being created
    if len(zip_folder_number) == 0:
        parentpath = os.getcwd()
        root_path = str(parentpath) + "/static/zip/"
        if not os.path.isdir(root_path):
            os.makedirs(root_path)
        zip_folder_number = str(0)
        current_folders = os.listdir(root_path)
        for index in range(len(current_folders)):
            if str(zip_folder_number) != str(current_folders[index]):
                zip_folder_number = str(index)
            if str(index) == str(current_folders[index]):
                zip_folder_number = str(index + 1)
    #for each folder
    for folder in folder_elements:
        #create a route with the folder
        folder = str(folder).replace(">","/")
        #convert to an array
        file_route_split = folder.split("/")
        #grab the filename
        filename = file_route_split[len(file_route_split)-1]
        #the route is the 3rd infec
        route = file_route_split[3]
        #start at 4 because thats where the index for the folder route is 
        for routing_index in range(4,len(file_route_split)):
            route = route + "/" + file_route_split[routing_index]
        #convert the uri a little
        route = route.replace("+"," ")
        folder = folder.split("/")
        base_folder = ''
        #download the object
        for route_part_index in range(3,len(folder)):
            base_folder = base_folder + folder[route_part_index] + "/"
        download_folder(BUCKET_NAME,route,zip_folder_number,base_folder)
    return jsonify(zip_folder_number)


@app.route("/deletion", methods=['POST'])
def delete_files():
    files_info = request.json["ids"]
    username = session["username"]
    username = str(grab_user_id(username))
    for id_number in files_info:
        db_info = connectdb()
        db = db_info[0]
        db_conn = db_info[1]
        folder_id = id_number
        db.execute('SELECT objectroute,name,objecttype,user_access_names,user_id,course FROM "materials" WHERE id=%s',(id_number,))
        object_info = db.fetchone()
        objectroute = object_info[0]
        name = object_info[1]
        object_type = object_info[2]
        user_access_names = object_info[3] 
        creator = str(object_info[4])
        course = str(object_info[5])
        if username == creator:
            access= "granted"
        else:
            if object_type == "folder":
                user_access_names_split = user_access_names.split(",")
                if ("+-" in user_access_names_split):
                    access="granted"
                #else, it will continue and grant access to the select users
                else:
                    #if this symbol is within the access users, then grant the user's of the parent folder access also to this folder
                    if "-" in user_access_names_split:
                        parent_route_parts = objectroute.split("/") 
                        parent_route_parts.pop(0)
                        parent_route_root = ""
                        parent_folder_name = parent_route_parts[len(parent_route_parts)-1]
                        for part_index in range(len(parent_route_parts)-1):
                            parent_route_root = parent_route_root + "/" + parent_route_parts[part_index]
                        db.execute('SELECT user_access_names FROM "materials" WHERE objectroute = %s  AND name=%s AND objecttype=%s',(parent_route_root,parent_folder_name,"folder"))
                        username_parent = db.fetchall()
                        username_parent = username_parent[0][0]
                        user_access_names = user_access_names + username_parent
                        user_access_names = user_access_names.split(",")
                    #checks if the user is in the user is in the user names
                    if username not in user_access_names:
                        access="denied"
                    else:
                        access="granted"
                if access == "denied":
                    return jsonify("denied")
                else:
                    db.execute('DELETE FROM "materials" WHERE id=%s',(id_number,))
                    delete_aws_files(objectroute,name,"file")
            else:
                parent_route_parts = objectroute.split("/") 
                parent_route_parts.pop(0)
                parent_route_root = ""
                parent_folder_name = parent_route_parts[len(parent_route_parts)-1]
                for part_index in range(len(parent_route_parts)-1):
                    parent_route_root = parent_route_root + "/" + parent_route_parts[part_index]
                db.execute('SELECT user_access_names FROM "materials" WHERE objectroute=%s AND objecttype=%s',(parent_route_root,"folder",))
                object_info = db.fetchone()
                user_access_names = object_info[0]
                user_access_names_split = user_access_names.split(",")
                if ("+-" in user_access_names_split):
                    access="granted"
                #else, it will continue and grant access to the select users
                else:
                    #if this symbol is within the access users, then grant the user's of the parent folder access also to this folder
                    if "-" in user_access_names_split:
                        parent_route_parts = parent_route_root.split("/") 
                        parent_route_parts.pop(0)
                        parent_route_root = ""
                        parent_folder_name = parent_route_parts[len(parent_route_parts)-1]
                        for part_index in range(len(parent_route_parts)-1):
                            parent_route_root = parent_route_root + "/" + parent_route_parts[part_index]
                        db.execute('SELECT user_access_names FROM "materials" WHERE objectroute = %s  AND name=%s AND objecttype=%s',(parent_route_root,parent_folder_name,"folder"))
                        username_parent = db.fetchall()
                        username_parent = username_parent[0][0]
                        user_access_names = user_access_names + username_parent
                        user_access_names = user_access_names.split(",")
                    #checks if the user is in the user is in the user names
                    if username not in user_access_names:
                        access="denied"
                    else:
                        access="granted"
                        
        if access == "denied":
            return jsonify("denied")
        else:
            if object_type == "folder":
                db.execute('DELETE FROM "materials" WHERE id=%s',(folder_id,))
                delete_aws_files(objectroute,name,"folder")
                objectroute = objectroute + "/" + name
                db.execute('SELECT * FROM "materials" WHERE course=%s',(course,))
                materials = db.fetchall()
                for material in materials:
                    father_object_route = objectroute.split("/")
                    paths_split = material[2].split("/")
                    path_id = material[0]
                    file_name = material[6]
                    for index, father_part in enumerate(father_object_route):
                        if len(paths_split) < len(father_object_route):
                            same_parent = False
                            break;
                        if father_part == paths_split[index]:
                            same_parent = True
                        else:
                            same_parent = False
                            break;
                    if same_parent == True:
                        db.execute('DELETE FROM "materials" WHERE id=%s',(path_id,))
                        delete_aws_files(material[2],file_name,"file")
                        db_conn.commit()
            else:
                db.execute('DELETE FROM "materials" WHERE id=%s',(id_number,))
                delete_aws_files(objectroute,name,"file")
                db_conn.commit()
    db_conn.commit()
    db.close()
    db_conn.close()
    return jsonify("done")


@app.route("/meetings_intro", methods=['GET','POST'])
def meetings_intro():
    return redirect(url_for("join", display_name = session['username'], mute_audio = 1, mute_video = 1, room_id=1234))
    #return render_template("meetingsintro.html")

users_in_room = {}
rooms_sid = {}
names_sid = {}

@app.route("/join", methods=["GET"])
def join():
    display_name = request.args.get('display_name')
    mute_audio = request.args.get('mute_audio') # 1 or 0
    mute_video = request.args.get('mute_video') # 1 or 0
    room_id = request.args.get('room_id')
    session[room_id] = {"name": display_name,
                        "mute_audio": mute_audio, "mute_video": mute_video}
    print(session[room_id])
    return render_template("join.html", room_id=room_id, display_name=session[room_id]["name"], mute_audio=session[room_id]["mute_audio"], mute_video=session[room_id]["mute_video"])


@socketio.on("connect")
def on_connect():
    sid = request.sid
    print("New socket connected ", sid)


@socketio.on("join-room")
def on_join_room(data):
    sid = request.sid
    room_id = data["room_id"]
    display_name = session[room_id]["name"]

    # register sid to the room
    join_room(room_id)
    rooms_sid[sid] = room_id
    names_sid[sid] = display_name

    # broadcast to others in the room
    print("[{}] New member joined: {}<{}>".format(room_id, display_name, sid))
    emit("user-connect", {"sid": sid, "name": display_name},
         broadcast=True, include_self=False, room=room_id)

    # add to user list maintained on server
    if room_id not in users_in_room:
        users_in_room[room_id] = [sid]
        emit("user-list", {"my_id": sid})  # send own id only
    else:
        usrlist = {u_id: names_sid[u_id]
                   for u_id in users_in_room[room_id]}
        # send list of existing users to the new member
        emit("user-list", {"list": usrlist, "my_id": sid})
        # add new member to user list maintained on server
        users_in_room[room_id].append(sid)

    print("\nusers: ", users_in_room, "\n")


@socketio.on("disconnect")
def on_disconnect():
    sid = request.sid
    room_id = rooms_sid[sid]
    display_name = names_sid[sid]

    print("[{}] Member left: {}<{}>".format(room_id, display_name, sid))
    emit("user-disconnect", {"sid": sid},
         broadcast=True, include_self=False, room=room_id)

    users_in_room[room_id].remove(sid)
    if len(users_in_room[room_id]) == 0:
        users_in_room.pop(room_id)

    rooms_sid.pop(sid)
    names_sid.pop(sid)

    print("\nusers: ", users_in_room, "\n")


@socketio.on("data")
def on_data(data):
    sender_sid = data['sender_id']
    target_sid = data['target_id']
    if sender_sid != request.sid:
        print("[Not supposed to happen!] request.sid and sender_id don't match!!!")

    if data["type"] != "new-ice-candidate":
        print('{} message from {} to {}'.format(
            data["type"], sender_sid, target_sid))
    socketio.emit('data', data, room=target_sid)


if any(platform.win32_ver()):
    socketio.run(app, debug=True)
    socketio.run(app, debug=True)

@app.route("/settings", methods=['GET','POST'])
def settings():
    if request.method == "POST":
        form = request.form.get("form-name")
        if form == "password_form":
            password = request.form.get("password")
            db_info = connectdb()
            db = db_info[0]
            db_conn = db_info[1]
            password = get_hashed_password(password)
            username = session["username"]
            db.execute('UPDATE "Users" SET password=%s WHERE username=%s',(password,username,))
            db_conn.commit()
            db.close()
            db_conn.close()
    db_info = connectdb()
    db = db_info[0]
    db_conn = db_info[1]
    username = session["username"]
    user_id = grab_user_id(username)
    db.execute('SELECT * FROM posts WHERE user_id=%s',(user_id,))
    posts = db.fetchall()

    return render_template("settings.html", posts = posts, username=username)

@public_endpoint
@app.route("/privacy_policy", methods=['GET','POST'])
def privacy_policy():
    return render_template("privacy_policy.html")

@public_endpoint
@app.route("/terms_and_conditions", methods=['GET','POST'])
def terms_and_condtitions():
    return render_template("terms_of_service.html")
#Mostly Accessed by Javascript
@app.route("/grab_course_grades", methods=["POST"])
def grab_course_grades():
    course = request.json
    grades_data = session["hacgrades"]
    assignment_grades = grades_data['assignment_grades'][course]
    return jsonify(assignment_grades)

@app.route("/delete_post",methods=["POST"])
def delete_post():
    db_info = connectdb()
    db = db_info[0]
    db_conn = db_info[1]
    postid = request.json["post_id"]
    db.execute("SELECT images FROM images WHERE postid=%s",(postid,))
    image_names = db.fetchall()
    # if len(image_names) != 0:
    #     image_names = image_names[0]
    db.execute("SELECT files FROM files WHERE postid=%s",(postid,))
    file_names = db.fetchall()
    # if len(file_names) != 0:
    #     file_names = file_names[0]
    for image_name in image_names:
        image_name= image_name[0]
        delete_aws_files_post("userfiles/"+str(postid)+"/"+str(image_name),image_name,"file")
    db.execute('DELETE FROM images WHERE postid=%s',(postid,))
    db_conn.commit()
    for file_name in file_names:
        file_name = file_name[0]
        delete_aws_files_post("userfiles/"+str(postid)+"/"+str(file_name),file_name,"file")
    db.execute('DELETE FROM files WHERE postid=%s',(postid,))
    db_conn.commit()
    db.execute('DELETE FROM replies WHERE postid=%s',(postid,))
    db.execute("SELECT images FROM replyimages WHERE postid=%s",(postid,))
    reply_image_names = db.fetchall()
    # if len(reply_image_names) != 0:
    #     reply_image_names = reply_image_names[0]
    for reply_image_name in reply_image_names:
        reply_image_name = reply_image_name[0]
        delete_aws_files_post("userfiles-replies/"+str(postid)+"/"+str(reply_image_name),reply_image_name,"file")
    db.execute('DELETE FROM replyimages WHERE postid=%s',(postid,))
    db_conn.commit()
    db.execute("SELECT files FROM replyfiles WHERE postid=%s",(postid,))
    reply_file_names = db.fetchall()
    # if len(reply_file_names) != 0:
    #     reply_file_names = reply_file_names[0]
    for reply_file_name in reply_file_names:
        reply_file_name = reply_file_name[0]
        delete_aws_files_post("userfiles-replies/"+str(postid)+"/"+str(reply_file_name),reply_file_name,"file")
    db.execute('DELETE FROM replyfiles WHERE postid=%s',(postid,))
    db_conn.commit()
    db.execute('DELETE FROM posts WHERE postid=%s',(postid,))
    db_conn.commit()
    db.close()
    db_conn.close()
    return jsonify("done")

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=9000)