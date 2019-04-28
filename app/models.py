from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    twitter_api = db.relationship("TwitterAPI", backref="user", lazy="dynamic")
    trello_api = db.relationship('TrelloAPI', backref="user", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

class TwitterAPI(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True)
    access_token = db.Column(db.String(50), unique=True)
    access_token_secret = db.Column(db.String(45), unique=True)

class TrelloAPI(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True)
    token = db.Column(db.String(64), unique=True)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
