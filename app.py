from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify,send_file
from flask_session import Session
from helpers import login_required, grabclasses, checkclass, check, connectdb, time_difference, login_hac_required, update_hac, hac_executions
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

#change
app = Flask(__name__)
load_dotenv()
s3 = boto3.client('s3',
    aws_access_key_id = os.environ.get('AWS_S3_ACCESS_KEY'),
    aws_secret_access_key = os.environ.get('AWS_S3_SECRET_ACCESS_KEY'),
        )
app.config["SESSION_PERMANENT"] = False
# change
#s3

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
else:
    conn = psycopg2.connect(
        host=os.environ.get('RDS_HOSTNAME'),
        database=os.environ.get('RDS_DB_NAME'),
        user=os.environ.get('RDS_USERNAME'),
        password= os.environ.get('RDS_PASSWORD')
    )
    cursor = conn.cursor()
    BUCKET_NAME='studyist'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}:{}/{}'.format(
        os.environ.get('RDS_USERNAME'),
        os.environ.get('RDS_PASSWORD'),
        os.environ.get('RDS_HOSTNAME'),
        os.environ.get('RDS_PORT'),
        os.environ.get('RDS_DB_NAME')
    )
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_creation = SQLAlchemy(app)
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
app.secret_key = "super secret key"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

from aws import upload, download_file
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


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

#the intro homepage for the user
#test1
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
    #Get password/confirmation information
        form = request.form.get("form-name")
        if form == "signupform":
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
            null = "null"
            db.execute('INSERT INTO "Users"(username, password, email, gradeappusername, gradeapppassword, google_auth) VALUES (%s, %s, %s, %s, %s, %s)',(username,password,email,null,null,"False",))
            db_conn.commit()
            db.close()
            db_conn.close()
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
            #if an account with the same email has
            if google_auth == "True":
                #if the password is not already set to something
                if db_password == "null":
                    session["attempted_password"] = password
                    session["user_id"] = username[0][0]
                    session["hacattendancetimeupdated"] =''
                    session["hacgradestimeupdated"] =''
                    return redirect(url_for("login"))
                #else, continue to authenticate password

            db.execute('SELECT username FROM "Users" WHERE email=%s AND password=%s',(email,password));
            username = db.fetchall()
            count = len(username)
            db.close()
            db_conn.close()
            #if password is not the same as the user with the email, return error
            if count == 0:
                flash("Password is Incorrect")
                return render_template("intro.html")

            #set the session
            session["user_id"] = username[0][0]
            session["hacattendancetimeupdated"] =''
            session["hacgradestimeupdated"] =''
            return redirect(url_for("studyist"))
    else:
        return render_template("intro.html")
    return render_template("intro.html")


@app.route('/login')
def login():
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

@app.route("/login/callback")
def callback():
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
            db.execute('INSERT INTO "Users"(username, password, email, gradeappusername, gradeapppassword, google_auth) VALUES (%s, %s, %s, %s, %s, %s)',(users_name,null,users_email,null,null,"True",))
            # Send user back to homepage
            db_conn.commit()
            db.close()
            db_conn.close()
            return redirect(url_for("studyist"))
    session["user_id"] = users_name
    #adds the attempted password if the user doesn't already have one
    if "attempted_password" in session:
        db_info = connectdb()
        db = db_info[0]
        db_conn = db_info[1]
        db.execute('UPDATE "Users" SET password=%s WHERE username=%s',(session["attempted_password"],session["user_id"]))
    db_conn.commit()
    db.close()
    db_conn.close()
    return redirect(url_for("studyist"))

@app.route("/homepage", methods=["GET", "POST"])
@login_required
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
        username = session["user_id"]
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
                    db.execute('INSERT INTO "images"(postid, images) VALUES (%s, %s)',(id,filename, ))
                    db_conn.commit()
                else:
                    filename = secure_filename(file.filename)
                    fileupload = upload(filespath,filename,file)
                    db.execute('INSERT INTO "files"(postid, files) VALUES (%s, %s)',(id,filename, ))
                    db_conn.commit()
        db.execute('INSERT INTO "posts"(postid, course, username, title, body, time, date) VALUES(%s,%s,%s,%s,%s,%s,%s)',(id, course, username, title, body, time, date, ))            
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
@login_required
def post(course):
    page_identifier= course
    return render_template("post.html", course = course, page_identifier=page_identifier)


@app.route('/<course>/post/<postid>', methods=["GET", "POST"])
def viewpost(course, postid):
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
            username = session["user_id"]
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

            db.execute('INSERT INTO "replies"(replyid, postid, course, username, title, body, time, date) VALUES(%s,%s, %s, %s,%s, %s, %s,%s)',(id, postid, course, username, title, body, time, date,))
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
                        db.execute('INSERT INTO "replyimages"(replyid, postid, images) VALUES (%s, %s, %s)',(id,postid,filename, ))
                        db_conn.commit()

                    else:
                        filename = secure_filename(file.filename)
                        fileupload = upload(filespath,filename,file)
                        db.execute('INSERT INTO "replyfiles"(replyid, postid, files) VALUES (%s, %s, %s)',(id,postid,filename, ))
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
    userid = session["user_id"]
    page_identifier = "homepage"
    return render_template("viewpost.html", postid = postid, postinfo = postinfo, imagesinfo = imagesinfo, filesinfo = filesinfo, repliesinfo = repliesinfo, repliesimagesinfo = repliesimagesinfo, repliesfilesinfo = repliesfilesinfo, courses = courses, course = course, userid = userid,BUCKET_NAME = BUCKET_NAME)




@app.route('/resources/<route>', methods=["GET", "POST"])
def resources(route):
    #saves route created and checks if peson put in a correct course
    currentfolderrouteurl = route
    routeparts = route.split(">")
    route = str()
    for i in range(len(routeparts)):
        route = route + "/" + routeparts[i]
    course = routeparts[0]
    courses = grabclasses()
    courseavailible = checkclass(course, courses)
    #saves route created and checks if peson put in a correct course
    db_info = connectdb()
    db = db_info[0]
    db_conn = db_info[1]
    root_route = ""
    if len(routeparts) > 1:
        for route_part in range(len(routeparts)-1):
            root_route = root_route + "/" + routeparts[route_part]
        print(root_route)
        print(routeparts)
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
        username = session["user_id"]
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
            username = session["user_id"]
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

                        db.execute('''INSERT INTO "materials"(resourceid, objectroute, objecttype, course, username, name, time, date, title, body) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                        ,(id,objectroute,objecttype,course,username,filename,time,date,title,body,))

                        db_conn.commit()
                    else:
                        objecttype = "file"
                        filename = secure_filename(file.filename)
                        fileupload = upload(filespath,filename,file)

                        db.execute('''INSERT INTO "materials"(resourceid, objectroute, objecttype, course, username, name, time, date, title, body) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                        ,(id,objectroute,objecttype,course,username,filename,time,date,title,body,))

                        db_conn.commit()
        if type_of_form == "newfolder":
            foldername = request.form.get("name_of_folder")
            foldername = str(foldername)

            #if no upload folder, return error
            if foldername == "":
                flash('No input to required parts')
                return redirect(request.url)

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

            db.execute('''INSERT INTO "materials"(resourceid, objectroute, objecttype, course, username, name, time, date, title, body) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                        ,(id,objectroute,objecttype,course,username,foldername,time,date,"",""))
            db_conn.commit()
    #grab the materials
    db.execute('SELECT * FROM "materials" WHERE (objecttype=%s OR objecttype=%s) AND objectroute=%s',('image','file', route,))
    materialsinfo = db.fetchall()
    materialsinfocount = len(materialsinfo)

    db.execute('SELECT * FROM "materials" WHERE objecttype=%s AND objectroute=%s',('folder', route,))
    foldersinfo = db.fetchall()

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
            count+=1
        aws_resource_list.append(material_info_data)
    #grab the materials
    page_identifier=course
    return render_template("resources.html",BUCKET_NAME= BUCKET_NAME,aws_resource_list = aws_resource_list, currentfolderrouteurl = currentfolderrouteurl, page_identifier = page_identifier, course = course, foldersinfo = foldersinfo, materialsinfo = materialsinfo, route = route,)

@app.route('/grade_viewer', methods=["GET","POST"])
@login_hac_required
def grade_viewer():
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
        return redirect(url_for('grade_viewer_signup'))
    #grab information for grades
    update_hac()
    grades_data = session["hacgrades"]
    if 'error' in grades_data:
        error = grades_data['error']
        url = '/grade_viewer'
        return render_template("error.html", error = error, url = url)
    #grabs data from dictionary
    class_names = grades_data['class_names']
    #returns as ['class 1', 'class 2', 'class 3', 'class 4', 'class 5']
    grade_summary = grades_data['grade_summary']
    assignment_grades = grades_data['assignment_grades']
    iterate = [1,2,3,4,5]
    
    course="homepage"
    page_identifier="grade_viewer"
    # for i in range()
    return render_template("grade_viewer.html", course=course, page_identifier=page_identifier, class_names=class_names, grade_summary=grade_summary, assignment_grades=assignment_grades, iterate=iterate)

@app.route('/grade_viewer_signup', methods=["GET","POST"])
def grade_viewer_signup():
    db_info = connectdb()
    db = db_info[0]
    db_conn = db_info[1]
    username = session["user_id"]
    if request.method == "POST":
        grade_username = request.form.get('gradeusername')
        gradepassword = request.form.get('gradepassword')
        db.execute('UPDATE "Users" SET gradeappusername = %s, gradeapppassword = %s WHERE username =%s', (grade_username, gradepassword, username, ))
        db_conn.commit()
        hac_executions('attendance')
        hac_executions('grades')
        return redirect(url_for('studyist'))
    db.close()
    db_conn.close()
    return render_template("grade_viewer_signup.html")

@app.route('/grade_viewer/<selectedcourse>', methods=["GET","POST"])
@login_required
def grade_viewer_course(selectedcourse):
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
    update_hac()
    grades_data = session["hacgrades"]

    #grabs data from dictionary
    class_names = grades_data['class_names']
    #returns as ['class 1', 'class 2', 'class 3', 'class 4', 'class 5']
    grade_summary = grades_data['grade_summary'][selectedcourse]
    percentage=grade_summary[0][3]
    assignment_grades = grades_data['assignment_grades'][selectedcourse]
    
    course="homepage"
    page_identifier="grade_viewer"
    # for i in range()
    return render_template("grade_viewer_selected_course.html", percentage=percentage, course=course, page_identifier=page_identifier, selectedcourse = selectedcourse, class_names=class_names, grade_summary=grade_summary, assignment_grades=assignment_grades)

@app.route('/Attendance', methods=["GET","POST"])
@login_hac_required
def calendar():
    course = "homepage"
    page_identifier = "attendance"

    return render_template("attendance.html", course=course, page_identifier=page_identifier)

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

# @app.route('/getresources', methods=["GET", "POST"])
# def getresources():
#     course = request.json
#     #grab the materials
#     db_info = connectdb()
#     db = db_info[0]
#     db_conn = db_info[1]
#     db.execute('SELECT * FROM "materials" WHERE objecttype=%s OR objecttype=%s AND course=%s',('image','file',course, ))
#     #grab the materials
#     materialsinfo = db.fetchall()
#     db.close()
#     db_conn.close()
#     resources = jsonify(materialsinfo)
#     return(resources)

# @app.route('/getfolders', methods=["GET", "POST"])
# def getfolders():
#     db_info = connectdb()
#     db = db_info[0]
#     db_conn = db_info[1]
#     course = request.json
#     db.execute('SELECT * FROM "materials" WHERE (objecttype=%s and course=%s)',('folder',course, ))
#     #grab the materials
#     foldersinfo = db.fetchall()
#     db.close()
#     db_conn.close()
#     folders = jsonify(foldersinfo)
#     return(folders)

@app.route('/gethacattendance', methods=['GET', 'POST'])
def gethaclogin():
    update_hac()
    attendance_data = session["hacattendance"]
    return jsonify(attendance_data)

@app.route('/update_hac', methods=['GET', 'POST'])
def update_hac_function():
    update_hac()
    response = "good"
    return (response)

@app.route('/grade_save_calculations', methods=['GET','POST'])
def grade_save_calculations():
    grade_info_change = request.json
    response = "good"
    return (response)

@app.route("/zip_download", methods=['POST'])
def get_zip():
    file_elements = request.json
    parentpath = os.getcwd()
    root_path = str(parentpath) + "/static/zip/"
    if not os.path.isdir(root_path):
        os.makedirs(root_path)
    zip_folder_number = str(0)
    current_folders = os.listdir(root_path)
    print(current_folders)
    for index in range(len(current_folders)):
        if str(zip_folder_number) != str(current_folders[index]):
            zip_folder_number = str(index)
        if str(index) == str(current_folders[index]):
            zip_folder_number = str(index + 1)
    for file_element in file_elements:
        file_element = str(file_element)
        file_route_split = file_element.split("/")
        filename = file_route_split[len(file_route_split)-1]
        route = file_route_split[3]
        for routing_index in range(4,len(file_route_split)):
            route = route + "/" + file_route_split[routing_index]
        print("\n")
        route = route.replace("+"," ")
        print("\n")
        download_file(route,filename, BUCKET_NAME, zip_folder_number)
    zip_folder_path = root_path + zip_folder_number + ".zip"
    zip_folder_past = root_path + zip_folder_number
    # with zipfile.ZipFile(zip_folder_path, 'w') as f:
    #     for file in glob.glob(zip_folder_past):
    #         f.write(file)

    # import os, zipfile

    name = zip_folder_past
    zip_name = name + '.zip'

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
        for folder_name, subfolders, filenames in os.walk(name):
            for filename in filenames:
                file_path = os.path.join(folder_name, filename)
                zip_ref.write(file_path, arcname=os.path.relpath(file_path, name))

    zip_ref.close()

    return jsonify(zip_folder_number+".zip")

    