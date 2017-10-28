from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    ing = db.Column(db.String(100))

    recipe_id = db.Column(db.Integer, db.ForeignKey("recipes.id"))



class Recipe(db.Model):
    __tablename__ = 'recipes'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    recipe_ingredients = db.relationship('Ingredient', backref='ingredient', lazy='dynamic')
    directions = db.Column(db.String(10000))

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

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
    user_recipes = db.relationship('Recipe', backref='recipe', lazy='dynamic')

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

    def __repr__(self):
        return '{} {}'.format(self.first_name, self.last_name)

#set up user loader which Flask-Login uses to reload the user object from the user ID stored in the session.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




