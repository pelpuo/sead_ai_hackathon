from flask import Flask
import os
from os import path
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import re



def create_database(app):
    if not path.exists("main/"+ DB_NAME):
        db.create_all(app=app)
        print('Created db')


db = SQLAlchemy()
DB_NAME = "database.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"

app.config['UPLOAD_FOLDER'] = '/uploads'


app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{DB_NAME}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

from .views import views
from .auth import auth
from .handlers import handlers

app.register_blueprint(views, url_prefix="/")
app.register_blueprint(auth, url_prefix="/")
app.register_blueprint(handlers, url_prefix="/")


from .models import User

create_database(app)

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))



