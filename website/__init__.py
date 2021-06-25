from flask import Flask
import os
from os import path
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import re

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app(ENV):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "secret"

    app.config['UPLOAD_FOLDER'] = '/uploads'


    # Configuring Database
    if ENV == 'dev' or ENV == 'prod':
        # app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:panda@localhost/sead_ai-hackathon'  
        app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{DB_NAME}'
    else:
        uri = os.environ.get("DATABASE_URL")
        # app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{DB_NAME}'
        if uri.startswith("postgres://"):
            uri = uri.replace("postgres://", "postgresql://", 1)
        app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://mmunhpcapmkfzy:ee4436a12899f9d7a1e7e5e57543521e0f156855c6e97db0e75cf18efb0c432c@ec2-54-74-156-137.eu-west-1.compute.amazonaws.com:5432/d7afb3l6c1abb8'

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

    return app


def create_database(app):
    if not path.exists("website/"+ DB_NAME):
        db.create_all(app=app)
        print('Created db')