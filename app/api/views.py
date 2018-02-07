import re

from flask import request, render_template
from flask_login import login_required, login_user, logout_user, current_user
from flask_restplus import Resource, fields, abort, reqparse
from flask_mail import Message
from sqlalchemy import literal
from sqlalchemy_searchable import search

from sqlalchemy.exc import IntegrityError

from . import api
from app import db, mail
from ..models import Category, User, Recipe

user_registration_format = api.model('UserRegistration', {
    'first_name' : fields.String('Your first name'),
    'last_name' : fields.String('Your last name'),
    'username' : fields.String('User name'),
    'email' : fields.String('Your e-mail'),
    'password' : fields.String('Password')
})

user_basic_format = api.model('User', {
    'email' : fields.String('Your e-mail.'),
    'password' : fields.String('Password.')
})

resetpassword_format = api.model('Email', {
    'email' : fields.String('Email')
})

category_format = api.model('Category', {
    'name' : fields.String('Category name')
})

recipe_format = api.model('Recipe', {
    'title' : fields.String('Recipe title'),
    'ingredient1' : fields.String('ingredient'),
    'ingredient2' : fields.String('ingredient'),
    'ingredient3' : fields.String('ingredient'),
    'directions' : fields.String('Directions to cook the recipe')
})
new_password_format = api.model('New_password', {
    'token' : fields.String('Token for resetting password'),
    'new_password' : fields.String('Your new password')
})

pagination_args = reqparse.RequestParser(bundle_errors=True)
pagination_args.add_argument(
    'q', type=str, help='Search parameter', location='query')

pagination_args.add_argument(
    'limit', type=int, help='Results per page', location='query')

pagination_args.add_argument(
    'page', type=int, help='Number of page', location='query')

# Namespaces
auth_ns = api.namespace('auth', description='Authentication operations')
category_ns = api.namespace('categories', description='Category operations')
recipe_ns = api.namespace('recipes', description='Recipe operations')

def token_required(f):
    def wrapper(*args, **kwargs):
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            abort(401, 'Please provide token to access this resource.')
        elif auth_header.startswith("Bearer "):
            access_token = auth_header.split(" ")[1]
        else:
            abort(400, "Make sure you have the word 'Bearer' before the token: 'Bearer TOKEN'")

        if access_token:
            if current_user.is_anonymous:
                abort(401, 'Please login to get a valid token.')
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if isinstance(user_id, str):
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                abort(401, response)

            return f(*args, user_id=user_id, **kwargs)

    return wrapper


def validation(string, email=False, password=False):
    string = string.lstrip()

    if email:
        email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
        return email_regex.match(string)

    elif password:
        # At least 8 characters, may contain letters, numbers or special characters(@#$%^&+=)
        password_regex = re.compile(r'[A-Za-z0-9@#$%^&+=]{8,}')
        return password_regex.match(string)

    else:
        text_regex = re.compile(r'^[A-Za-z1-9 ]+$')
        return text_regex.match(string)

def validate_data(data, *args):
    for key, value in data.items():
        if not isinstance(value, str):
            abort(422, 'The {} you provided is not in string format. PLease make sure you entered your {} in quotes.'.format(key, key))

        if key == 'email':
            response = validation(value, email=True)

        elif 'password' in key:
            response = validation(value, password=True)
            if not response:
                abort(422, 'The password you provided MUST be atleast 8 characters long.')

        else:
            response = validation(value)

        if not response:
            abort(422, 'The {} you provided contains nothing or an invalid character'.format(key))

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

@auth_ns.route('/register')
class Register(Resource):
    @api.expect(user_registration_format)
    def post(self):
        data = api.payload

        # Validate the input provided by the user
        validate_data(data)

        try:
            # create user and add him/her to the db
            user = User(email = data['email'],
                        username = data['username'],
                        first_name = data['first_name'],
                        last_name = data['last_name'],
                        password = data['password'])

            db.session.add(user)
            db.session.commit()

        except IntegrityError as e:
            db.session.rollback()
            if ('username' in str(e.orig)):
                abort(409, "The username has already been taken, please choose another username.")
            else:
                abort(409, "The email that you entered has already been registered with this website.")

        return {'message' : 'user created successfully'}, 201


@auth_ns.route('/login')
class Login(Resource):
    @api.expect(user_basic_format)
    def post(self):
        data = api.payload

        # Validate data
        validate_data(data)

        user = User.query.filter_by(email=data['email']).first()

        if user is not None and user.verify_password(data['password']):

            login_user(user)

            token = user.generate_token(user.id)
            user.token = token
            db.session.commit()

            response = {
                'message': 'You logged in successfully.',
                'access_token': token.decode()
            }
            return response

        abort(401, 'Invalid email or password, Please try again')


@auth_ns.route('/logout')
class Logout(Resource):
    def get(self):
        current_user.token = ""
        db.session.commit()
        logout_user()

        return {'message' : 'You have successfully logged out.'}

@auth_ns.route('/set-new-password', methods=['POST'])
class set_new_password(Resource):
    @api.expect(new_password_format)
    def post(self):
            data = api.payload

            if not data['new_password']:
                abort(400, 'You should provide your new password')
            if not data['token']:
                abort(400, 'You should provide the token')

            user_id = User.decode_token(data['token'])
            if isinstance(user_id, str):
                # user is not legit, so the payload is an error message
                abort(401, 'Invalid token. Please provide your email to reset-password.')

            user = User.query.filter_by(id=user_id).first()
            user.password = data['new_password']
            db.session.commit()

            return {'message' : 'Your new password has been set!'}

@auth_ns.route('/reset-password', methods=['POST'])
class ResetPassword(Resource):
    @api.expect(resetpassword_format)
    def post(self):
        data = api.payload

        if not data['email']:
            abort(400, 'You should provide your email.')

        # Validate data
        validate_data(data)

        user = User.query.filter_by(email=data['email']).first()
        if not user:
            return {'message' : 'user not found.'}, 404

        token = user.generate_token(user.id)

        # return {"password_reset_token" : token.decode()}

        send_email("Reset Password",
            data['email'],
            [user.email],
            render_template("resetpassword_email.txt", token=token.decode()),
            render_template("resetpassword_email.html", token=token.decode()))

        return {'message' : 'Instructions sent to your inbox.'}

@category_ns.route('/category')
class CategoriesAddOrGet(Resource):
    @api.doc(security='apikey')
    @api.expect(category_format)
    @token_required
    def post(self, **kwargs):
        user_id = kwargs.get('user_id')

        # Go ahead and handle the request, the user is authenticated
        data = request.get_json()

        # Validate data
        validate_data(data)

        if data['name']:
            category_name = data['name'].title()
            try:
                category = Category(name = category_name, user_id = user_id)

                db.session.add(category)
                db.session.commit()

            except IntegrityError:
                db.session.rollback()
                abort(409, "The category name that you entered already exists.")

            response = {'id' : category.id,
                    'category_name' : category.name,
                    'created_by' : current_user.first_name
                }

            return response, 201

    @api.doc(security='apikey')
    @api.expect(pagination_args)
    @token_required
    def get(self, **kwargs):
        user_id = kwargs.get('user_id')

        # set the limit if it has been provided by the user
        lim = request.args.get('limit', None)
        # set the page if the user provided, else default to one
        page = request.args.get('page', 1)
        # set the name if user provided the search query
        name = request.args.get('q', None)

        if name and lim:
            try:
                categories = Category.query.filter_by(user_id=user_id).search(name).paginate(int(page), int(lim), False).items
            except ValueError:
                abort(422, "Please make sure you provided a number for limit/page parameter.")
        elif name:
            categories = Category.query.filter_by(user_id=user_id).search(name).all()
        elif lim:
            try:
                categories = Category.query.filter_by(user_id=user_id).paginate(int(page), int(lim), False).items
            except ValueError:
                abort(422, "Please make sure you provided a whole number for limit/page parameter.")
        else:
            categories = Category.query.filter_by(user_id=user_id).all()

        if name and not categories:
            return {'message' : 'Not found'}, 404
        elif not categories:
            return {'message' : 'No categories here.'}, 404

        output = []

        for category in categories:
            category_data = {}
            category_data['id'] = category.id
            category_data['Name'] = category.name
            output.append(category_data)

        return {'categories' : output}


@category_ns.route('/category/<category_id>')
class CategoryFunctions(Resource):
    @api.doc(security='apikey')
    @token_required
    def get(self, category_id, **kwargs):
        user_id = kwargs.get('user_id')
        category = Category.query.filter_by(user_id=user_id).filter_by(id=category_id).first()

        if not category:
            return {'message' : 'No category found'}

        category_data = {}
        category_data['id'] = category.id
        category_data['Name'] = category.name

        return {'category': category_data}

    @api.doc(security='apikey')
    @api.expect(category_format)
    @token_required
    def put(self, category_id, **kwargs):
        user_id = kwargs.get('user_id')

        category = Category.query.filter_by(user_id=user_id).filter_by(id=category_id).first()

        if not category:
            return {'message' : 'category does not exists'}, 404

        data = request.get_json()
        if data['name']:
            try:
                prev_name = category.name
                category.name = data['name']
                db.session.commit()

            except IntegrityError:
                db.session.rollback()
                abort(409, "The category name that you entered already exists.")

            return {'message' : 'Category ' + prev_name + ' changed to ' + category.name}

    @api.doc(security='apikey')
    @token_required
    def delete(self, category_id, **kwargs):
        user_id = kwargs.get('user_id')
        category = Category.query.filter_by(user_id=user_id).filter_by(id=category_id).first()
        category_name = category.name

        if not category:
            return {'message' : 'No category found'}, 404

        db.session.delete(category)
        db.session.commit()

        return {'message' : 'Category ' + category_name + ' deleted successfully'}

@recipe_ns.route('/category/<category_id>/recipe')
class RecipesGetOrAdd(Resource):
    @api.doc(security='apikey')
    @api.expect(pagination_args)
    @token_required
    def get(self, category_id, **kwargs):
        user_id = kwargs.get('user_id')

        category = Category.query.filter_by(user_id=user_id).filter_by(id=category_id).first()

        if not category:
            return {'message' : 'category does not exists'}, 404

        #set the limit if it has been provided by the user
        lim = request.args.get('limit', None)
        #set the offset if the user provided
        page = request.args.get('page', 1)
        # set the title if search query was provided
        title = request.args.get('q', None)

        if title and lim:
            try:
                recipes = Recipe.query.filter_by(category_id=category_id).search(title).paginate(int(page), int(lim), False).items
            except ValueError:
                abort(422, "Please make sure you provided a whole number for limit/page parameter.")
        elif title:
            recipes = Recipe.query.filter_by(category_id=category_id).search(title).all()
        elif lim:
            try:
                recipes = Recipe.query.filter_by(category_id=category_id).paginate(int(page), int(lim), False).items
            except ValueError:
                abort(422, "Please make sure you provided a whole number for limit/page parameter.")
        else:
            recipes = category.category_recipes

        if not recipes:
            return {'message' : 'no recipes found'}, 404

        output = []

        for recipe in recipes:
            recipe_data = {}

            recipe_data['id'] = recipe.id
            recipe_data['title'] = recipe.title

            ing_num = 1
            for ingredient in recipe.recipe_ingredients:
                recipe_data['ingredient{}'.format(ing_num)] = ingredient.ing
                ing_num += 1

            recipe_data['directions'] = recipe.directions

            output.append(recipe_data)

        return {'{} - recipes'.format(category.name) : output}

    @api.doc(security='apikey')
    @api.expect(recipe_format)
    @token_required
    def post(self, category_id, **kwargs):
        user_id = kwargs.get('user_id')

        category = Category.query.filter_by(user_id=user_id).filter_by(id=category_id).first()

        if not category:
            return {'message' : 'category does not exists'}, 404

        data = request.get_json()

        # Validate data
        validate_data(data)

        ingredient = None
        ingredients = []
        ingredient_num = 1
        while 'ingredient{}'.format(ingredient_num) in data:
            ingredient = data['ingredient{}'.format(ingredient_num)]
            ingredients.append(ingredient)

            ingredient_num += 1

        recipe_title = data['title'].title()
        category.add_recipe(recipe_title, ingredients, data['directions'], 'noImage')

        return {'message' : 'recipe added successfully'}, 201

@recipe_ns.route('/category/<category_id>/recipe/<recipe_id>')
class RecipeFunctions(Resource):
    @api.doc(security='apikey')
    @token_required
    def get(self, category_id, recipe_id, **kwargs):
        user_id = kwargs.get('user_id')

        category = Category.query.filter_by(user_id=user_id).filter_by(id=category_id).first()

        if not category:
            return {'message' : 'category does not exists'}

        recipe = Recipe.query.filter_by(category_id=category.id).filter_by(id=recipe_id).first()

        if not recipe:
            return {'message' : 'recipe does not exists'}, 404

        recipe_data = {}

        recipe_data['id'] = recipe.id
        recipe_data['title'] = recipe.title

        ing_num = 1
        for ingredient in recipe.recipe_ingredients:
            recipe_data['ingredient{}'.format(ing_num)] = ingredient.ing
            ing_num += 1

        recipe_data['directions'] = recipe.directions

        return recipe_data

    @api.doc(security='apikey')
    @api.expect(recipe_format)
    @token_required
    def put(self, category_id, recipe_id, **kwargs):
        user_id = kwargs.get('user_id')

        data = request.get_json()

        category = Category.query.filter_by(user_id=user_id).filter_by(id=category_id).first()

        if not category:
            return {'message' : 'category does not exists'},404

        return category.edit_recipe(data, id=recipe_id)

    @api.doc(security='apikey')
    @token_required
    def delete(self, category_id, recipe_id, **kwargs):
        user_id = kwargs.get('user_id')

        category = Category.query.filter_by(user_id=user_id).filter_by(id=category_id).first()

        if not category:
            return {'message' : 'category does not exists'}, 404

        recipe = Recipe.query.filter_by(category_id=category.id).filter_by(id=recipe_id).first()

        if not recipe:
            return {'message' : 'recipe does not exists'}, 404

        db.session.delete(recipe)
        db.session.commit()

        return {'message' : 'Recipe deleted successfully'}
