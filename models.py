from app import db_creation as db

class Users(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    gradeappusername=db.Column(db.String(120), nullable=False)
    gradeapppassword=db.Column(db.String(120), nullable=False)
    google_auth = db.Column(db.String(120), nullable=False)
    is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    auth_try_on = db.Column(db.DateTime, nullable=True)

    def verify_password(self, password):
        pwhash = bcrypt.hashpw(password, self.password)
        return self.password == pwhash

    def __init__(self,username, password, email):
        self.username = username
        self.password = password
        self.email = email
        self.gradeappusername = gradeappusername
        self.gradeapppassword = gradeapppassword
        self.google_auth = google_auth
        self.is_confirmed = is_confirmed
        self.confirmed_on = confirmed_on
        self.auth_try_on = auth_try_on

class APIUsers(db.Model):
    __tablename__ = 'API_Users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    gradeappusername=db.Column(db.String(120), nullable=False)
    gradeapppassword=db.Column(db.String(120), nullable=False)
    google_auth = db.Column(db.String(120), nullable=False)
    is_confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    auth_try_on = db.Column(db.DateTime, nullable=True)

    def verify_password(self, password):
        pwhash = bcrypt.hashpw(password, self.password)
        return self.password == pwhash

    def __init__(self,username, password, email):
        self.username = username
        self.password = password
        self.email = email
        self.gradeappusername = gradeappusername
        self.gradeapppassword = gradeapppassword
        self.google_auth = google_auth
        self.is_confirmed = is_confirmed
        self.confirmed_on = confirmed_on
        self.auth_try_on = auth_try_on

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
    user_id = db.Column(db.Integer, nullable=False)

    def __init__(self, postid, course, username, title, body, time, date):
        self.postid = postid
        self.course = course
        self.username = username
        self.title = title
        self.body = body
        self.time = time
        self.date = date
        self.user_id = user_id
        

class images(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    postid = db.Column(db.Integer,nullable=False)
    images = db.Column(db.Text,nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    
    def __init__(self,postid, images):
        self.postid = postid
        self.images = images
        self.user_id = user_id

class files(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    postid = db.Column(db.Integer,nullable=False)
    files = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    def __init__(self,postid, files):
        self.postid = postid
        self.files = files
        self.user_id = user_id


#models for replies
class replies(db.Model):
    __tablename__ = 'replies'
    id = db.Column(db.Integer, primary_key=True)
    replyid = db.Column(db.Integer,nullable=False)
    postid = db.Column(db.Integer,nullable=False)
    course = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    title = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    def __init__(self, replyid, postid, course, username, title, body, time, date):
        self.replyid = replyid
        self.postid = postid
        self.course = course
        self.username = username
        self.title = title
        self.body = body
        self.time = time
        self.date = date
        self.user_id = user_id

class replyimages(db.Model):
    __tablename__ = 'replyimages'
    id = db.Column(db.Integer, primary_key=True)
    replyid = db.Column(db.Integer,nullable=False)
    postid = db.Column(db.Integer,nullable=False)
    images = db.Column(db.Text,nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    def __init__(self, replyid, postid, images):
        self.replyid = replyid
        self.postid = postid
        self.images = images
        self.user_id = user_id
        self.user_id = user_id


class replyfiles(db.Model):
    __tablename__ = 'replyfiles'
    id = db.Column(db.Integer, primary_key=True)
    replyid = db.Column(db.Integer,nullable=False)
    postid = db.Column(db.Integer,nullable=False)
    files = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    def __init__(self, replyid, postid, files):
        self.replyid = replyid
        self.postid = postid
        self.files = files
        self.user_id = user_id

#models for materials

class materials(db.Model):
    __tablename__ = 'materials'
    id = db.Column(db.Integer, primary_key=True)
    resourceid = db.Column(db.Integer,nullable=False)
    objectroute = db.Column(db.Text, nullable=False)
    objecttype = db.Column(db.String(80), nullable=False)
    course = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    name = db.Column(db.Text, nullable=False)
    time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False)
    title = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    user_access_names = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    def __init__(self, resourceid, objectroute, objecttype, course, username,name, time, date):
        self.resourceid = resourceid
        self.objectroute = objectroute
        self.objecttype = objecttype
        self.course = course
        self.username = username
        self.name = name
        self.time = time
        self.date = date
        self.title = title
        self.body = body
        self.user_id = user_id

#models for classes
class classes(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(80),nullable=False)

    def __init__(self,postid, files):
        self.type = type
        self.name = name
        self.user_id = user_id