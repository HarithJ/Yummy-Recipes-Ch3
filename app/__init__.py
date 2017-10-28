from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate #Migrations allow us to manage changes we make to the models, and propagate these changes in the database.

from sqlalchemy import Integer, Column, String, create_engine, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, backref

#local imports
from config import app_config

#db var init
db = SQLAlchemy()
#init loginmanager object
login_manager = LoginManager()

def create_app(config_name):
    #init the app
    #Note that if we set instance_relative_config to True,
    #we can use app.config.from_object('config') to load the config.py file.
    app = Flask(__name__, instance_relative_config = True, static_folder='../designs/UI', template_folder='../designs/UI')

    #Load the config file
    app.config.from_object(app_config[config_name])

    app.config.from_pyfile('config.py')

    db.init_app(app)

    #if a user tries to access a page that they are not authorized to,
    #it will redirect to the specified view and display the specified message.
    login_manager.init_app(app)
    login_manager.login_message = "You must be logged in to access this page."
    login_manager.login_view = "auth.login_page"

    migrate = Migrate(app, db) #allow us to run migrations using Flask-Migrate.

    from app import models

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)


    return app






