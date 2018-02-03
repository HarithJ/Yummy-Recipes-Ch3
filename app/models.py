import os
from flask_login import UserMixin, login_required, current_user
from flask import flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
from flask import jsonify, request
from datetime import datetime, timedelta
from flask_restplus import abort
import flask_whooshalchemy

from sqlalchemy.exc import IntegrityError

from config import Config

from app import db, login_manager

class Globals():
    current_category = None

class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    ing = db.Column(db.String(100))

    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"))


class Recipe(db.Model):
    __tablename__ = 'recipes'
    __table_args__ = {'extend_existing': True}
    __searchable__ = ['title']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    recipe_ingredients = db.relationship('Ingredient', backref='ingredient', lazy='dynamic', cascade="all, delete-orphan")
    directions = db.Column(db.String(10000))
    filename = db.Column(db.String(100))

    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))

    __table_args__ = (db.UniqueConstraint('category_id', 'title', name='_category_title_uc'),
                     )

class Category(db.Model):
    __tablename__ = 'categories'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    category_recipes = db.relationship('Recipe', backref='recipe', lazy='dynamic', cascade="all, delete-orphan")

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    __table_args__ = (db.UniqueConstraint('user_id', 'name', name='_user_category_uc'),
                     )

    def add_recipe(self, recipe_title, ingredients, directions, filename):
        for i in range(len(ingredients)):
            ingredients[i] = Ingredient(ing=ingredients[i])
            db.session.add(ingredients[i])

        try:
            recipe = Recipe(title = recipe_title, recipe_ingredients = ingredients, directions = directions, filename = filename)

            self.category_recipes.append(recipe)
            db.session.add(recipe)

            db.session.commit()
        except:
            db.session.rollback()
            abort(409, 'The recipe title already exists.')

    def get_recipes(self):
        return self.category_recipes.all()

    def edit_recipe(self, data, *args, **kwargs):
        edit_this = None
        if 'id' in kwargs:
            edit_this = Recipe.query.filter_by(id=kwargs['id']).filter_by(category_id=self.id).first()
        else:
            edit_this = Recipe.query.filter_by(title=kwargs['prev_title']).filter_by(category_id=self.id).first()

        if edit_this == None:
            return {'message' : 'recipe not found'}, 404

        try:
            if 'title' in data:
                edit_this.title = data['title']
                data.pop('title')

            if 'directions' in data:
                edit_this.directions = data['directions']
                data.pop('directions')

            if 'filename' in data:
                edit_this.filename = data['filename']
                data.pop('filename')

            if data:
                ing_num = 1
                for ingredient in edit_this.recipe_ingredients:
                    ing = 'ingredient{}'.format(ing_num)
                    if ing in data:
                        ingredient.ing = data[ing]
                        data.pop(ing)
                        db.session.commit()
                    ing_num += 1

        except IntegrityError:
                db.session.rollback()
                abort(409, 'The recipe title already exists.')
        """
        if data:
            for key, value in data.items():
                if 'ingredient' in key:
                    ingredient = Ingredient(ing=value, recipe_id=edit_this.id)
                    db.session.add(ingredient)

        db.session.commit()

        """
        return {'message' : 'Edited successfully'}

    def delete_recipe(self, recipe_title):
        delete_this = Recipe.query.filter_by(title=recipe_title).filter_by(category_id=self.id).first()

        if delete_this.filename != 'noImage':
            os.remove(os.path.join(Config.UPLOAD_FOLDER, delete_this.filename))

        db.session.delete(delete_this)
        db.session.commit()

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



class User(UserMixin, db.Model):
    '''
    Create a user table
    '''
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    password_hash = db.Column(db.String(128))
    reset_password_token_hash = db.Column(db.String(128))
    user_categories = db.relationship('Category', backref='categories', lazy='dynamic', cascade="all, delete-orphan")

    @property
    def password(self):
        '''
        Prevent Password from being accessed
        '''
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        '''
        Set password to a hashed password
        '''
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        '''
        check if hashed password matches actual password
        '''
        return check_password_hash(self.password_hash, password)

    def reset_password(self, password):
        self.password_hash = generate_password_hash(password)

        db.session.commit()

    def edit_category(self, prev_name, new_name):
        edit_this = Category.query.filter_by(name=prev_name).filter_by(user_id=self.id).first()
        edit_this.name = new_name

        db.session.commit()

    def return_category(self, category_name):
        return Category.query.filter_by(name=category_name).filter_by(user_id=self.id).first()

    def delete_category(self, category_name):
        delete_this = Category.query.filter_by(name=category_name).filter_by(user_id=self.id).first()

        db.session.delete(delete_this)
        db.session.commit()

    def generate_token(self, user_id):
        """ Generates the access token"""

        try:
            # set up a payload with an expiration time
            payload = {
                'exp': datetime.utcnow() + timedelta(hours=5),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            # create the byte string token using the payload and the SECRET key
            jwt_string = jwt.encode(
                payload,
                'testing',
                algorithm='HS256'
            )
            return jwt_string

        except Exception as e:
            # return an error in string format if an exception occurs
            return str(e)

    @staticmethod
    def decode_token(token):
        """Decodes the access token from the Authorization header."""
        try:
            # try to decode the token using our SECRET variable
            payload = jwt.decode(token, 'testing')
            return payload['sub']
        except jwt.ExpiredSignatureError:
            # the token is expired, return an error string
            return "Expired token. Please login to get a new token"
        except jwt.InvalidTokenError:
            # the token is invalid, return an error string
            return "Invalid token. Please register or login"

    def token_required(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = None

            if 'x-access-token' in request.headers:
                token = request.headers['x-access-token']

            if not token:
                return jsonify({'message' : 'Token is missing'}), 401

            try:
                data = self.decode_token(token)
                current_user = User.query.filter_by(id=data['id']).first()
            except:
                return jsonify({'message' : 'Token is invalid'}), 401

            return f(current_user, *args, **kwargs)
        return wrapper


    def __repr__(self):
        return '{} {}'.format(self.first_name, self.last_name)

#set up user loader which Flask-Login uses to reload the user object from the user ID stored in the session.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




