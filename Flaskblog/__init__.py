#init.py
from flask_bcrypt import Bcrypt
from flask import Flask

from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager


app = Flask(__name__)
app.app_context().push()


app.config['SECRET_KEY']= '06a0ac6eea0d291331e951fc3f3d3ae5'
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///site.db'


db = SQLAlchemy(app)
bcrypt=Bcrypt(app)
login_manager=LoginManager(app)
from Flaskblog import routes