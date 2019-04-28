import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = "*i9uld6u@t!kxl9%o+byxqf14&a&&@y@q=l$!lg4m%b-a*^o(a"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "database.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
