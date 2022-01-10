from flask import Flask, flash, redirect, render_template, request, session, url_for
from helpers import login_required, grabclasses, checkclass, check, connectdb
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import sqlite3

UPLOAD_FOLDER = '/Studyist/userimages'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
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

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


@app.route("/homepage/apology", methods= ["GET", "POST"])
def apology(error):
    #if there is an error, goes to apology page
    print(error)
    return render_template("apology.html", error = error)


#the intro homepage for the user
@app.route("/", methods=["GET", "POST"])
def index():
    session.clear()
    # if the form is submitted
    if request.method == "POST":

        #Get password/confirmation information
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        #if information not filled in
        if password == "" or username == "" or email == "":
            formsubmission = False
            flash("Sign Up Form missing an element")
            return redirect(request.url)

        #if password does not match confirmation of password
        if password != confirmation:
            formsubmission = False
            print("hello")
            flash("Confirmation Password and Password do not match")
            return redirect(request.url)

        #checks if email is writen correctly
        emailvalidation = check(email)
        if emailvalidation == "invalid":
            formsubmission = False
            error = "invalid email address"
            flash("invalid email address")
            return redirect(request.url)

        #goes to function that connects db
        dbinfo = connectdb("userinfo.db")
        #seperate list into db objects
        userinfocursor = dbinfo[0]
        userinfoconnect = dbinfo[1]

        #checks if email is already in the system | cant be 2 of the same email
        userinfocursor.execute("SELECT email FROM users WHERE email = ?", (email, ));
        stored_email = userinfocursor.fetchone()
        print(stored_email)
        if stored_email != None:
            print("yo")
            error = "invalid email address"
            flash("email already has been used")
            return redirect(request.url)

        #checks if username is already in the system | cant be 2 of same username
        userinfocursor.execute("SELECT username FROM users WHERE username = ?", (username, ));
        stored_username = userinfocursor.fetchone()
        userinfoconnect.close()
        print(stored_username)
        if stored_username != None:
            print("yo")
            error = "invalid email address"
            flash("username already has been used")
            return redirect(request.url)

        # after checks, insert into db
        dbinfo = connectdb("userinfo.db")
        userinfodb = dbinfo[0]
        userinfoconnect = dbinfo[1]
        userinfodb.execute("INSERT INTO users VALUES (?, ?, ?)", (username, password, email));
        userinfoconnect.commit()
        userinfoconnect.close()
        return redirect("/")

    else:
        return render_template("intro.html")



@app.route("/login", methods=["GET", "POST"])
def login():

    #connects to db and checks if account is valid
    session.clear()
    dbinfo = connectdb("userinfo.db")
    userinfocursor = dbinfo[0]
    userinfoconnect = dbinfo[1]
    email = request.form.get("email")
    password = request.form.get("password")
    userinfocursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password, ));
    user = userinfocursor.fetchone()
    userinfocursor.execute("SELECT username FROM users WHERE email = ? AND password = ?", (email, password, ));
    username = userinfocursor.fetchone()
    userinfoconnect.close()

    #if the user is not found, the password or username must be incorrect
    #redirect back to index page
    if user == None:
        flash("username or password is incorrect or no user is found")
        return redirect("/")
    else:
    #login successful redirects to homepage with feed
        username = username[0]
        session["user_id"] = username
        return redirect("homepage")


@app.route("/homepage", methods=["GET", "POST"])
@login_required
def studyist():
    courses = grabclasses()
    if request.method == "POST":
        #looks in the classes db to find all of the classes
        course = request.form.get("name")
        courseavailible = checkclass(course, courses)
        if courseavailible == False:
            error = "Class is not availible. Select Class from Options"
            return render_template('apology.html', error = error)
        print(courses)
        #checks if the course requested is the same as one in the array
        return redirect(url_for('course', course = course))

    else:
        return render_template("homepage.html", courses = courses)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/<course>', methods=["GET", "POST"])
def course(course):
    print(course)
    #grabs the classes and checks if class is a class in db
    courses = grabclasses()
    courseavailible = checkclass(course, courses)
    #if the class is not in the list, it will render an apology
    if courseavailible == False:
        error = "Class is not availible. Select Class from Options"
        return render_template('apology.html', error = error)
    #if there is a post request, it will redirect to a page where you can post
    # else it will render the course page requested
    checkclass(course, courses)

    if request.method == "POST":
        print("ye")
        #check if the post request has the file part
        if 'file' not in request.files:
            print("not going here")
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            print("does not detect the file")
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            print("everything should be going as it should be. :(")
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return 0
        
        print("heeeheheheh")
        #gathers information for database entry
        title = request.form.get("title")
        title = str(title)
        body = request.form.get("text")
        body = str(body)
        username = session["user_id"]
        images = "NULL"
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        #if there is no inputs, return an error
        if title == "" or body == "":
            error = "No input to the post"
            return render_template('apology.html', error = error)

        print("dhdhdhdhdhdhhdhhS")
        #connects to the post db
        dbinfo = connectdb("posts.db")
        postcursor = dbinfo[0]
        postconnect = dbinfo[1]
        #fetches all of the post names and creates unique id's for each
        postcursor.execute("SELECT * FROM posts")
        posts = postcursor.fetchall()
        postslength = len(posts)
        print(postslength)
        id = postslength + 1

        #inserts into db
        postcursor.execute("INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?)", (id, course, username, title, body, images, dt_string));
        postconnect.commit()
        postconnect.close()

        return redirect(url_for('course', course = course))

    #db feches all the post from a cetain course
    dbinfo = connectdb("posts.db")
    postcursor = dbinfo[0]
    postconnect = dbinfo[1]
    postcursor.execute("SELECT * FROM posts WHERE class = ?", (course,));
    posts = postcursor.fetchall()
    return render_template("coursemain.html", course = course, courses = courses, post = posts)


@app.route('/<course>/postcreation', methods=["GET", "POST"])
@login_required
def post(course):
    print("high")
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
                return render_template('apology.html', error = error)

            #connects to the post db
            dbinfo = connectdb("posts.db")
            replycursor = dbinfo[0]
            replyconnect = dbinfo[1]
            #fetches all of the post names and creates unique id's for each
            replycursor.execute("SELECT * FROM replies");
            replies = replycursor.fetchall()
            replieslength = len(replies)
            print(replieslength)
            id = replieslength + 1
            images = "NULL"

            #inserts into db
            replycursor.execute("INSERT INTO replies VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (id, course, username, title, body, dt_string, postid, images));
            replyconnect.commit()
            replyconnect.close()

        return redirect(url_for('viewpost', course = course, postid = postid))
    #grab all of the courses
    courses = grabclasses()
    #convert postid into integer

    #connect and check if the post db has a post id of that number
    dbinfo = connectdb("posts.db")
    postcursor = dbinfo[0]
    postconnect = dbinfo[1]
    postcursor.execute("SELECT * FROM posts WHERE id = ?", (postid, ));
    post = postcursor.fetchone()
    postconnect.close()



    #if not, return apology
    if post == None:
        error = "post not availible"
        return render_template('apology.html', error = error)


    dbinfo = connectdb("posts.db")
    replycursor = dbinfo[0]
    replyconnect = dbinfo[1]
    replycursor.execute("SELECT * FROM replies WHERE postid = ?", (postid,));
    replies = replycursor.fetchall()
    print(replies)
    return render_template("viewpost.html", postid = postid, post = post, courses = courses, course = course, replies = replies, )



