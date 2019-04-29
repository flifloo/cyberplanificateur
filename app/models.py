from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
import tweepy, twitter_credentials, trello, trello_credentials

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    twitter_api = db.relationship("TwitterAPI", backref="user", lazy="dynamic")
    tweets = db.relationship("Tweets", backref="user", lazy="dynamic")
    trello_api = db.relationship("TrelloAPI", backref="user", lazy="dynamic")
    boards = db.relationship("Boards", backref="user", lazy="dynamic")

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

    def api_login(self):
        auth = tweepy.OAuthHandler(twitter_credentials.consumer_key, twitter_credentials.consumer_secret_key)
        auth.set_access_token(self.access_token, self.access_token_secret)
        return tweepy.API(auth)

class Tweets(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    statu_id = db.Column(db.Integer, unique=True)
    slots = db.Column(db.Integer)
    slots_max = db.Column(db.Integer)
    keywords = db.Column(db.String(256))

class TrelloAPI(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True)
    token = db.Column(db.String(64), unique=True)

    def api_login(self):
        return trello.TrelloClient(api_key = trello_credentials.api_key, token = self.token)

class Boards(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True)
    board_id = db.Column(db.String(24))
    column_id = db.Column(db.String(24))

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
