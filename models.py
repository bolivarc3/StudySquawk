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

    def __repr__(self):
        return '<User %r>' % self.username