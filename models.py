from app import db

class Users(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def verify_password(self, password):
        pwhash = bcrypt.hashpw(password, self.password)
        return self.password == pwhash

    def __init__(self,username, password, email):
        self.username = username
        self.password = password
        self.email = email

#models for postings
class posts(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    postid = db.Column(db.Integer,nullable=False)
    course = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    title = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)

    def __init__(self, postid, course, username, title, body, time, date):
        self.postid = postid
        self.course = course
        self.username = username
        self.title = title
        self.body = body
        self.time = time
        self.date = date
        

class images(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    postid = db.Column(db.Integer,nullable=False)
    images = db.Column(db.Text,nullable=False)
    
    def __init__(self,postid, images):
        self.postid = postid
        self.images = images

class files(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    postid = db.Column(db.Integer,nullable=False)
    files = db.Column(db.Text, nullable=False)

    def __init__(self,postid, files):
        self.postid = postid
        self.files = files

#models for replies
class replies(db.Model):
    __tablename__ = 'replies'
    id = db.Column(db.Integer, primary_key=True)
    postid = db.Column(db.Integer,nullable=False)
    course = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    title = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)

    def __init__(self, postid, course, username, title, body, time, date):
        self.postid = postid
        self.course = course
        self.username = username
        self.title = title
        self.body = body
        self.time = time
        self.date = date

class replyimages(db.Model):
    __tablename__ = 'replyimages'
    id = db.Column(db.Integer, primary_key=True)
    postid = db.Column(db.Integer,nullable=False)
    images = db.Column(db.Text,nullable=False)

    def __init__(self,postid, images):
        self.postid = postid
        self.images = images


class replyfiles(db.Model):
    __tablename__ = 'replyfiles'
    id = db.Column(db.Integer, primary_key=True)
    postid = db.Column(db.Integer,nullable=False)
    files = db.Column(db.Text, nullable=False)

    def __init__(self,postid, files):
        self.postid = postid
        self.files = files

#models for materials

class materials(db.Model):
    __tablename__ = 'materials'
    id = db.Column(db.Integer, primary_key=True)
    postid = db.Column(db.Integer,nullable=False)
    objectroute = db.Column(db.Text, nullable=False)
    objecttype = db.Column(db.String(80), nullable=False)
    course = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    name = db.Column(db.Text, nullable=False)
    time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)

    def __init__(self, postid, course, username, title, body, time, date):
        self.postid = postid
        self.course = course
        self.username = username
        self.title = title
        self.body = body
        self.time = time
        self.date = date

#models for classes
class classes(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(80),nullable=False)

    def __init__(self,postid, files):
        self.type = type
        self.name = name