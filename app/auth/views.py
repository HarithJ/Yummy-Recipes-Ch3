from flask import render_template, redirect, url_for, request, session, g, abort, flash
from flask_login import login_required, login_user, logout_user, current_user
import jwt
import datetime

from . import auth
from ..models import User, Ingredient, Recipe
from app import validate_input, db

@auth.route('/')
@auth.route('/index.html/')
def index():
    """This function takes a user to index.html page (homepage) which displays a registration form and a link to login page."""

    return render_template("index.html")


@auth.route('/login.html/')
def login_page():
    """function renders a template for logging in"""
    return render_template("login.html")

@auth.route('/register/', methods=['POST'])
def register():
    """This function is there to register a user"""
    error = None

    #: check if the user inputted leading spaces
    if validate_input(request.form['first_name']) or validate_input(request.form['email']):
        error = 'Leading spaces inserted in name/email field!'

    # check if the password and ver password are not the same
    if request.form['password'] != request.form['verpassword']:
        error = 'Password does not match the password in verify password field'

    if error:
        flash(error)
        return redirect(url_for('auth.index'))

    user = User(email = request.form['email'],
                username = request.form['username'],
                first_name = request.form['first_name'],
                last_name = request.form['last_name'],
                password = request.form['password'])

    # add user to the database
    db.session.add(user)
    db.session.commit()
    flash('You have successfully registered! You may login')

    return redirect(url_for('auth.login_page'))

@auth.route('/validate/', methods=['POST'])
def validate():
    """This function validates the login credentials entered by a user in login form"""

    user = User.query.filter_by(email=request.form['email']).first()
    if user is not None and user.verify_password(request.form['password']):
        login_user(user)
        token = user.generate_token(user.id)
        return redirect(url_for('categories.profile', token=token))

    #: if incorrect credentials are entered then display a flash message to the user
    flash("Incorrect Credentials Entered")
    return redirect(url_for('auth.login_page'))

@auth.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You have successfully loged out!')
    return redirect(url_for('auth.login_page'))