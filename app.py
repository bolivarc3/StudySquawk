from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from helpers import login_required, grabclasses, checkclass, check, connectdb, time_difference
from werkzeug.utils import secure_filename
from sqlalchemy import *
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import stat
import os
import sqlite3
import boto3
import botocore

app = Flask(__name__)
app.debug = True
# Ensure responses aren't cached
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

#s3
s3 = boto3.client('s3',
                aws_access_key_id='AKIA4XOBDYJLMRYYW35I',
                aws_secret_access_key= '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',
                    )
ENV = 'prod'
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Tecra$2290@localhost/studyist'
    BUCKET_NAME='studyist-dev'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://studyist:wP3d62y*mKzBamm3@studyist.cqdyic3h8igs.us-east-1.rds.amazonaws.com:5432/studyist'
    BUCKET_NAME='studyist'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = '/Studyist/userfiles'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "super secret key"
app.config["TEMPLATES_AUTO_RELOAD"] = True
db = SQLAlchemy(app)
from models import Users, posts, images, files, replies, replyfiles, replyimages, materials


def getApp():
    return app

from aws import upload, download_file

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
    print(BUCKET_NAME)
    session.clear()
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
            dbinfo = connectdb("userinfo.db")
            #seperate list into db objects
            userinfocursor = dbinfo[0]
            userinfoconnect = dbinfo[1]

            #checks if email is already in the system | cant be 2 of the same email
            # userinfocursor.execute("SELECT email FROM users WHERE email = ?", (email, ));
            # stored_email = userinfocursor.fetchone()

            if db.session.query(Users).filter(Users.email == email).count() != 0:
                error = "invalid email address"
                flash('email already has been used')
                return redirect(url_for('index'))

            #checks if username is already in the system | cant be 2 of same username
            # userinfocursor.execute("SELECT username FROM users WHERE username = ?", (username, ));
            # stored_username = userinfocursor.fetchone()
            # userinfoconnect.close()

            if db.session.query(Users).filter(Users.username == username).count() != 0:
                error = "invalid email address"
                flash("username already has been used")
                return redirect(url_for('index'))
            data = Users(username, password, email)
            db.session.add(data)
            db.session.commit()
            return redirect("/")

        if form == "loginform":
            email = request.form.get("email")
            password = request.form.get("password")

            #if email is not in system, return error
            if db.session.query(Users).filter(Users.email == email).count() == 0:
                flash("Email and User not found")
                return render_template("intro.html")

            User = db.session.query(Users).filter(Users.email == email, Users.password == password).first()
            username = User.username
            #if password is not the same as the user with the email, return error
            if db.session.query(Users).filter(Users.email == email, Users.password == password).count() == 0:
                flash("Password is Incorrect")
                return render_template("intro.html")

            #set the session
            session["user_id"] = username
            return redirect("homepage")
    else:
        return render_template("intro.html")


@app.route("/homepage", methods=["GET", "POST"])
@login_required
def studyist():

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
        postings = db.session.query(posts).order_by(posts.date.desc(),posts.time.desc()).all()
        #return object looking like <posts> which is an object
        #index into it and . insert what you are looking for
        course = "homepage"
        return render_template("homepage.html", course = course, courses = courses,postings = postings)


@app.route('/<course>', methods=["GET", "POST"])
def course(course):

    #grabs the classes and checks if class is a class in db
    courses = grabclasses()
    print(course)
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

        id = db.session.query(posts).count() +1
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
                    imagedata = images(id,filename)
                    db.session.add(imagedata)
                    db.session.commit()
                else:
                    filename = secure_filename(file.filename)
                    fileupload = upload(filespath,filename,file)

                    filedata = files(id,filename)
                    db.session.add(filedata)
                    db.session.commit()

        postsdata = posts(id, course, username, title, body, time, date)
        db.session.add(postsdata)
        db.session.commit()

        return redirect(url_for('course', course = course))

    postings = db.session.query(posts).filter(posts.course == course).order_by(posts.date.desc(),posts.time.desc()).all()
    return render_template("coursemain.html", course = course, courses = courses, postings = postings)


@app.route('/<course>/postcreation', methods=["GET", "POST"])
@login_required
def post(course):
    return render_template("post.html", course = course, )


@app.route('/<course>/post/<postid>', methods=["GET", "POST"])
def viewpost(course, postid):

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

            repliesquery = db.session.query(replies).order_by(replies.date.desc(),replies.time.desc()).all()
            replieslength = len(repliesquery)
            id = replieslength + 1

            data = replies(id, postid,course, username, title, body, time, date)
            db.session.add(data)
            db.session.commit()
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

                        imagedata = replyimages(id,postid,filename)
                        db.session.add(imagedata)
                        db.session.commit()

                    else:
                        filename = secure_filename(file.filename)
                        fileupload = upload(filespath,filename,file)

                        filedata = replyfiles(id,postid,filename)
                        db.session.add(filedata)
                        db.session.commit()


        return redirect(url_for('viewpost', course = course, postid = postid))


    #grab all of the courses
    courses = grabclasses()

    postinfo = db.session.query(posts).filter(posts.postid == postid).first()
    #looks like -> <object> -inside -> <id:id#, postid:postid#, etc>

    #If there is no post found
    if postinfo == None:
        error = 'post not availible'
        url = "/" + str(course)
        return render_template("error.html", error = error, url = url)

    imagesinfo = db.session.query(images.id,images.postid,images.images).filter(images.postid == postid).all()
    #looks like -> {id,postid,images}

    filesinfo = db.session.query(files.id,files.postid,files.files).filter(files.postid == postid).all()
    #looks like -> {id,postid,images}


    print(imagesinfo)
    # postduration = time_difference(post[5],post[6])

    repliesinfo = db.session.query(replies.id,replies.replyid,replies.postid,replies.course,replies.username,replies.title,replies.body,replies.time,replies.date).filter(replies.postid == postid).order_by(replies.date.desc(),replies.time.desc()).all()
    #looks like -> <object> -inside -> <id:id#, postid:postid#, etc>


    repliesimagesinfo = db.session.query(replyimages.id,replyimages.replyid,replyimages.postid,replyimages.images).filter(replyimages.postid == postid).all()
    #looks like -> {id,postid,images}

    repliesfilesinfo = db.session.query(replyfiles.id,replyfiles.replyid,replyfiles.postid,replyfiles.files).filter(replyfiles.postid == postid).all()
    #looks like -> {id,postid,files}
    print("replies")
    print(len(repliesfilesinfo))

    #if there are images or files that need to be downloaded, download them. 
    if len(repliesfilesinfo) != 0:
        for i in range(len(repliesfilesinfo)):
            filespath = "userfiles-replies/" + str(repliesfilesinfo[i].replyid)
            download_file(filespath,BUCKET_NAME)

    if len(repliesimagesinfo) != 0:
        for i in range(len(repliesimagesinfo)):
            filespath = "userfiles-replies/" + str(repliesimagesinfo[i].replyid)
            download_file(filespath,BUCKET_NAME)
    
    if len(imagesinfo) != 0:
        filespath = "userfiles/" + str(imagesinfo[0].postid)
        print(filespath)
        download_file(filespath,BUCKET_NAME)
    
    if len(filesinfo) != 0:
        filespath = "userfiles/" + str(filesinfo[0].postid)
        download_file(filespath,BUCKET_NAME)
    #if there are images or files that need to be downloaded, download them. 

    userid = session["user_id"]
    return render_template("viewpost.html", postid = postid, postinfo = postinfo, imagesinfo = imagesinfo, filesinfo = filesinfo, repliesinfo = repliesinfo, repliesimagesinfo = repliesimagesinfo, courses = courses, course = course, userid = userid, )




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
    print("route")
    print(route)
    
    #saves route created and checks if peson put in a correct course

    #if the class is not in the list, it will render an apology
    if courseavailible == False:
        error = 'Class is not availible. Select Class from Options'
        url = "/homepage"
        return render_template("error.html", error = error, url = url)

    if request.method == "POST":
        print("hey")
        #gathers information for database entry
        type_of_form = request.form.get("type_of_form")
        username = session["user_id"]
        objectroute = route

        now = datetime.now()
        date = now.strftime("%m/%d/%Y")
        time = now.strftime("%H:%M:%S")

        id = db.session.query(materials).count()

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
            if os.path.exists(filespath):
                print("it exists")
            else:
                print("hey")
                
            #makes a new upload folder if the upload folder does not exist
            UPLOAD_FOLDER = "static/resources/" + str(route)
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
            filedata = request.files.getlist("file")
            username = session["user_id"]
            #makes a new upload folder if the upload folder does not exist

            filespath = "resources" + str(route)
            print(filespath)
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
                        print("hey")
                        materialdata = materials(id,objectroute,objecttype,course,username,filename,time,date)
                        db.session.add(materialdata)
                        db.session.commit()
                    else:
                        objecttype = "file"
                        filename = secure_filename(file.filename)
                        fileupload = upload(filespath,filename,file)
                        materialdata = materials(id,objectroute,objecttype,course,username,filename,time,date)
                        db.session.add(filedata)
                        db.session.commit()

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
            materialdata = materials(id,objectroute,objecttype,course,username,foldername,time,date)
            db.session.add(materialdata)
            db.session.commit()
    
    #grab the materials
    materialsinfo = db.session.query(materials.id,materials.resourceid,materials.objectroute,materials.objecttype,materials.course,materials.username,materials.name,materials.time,materials.date).filter(or_(materials.objecttype == "file", materials.objecttype == "image"), materials.objectroute ==  route).all()
    print(materialsinfo)
    materialsinfocount = db.session.query(materials.id,materials.resourceid,materials.objectroute,materials.objecttype,materials.course,materials.username,materials.name,materials.time,materials.date).filter(materials.objecttype == "file", materials.objecttype == "image", materials.objectroute ==  route).count()
    print(materialsinfocount)
        #grab the folders
    foldersinfo = db.session.query(materials.id,materials.resourceid,materials.objectroute,materials.objecttype,materials.course,materials.username,materials.name,materials.time,materials.date).filter(materials.objecttype == "folder", materials.objectroute == route).all()
    parentpath = os.getcwd()
    folderpath = str(parentpath) + "/static/resources" + route
    print("folderpath")
    print(folderpath)
    if not os.path.isdir(folderpath):
            os.makedirs(folderpath)
    for j in range(len(foldersinfo)):
        parentpath = os.getcwd()
        folderpath = str(parentpath) + "/static/resources/" + str(foldersinfo[i][2])
        print(folderpath)
        if not os.path.isdir(folderpath):
            os.makedirs(folderpath)
    #grab the folders
    for i in range(len(materialsinfo)):
        print("yesss")
        parentpath = os.getcwd()
        if materialsinfo[i][3] == "folder":
            folderpath = str(parentpath) + "/static/" + str(materialsinfo[i][2])
            print(folderpath)
            if not os.path.isdir(folderpath):
                os.makedirs(folderpath)
        else:
            key = "resources" + str(materialsinfo[i][2]) + "/" + str(materialsinfo[i][6])
            print(key)
            localfolder = str(parentpath) + '/static/' + str(key)
            s3.download_file(BUCKET_NAME,key,localfolder)
    #grab the materials

    return render_template("resources.html",currentfolderrouteurl = currentfolderrouteurl, course = course, foldersinfo = foldersinfo, materialsinfo = materialsinfo, route = route)


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
        postings = db.session.query(posts.id,posts.postid,posts.course,posts.username,posts.title,posts.body,posts.time,posts.date).order_by(posts.date.desc(),posts.time.desc()).all()
    else:
        postings = db.session.query(posts.id,posts.postid,posts.course,posts.username,posts.title,posts.body,posts.time,posts.date).filter(posts.course == course).order_by(posts.date.desc(),posts.time.desc()).all()
    postlist = [tuple(row) for row in postings]
    postings = json.dumps(postlist, indent=4, sort_keys=True, default=str)
    return(postings)

@app.route('/getresources', methods=["GET", "POST"])
def getresources():
    course = request.json
    #grab the materials
    materialsinfo = db.session.query(materials.id,materials.resourceid,materials.objectroute,materials.objecttype,materials.course,materials.username,materials.name,materials.time,materials.date).filter(materials.objecttype == "file", materials.objecttype == "image", materials.course == course).all()
    #grab the materials

    resources = jsonify(materialsinfo)
    return(resources)

@app.route('/getfolders', methods=["GET", "POST"])
def getfolders():
    course = request.json
    print(course)
    foldersinfo = db.session.query(materials.id,materials.resourceid,materials.objectroute,materials.objecttype,materials.course,materials.username,materials.name,materials.time,materials.date).filter(materials.objecttype == "folder", materials.course == course).all()
    print(foldersinfo)
    folders = jsonify(foldersinfo)
    return(folders)
