from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from helpers import login_required, grabclasses, checkclass, check, connectdb, time_difference
from werkzeug.utils import secure_filename
from sqlalchemy import *
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import botocore
import json
import stat
import os
import sqlite3
import boto3
from dotenv import load_dotenv
import psycopg2

#change
app = Flask(__name__)

s3 = boto3.client('s3',
    aws_access_key_id = os.environ.get('AWS_S3_ACCESS_KEY'),
    aws_secret_access_key = os.environ.get('AWS_S3_SECRET_ACCESS_KEY'),
        )
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
load_dotenv()
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
    #needs to be changed to studyist
    BUCKET_NAME='studyist-dev'
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

UPLOAD_FOLDER = '/Studyist/userfiles'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "super secret key"
app.config["TEMPLATES_AUTO_RELOAD"] = True

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

#the intro homepage for the user
#test1
@app.route("/", methods=["GET", "POST"])
def index():
    # if the form is submitted
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
            db.execute('INSERT INTO "Users"(username, password, email) VALUES (%s, %s, %s)',(username,password,email, ))
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
            return redirect("homepage")
    else:
        return render_template("intro.html")


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
            return redirect(url_for(studyist))
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
    return render_template("post.html", course = course, )


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
                    imagefileextensions = ['.png', 'PNG', '.jpg', '.jpeg', '.bmp' '.tiff', '.gif','.webp']
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
    if len(routeparts) > 1:
        db.execute('SELECT * FROM "materials" WHERE objectroute = %s',(route,))
        count = len(db.fetchall())
        if count == 0:
            error = 'this folder does not exist. Please go back'
            url = "/resources/"+ routeparts[0]
            return render_template("error.html", error = error, url = url)
    #if the class is not in the list, it will render an apology
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
            title = str(title)

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

                        db.execute('''INSERT INTO "materials"(resourceid, objectroute, objecttype, course, username, name, time, date) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'''
                        ,(id,objectroute,objecttype,course,username,filename,time,date,))

                        db_conn.commit()
                    else:
                        objecttype = "file"
                        filename = secure_filename(file.filename)
                        fileupload = upload(filespath,filename,file)

                        db.execute('''INSERT INTO "materials"(resourceid, objectroute, objecttype, course, username, name, time, date) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'''
                        ,(id,objectroute,objecttype,course,username,filename,time,date,))

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

            db.execute('''INSERT INTO "materials"(resourceid, objectroute, objecttype, course, username, name, time, date) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)'''
                        ,(id,objectroute,objecttype,course,username,foldername,time,date,))
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
            count+=1
        aws_resource_list.append(material_info_data)
    #grab the materials
    page_identifier=course
    return render_template("resources.html",BUCKET_NAME= BUCKET_NAME,aws_resource_list = aws_resource_list, currentfolderrouteurl = currentfolderrouteurl, page_identifier = page_identifier, course = course, foldersinfo = foldersinfo, materialsinfo = materialsinfo, route = route,)

@app.route('/grade_viewer', methods=["GET","POST"])
def grade_viewer():
    username = "bolivarc@bentonvillek12.org"
    password = "Simon$2290"

    #grab information for grades
    grades_response = requests.get("https://2o5vn3b0m9.execute-api.us-east-1.amazonaws.com/grades/" + username + "/" + password + "/")

    #converts output to a json format(dictionary)
    grades_data = grades_response.json()

    #grabs data from dictionary
    class_names = grades_data['class_names']
    #returns as ['class 1', 'class 2', 'class 3', 'class 4', 'class 5']
    grade_summary = grades_data['grade_summary']
    assignment_grades = grades_data['assignment_grades']
    iterate = [1,2,3,4,5]

    print(assignment_grades[class_names[0]][0])
    
    course="homepage"
    page_identifier="grade_viewer"
    # for i in range()
    return render_template("grade_viewer.html", course=course, page_identifier=page_identifier, class_names=class_names, grade_summary=grade_summary, assignment_grades=assignment_grades, iterate=iterate)

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
        db_info = db_info[1]
        db.execute('SELECT * FROM "posts" ORDER BY date DESC, time DESC')
        postings = db.fetchall()
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
    course = request.json
    db_info = connectdb()
    db = db_info[0]
    db_conn = db_info[1]
    db.execute('SELECT * FROM "materials" WHERE (objecttype=%s and course=%s)',('folder',course, ))
    #grab the materials
    foldersinfo = db.fetchall()
    db.close()
    db_conn.close()
    folders = jsonify(foldersinfo)
    return(folders)
