from flask import Flask, flash, redirect, url_for
from functools import wraps
import re

from config import app_config
from .models import Globals

def validate_input(input_str):
    if re.match('^\s', input_str) or input_str == '':
        return True

def login_required(f):
    """
    Check if a user is logged in or not
    If a user if not logged in, then redirect them to login page
    with a flash msg.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if Globals.current_user == None:
            flash("You must be logged in to access this page. :)")
            return redirect(url_for('auth.login_page'))

        return f(*args, **kwargs)
    return wrapper

def category_required(f):
    """
    First, check if a user is logged in or not,
    if he is logged in, then check if he has selected a category or not,
    if he has not selected a category then redirect him to categories page.
    """
    @login_required
    @wraps(f)
    def wrapper(*args, **kwargs):
        if Globals.current_category == None:
            flash("You must select a category first to view the recipes ;)")
            return redirect(url_for('categories.categories_page'))

        return f(*args, **kwargs)
    return wrapper

def create_app(config_name):
    app = Flask(__name__, static_folder='../designs/UI', template_folder='../designs/UI', instance_relative_config=True)

    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .categories import categories as categories_blueprint
    app.register_blueprint(categories_blueprint)

    from .recipes import recipes as recipes_blueprint
    app.register_blueprint(recipes_blueprint)


    return app