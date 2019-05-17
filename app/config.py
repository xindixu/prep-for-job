import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'postgres://yvfdrppflgskzs:72f1d199b0aba877f86c806d70687204a758fa07485a99faca28ec05167bec56@ec2-54-163-226-238.compute-1.amazonaws.com:5432/desked1nc70ett'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']