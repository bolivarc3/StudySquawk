from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from helpers import login_required, grabclasses, checkclass, check, connectdb, time_difference
from werkzeug.utils import secure_filename
from sqlalchemy import *
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import stat
import os
import sqlite3

UPLOAD_FOLDER = '/Studyist/userfiles'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "super secret key"

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def getApp():
    return app

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Tecra$2290@localhost/studyist'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
from models import Users, posts, images, files, replies, replyfiles, replyimages, materials


#the intro homepage for the user
@app.route("/", methods=["GET", "POST"])
def index():

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
            return render_template('homepage.html')
        #checks if the course requested is the same as one in the array
        return redirect(url_for('course', course = course))

    else:
        #grabs info from database and shows post onto the feed page
        # dbinfo = connectdb("posts.db")
        # postcursor = dbinfo[0]
        # postconnect = dbinfo[1]
        # postcursor.execute("SELECT * FROM posts ORDER BY date,time DESC;")
        # posting = postcursor.fetchall()
        postsalch = db.session.query(posts).order_by(posts.date.desc(),posts.time.desc()).all()
        #return object looking like <posts> which is an object
        #index into it and . insert what you are looking for

        return render_template("homepage.html", courses = courses, post = posts)


@app.route('/<course>', methods=["GET", "POST"])
def course(course):

    #grabs the classes and checks if class is a class in db
    courses = grabclasses()
    courseavailible = checkclass(course, courses)

    #if the class is not in the list, it will render an apology
    if courseavailible == False:
        flash('Class is not availible. Select Class from Options')
        return redirect(request.url)
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
        # If the user does not select a file, the browser submits an
        # empty file without a filename.

        #grabs the postid
        dbinfo = connectdb("posts.db")
        postcursor = dbinfo[0]
        postconnect = dbinfo[1]
        #fetches all of the post names and creates unique id's for each
        postcursor.execute("SELECT * FROM posts")
        posts = postcursor.fetchall()
        postslength = len(posts)
        id = postslength + 1
        #grabs the postid

        #gives permission to parent path
        parentpath = os.getcwd()
        parentpath = str(parentpath) + '/static'
        os.chmod(parentpath, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        os.chmod(parentpath, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        #gives permission to parent path

        #makes a new folder for the images. This makes it so that it can conserve it's name
        filespath = "static/userfiles/" + str(id)
        os.makedirs(filespath)
        #makes a new upload folder
        UPLOAD_FOLDER = filespath
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        files = request.files.getlist("file")
        for file in files:
            if file.filename != "":
                split_tup = os.path.splitext(file.filename)

                # extract the file name and extension
                file_name = split_tup[0]
                file_extension = split_tup[1]
                imagefileextensions = ['.png', '.jpg', '.jpeg', '.bmp' '.tiff', '.gif']
                #checks if image
                if file_extension in imagefileextensions:
                    filename = secure_filename(file.filename)
                    dbinfo = connectdb("posts.db")
                    postcursor = dbinfo[0]
                    postconnect = dbinfo[1]
                    postcursor.execute("INSERT INTO images VALUES (?, ?)", (id, file.filename));
                    postconnect.commit()
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
                else:
                    filename = secure_filename(file.filename)
                    dbinfo = connectdb("posts.db")
                    postcursor = dbinfo[0]
                    postconnect = dbinfo[1]
                    postcursor.execute("INSERT INTO files VALUES (?, ?)", (id, file.filename));
                    postconnect.commit()
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

        #connects to the post db
        dbinfo = connectdb("posts.db")
        postcursor = dbinfo[0]
        postconnect = dbinfo[1]
        #fetches all of the post names and creates unique id's for each
        postcursor.execute("SELECT * FROM posts")
        posts = postcursor.fetchall()
        postslength = len(posts)
        id = postslength + 1
        #inserts into db
        postcursor.execute("INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?)", (id, course, username, title, body, time, date));
        postconnect.commit()
        postconnect.close()

        return redirect(url_for('course', course = course))

    #db feches all the post from a cetain course
    dbinfo = connectdb("posts.db")
    postcursor = dbinfo[0]
    postconnect = dbinfo[1]
    postcursor.execute("SELECT * FROM posts WHERE class = ? ORDER BY date,time DESC;", (course,));
    posts = postcursor.fetchall()
    return render_template("coursemain.html", course = course, courses = courses, post = posts)


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
            images = "NULL"
            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

            if title == "" or body == "":
                error = "No input to the post"
                flash('No input to the post')
                return redirect(request.url)

            #connects to the post db
            dbinfo = connectdb("posts.db")
            replycursor = dbinfo[0]
            replyconnect = dbinfo[1]
            #fetches all of the post names and creates unique id's for each
            replycursor.execute("SELECT * FROM replies");
            replies = replycursor.fetchall()
            replieslength = len(replies)
            id = replieslength + 1
            images = "NULL"

            #inserts into db
            replycursor.execute("INSERT INTO replies VALUES (?, ?, ?, ?, ?, ?, ?)", (id, course, username, title, body, dt_string, postid ));
            replyconnect.commit()
            replyconnect.close()

            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename

            #gives permission to parent path
            parentpath = os.getcwd()
            parentpath = str(parentpath) + '/static'
            os.chmod(parentpath, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            os.chmod(parentpath, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            #gives permission to parent path

            #makes a new folder for the images. This makes it so that it can conserve it's name
            filepath = "static/userfiles-replies/" + str(id)
            os.makedirs(filepath)

            #makes a new upload folder
            UPLOAD_FOLDER = filepath
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
            files = request.files.getlist("file")

            #for every file, it will save it
            images = []
            for file in files:
                #if not empty
                if file.filename != "":
                    split_tup = os.path.splitext(file.filename)

                    # extract the file name and extension
                    file_name = split_tup[0]
                    file_extension = split_tup[1]
                    imagefileextensions = ['.png', '.jpg', '.jpeg', '.bmp' '.tiff', '.gif']

                    if file_extension in imagefileextensions:
                        filename = secure_filename(file.filename)
                        dbinfo = connectdb("posts.db")
                        replycursor = dbinfo[0]
                        replyconnect = dbinfo[1]
                        replycursor.execute("INSERT INTO replyimages VALUES (?, ?, ?)", (id, file.filename, postid));
                        replyconnect.commit()
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
                    else:
                        filename = secure_filename(file.filename)
                        dbinfo = connectdb("posts.db")
                        replycursor = dbinfo[0]
                        replyconnect = dbinfo[1]
                        replycursor.execute("INSERT INTO replyfiles VALUES (?, ?, ?)", (id, file.filename, postid));
                        replyconnect.commit()
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
                    replyconnect.close()

        return redirect(url_for('viewpost', course = course, postid = postid))


    #grab all of the courses
    courses = grabclasses()

    #grabs information for specific post id
    dbinfo = connectdb("posts.db")
    postcursor = dbinfo[0]
    postconnect = dbinfo[1]
    postcursor.execute("SELECT * FROM posts WHERE id = ?", (postid, ));
    post = postcursor.fetchone()
    postconnect.close()
    dbinfo = connectdb("posts.db")
    postcursor = dbinfo[0]
    postconnect = dbinfo[1]
    postcursor.execute("SELECT * FROM images WHERE postid = ?", (postid, ));
    images = postcursor.fetchall()
    postcursor.execute("SELECT * FROM files WHERE postid = ?", (postid, ));
    files = postcursor.fetchall()
    postconnect.close()

    postduration = time_difference(post[5],post[6])

    #If there is no post found
    if post == None:
        flash('post not availible')
        return redirect(request.url)

    #convert post data into a dictionary form
    post = {"id": post[0],
            "class": post[1],
            "username": post[2],
            "title": post[3],
            "body": post[4],
            "time" : post[5],
            "date" : post[6]
    }
    for i in range(len(images)):
        images[i] = {"imageid": images[i][1]

        }

    for i in range(len(files)):
        files[i] = {"fileid": files[i][1]

        }

    #grabs all info for replies
    dbinfo = connectdb("posts.db")
    replycursor = dbinfo[0]
    replyconnect = dbinfo[1]
    replycursor.execute("SELECT * FROM replies WHERE postid = ?", (postid,));
    replies = replycursor.fetchall()

    replycursor.execute("SELECT * FROM replyimages WHERE postid = ?", (postid,));
    replyimages = replycursor.fetchall()

    replycursor.execute("SELECT * FROM replyfiles WHERE postid = ?", (postid,));
    replyfiles = replycursor.fetchall()
    replyconnect.close()

    #converts Reply data into a dictionary
    for i in range(len(replyimages)):
                    replyimages[i] = {"replyid": int(replyimages[i][0]),
                        "replyimageid": replyimages[i][1],
                        "postid": replyimages[i][2]
                    }

    for i in range(len(replyfiles)):
                    replyfiles[i] = {"replyid": int(replyfiles[i][0]),
                        "replyfileid": replyfiles[i][1],
                        "postid": replyfiles[i][2]
                    }

    for i in range(len(replies)):
        replies[i] = {"id": int(replies[i][0]),
                      "class": replies[i][1],
                      "username": replies[i][2],
                      "title": replies [i][3],
                      "body": replies[i][4],
                      "timedate": replies[i][5]
        }


    session_user_id = session["user_id"]
    return render_template("viewpost.html", postid = postid, images = images, files = files, replyfiles = replyfiles, replyimages = replyimages, post = post, courses = courses, course = course, replies = replies, session_user_id = session_user_id, )




@app.route('/resources/<route>', methods=["GET", "POST"])
def resources(route):
    #saves route created and checks if peson put in a correct course
    currentfolderrouteurl = route
    routeparts = route.split(">")
    print("routeparts" + str(routeparts))
    route = str()
    for i in range(len(routeparts)):
        route = route + "/" + routeparts[i]
    course = routeparts[0]
    courses = grabclasses()
    courseavailible = checkclass(course, courses)
    #saves route created and checks if peson put in a correct course

    #if the class is not in the list, it will render an apology
    if courseavailible == False:
        flash('Class is not availible. Select Class from Options')
        return redirect(url_for('course', course = course))
    print("yo")
    if request.method == "POST":
        print("hey")
        #gathers information for database entry
        type_of_form = request.form.get("type_of_form")
        username = session["user_id"]
        objectroute = route

        now = datetime.now()
        date = now.strftime("%m/%d/%Y")
        time = now.strftime("%H:%M:%S")

        #grabs the postid
        dbinfo = connectdb("resources.db")
        resourcescursor = dbinfo[0]
        resourcesconnect = dbinfo[1]
        #fetches all of the post names and creates unique id's for each
        resourcescursor.execute("SELECT * FROM materials")
        resources = resourcescursor.fetchall()
        resourceslength = len(resources)
        id = resourceslength + 1
        #grabs the postid

        if type_of_form == "uploadfile":
            title = request.form.get("title")
            title = str(title)

            #if there is no inputs, return an error
            if title == "":
                flash('No input to required parts')
                return redirect(request.url)

            #check if the post request has the file part
            print(request.files)
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # If the user does not select a file, the browser submits an
            # empty file without a filename.

            #gives permission to parent path
            parentpath = os.getcwd()
            staticpath = str(parentpath) + '/static'
            os.chmod(parentpath, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            os.chmod(staticpath, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            #gives permission to parent path

            #makes a new folder for the images. This makes it so that it can conserve it's name
            filespath = "static/resources/" + str(course)
            if os.path.exists(filespath):
                print("it exists")
            else:
                print("hey")
                os.makedirs(filespath)
            #makes a new upload folder if the upload folder does not exist
            UPLOAD_FOLDER = "static/resources/" + str(route)
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
            files = request.files.getlist("file")
            username = session["user_id"]
            resourcesconnect.commit()
            #makes a new upload folder if the upload folder does not exist

            for file in files:
                if file.filename != "":
                    split_tup = os.path.splitext(file.filename)

                    # extract the file name and extension
                    file_name = split_tup[0]
                    file_extension = split_tup[1]
                    imagefileextensions = ['.png', '.jpg', '.jpeg', '.bmp' '.tiff', '.gif']
                    #checks if image
                    if file_extension in imagefileextensions:
                        objecttype = "file"
                        filename = file.filename
                        resourcescursor.execute("INSERT INTO materials VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (id, objectroute, objecttype, course, username, filename, time, date));
                        resourcesconnect.commit()
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
                    else:
                        objecttype = "file"
                        filename = file.filename
                        resourcescursor.execute("INSERT INTO materials VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (id, objectroute, objecttype, course, username, filename, time, date));
                        resourcesconnect.commit()
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
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
            filespath = "static/resources" + str(route) + "/" + str(foldername)
            if os.path.exists(filespath):
                print("it exists")
                return(request.url)
            else:
                print("hey")
                os.makedirs(filespath)

            #enter folder information into database
            dbinfo = connectdb("resources.db")
            objecttype = "folder"
            resourcescursor = dbinfo[0]
            resourcesconnect = dbinfo[1]
            resourcescursor.execute("INSERT INTO materials VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (id, objectroute, objecttype, course, username, foldername, time, date));
            resourcesconnect.commit()
            resourcesconnect.close

    #grab the materials
    dbinfo = connectdb("resources.db")
    resourcescursor = dbinfo[0]
    resourcesconnect = dbinfo[1]
    filetype = "file"
    resourcescursor.execute("SELECT * FROM materials WHERE objectroute = ? AND objecttype = ?", (route, filetype, ));
    materials = resourcescursor.fetchall()
    resourcesconnect.close
    #grab the materials

    #grab the folders
    dbinfo = connectdb("resources.db")
    resourcescursor = dbinfo[0]
    resourcesconnect = dbinfo[1]
    filetype = "folder"
    resourcescursor.execute("SELECT * FROM materials WHERE objectroute = ? AND objecttype = ?", (route, filetype, ));
    folders = resourcescursor.fetchall()
    resourcesconnect.close
    #grab the folders

    return render_template("resources.html",currentfolderrouteurl = currentfolderrouteurl, course = course, folders = folders, materials = materials, route = route)



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
        dbinfo = connectdb("posts.db")
        postcursor = dbinfo[0]
        postconnect = dbinfo[1]
        now = datetime.now()
        nowdate = now.strftime("%m/%d/%Y")
        nowdate = datetime.strptime(nowdate,"%m/%d/%Y")
        postcursor.execute("SELECT * FROM posts ORDER BY date DESC, time DESC;")
        posts = postcursor.fetchall()
        print(posts)
    else:
        dbinfo = connectdb("posts.db")
        postcursor = dbinfo[0]
        postconnect = dbinfo[1]
        postcursor.execute("SELECT * FROM posts WHERE class = ? ORDER BY date DESC,time DESC;", (course,));
        posts = postcursor.fetchall()
        print(posts)

    posts = jsonify(posts)
    return(posts)

@app.route('/getresources', methods=["GET", "POST"])
def getresources():
    course = request.json
    dbinfo = connectdb("resources.db")
    resourcescursor = dbinfo[0]
    resourcesconnect = dbinfo[1]
    filetype = "file"
    resourcescursor.execute("SELECT * FROM materials WHERE objectroute = ? AND objecttype = ?", (course, filetype, ));
    materials = resourcescursor.fetchall()
    resourcesconnect.close
    resources = jsonify(materials)
    return(resources)

@app.route('/getfolders', methods=["GET", "POST"])
def getfolders():
    course = request.json
    print(course)
    dbinfo = connectdb("resources.db")
    resourcescursor = dbinfo[0]
    resourcesconnect = dbinfo[1]
    filetype = "folder"
    resourcescursor.execute("SELECT * FROM materials WHERE objectroute = ? AND objecttype = ?", (course, filetype, ));
    folders = resourcescursor.fetchall()
    print(folders)
    resourcesconnect.close
    folders = jsonify(folders)
    return(folders)