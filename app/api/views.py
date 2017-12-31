from flask import request
from flask_login import login_required, login_user, logout_user, current_user
from flask_restplus import Resource, fields, abort

from . import api
from app import db
from ..models import Category, User, Recipe

user_registration_format = api.model('UserRegistration', {
    'first_name' : fields.String('Your first name.'),
    'last_name' : fields.String('Your last name.'),
    'username' : fields.String('User name.'),
    'email' : fields.String('Your e-mail.'),
    'password' : fields.String('Password.')
})

user_basic_format = api.model('User', {
    'email' : fields.String('Your e-mail.'),
    'password' : fields.String('Password.')
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

@api.route('/register')
class Register(Resource):
    @api.expect(user_registration_format)
    def post(self):
        data = api.payload

        user1 = User.query.filter_by(username=data['username']).first()
        user2 = User.query.filter_by(email=data['email']).first()


        if user1 or user2:
            abort(409, 'User already exists. Please login.')


        user = User(email = data['email'],
                    username = data['username'],
                    first_name = data['first_name'],
                    last_name = data['last_name'],
                    password = data['password'])

        # add user to the database
        db.session.add(user)
        db.session.commit()

        return {'message' : 'user created successfully'}, 201


@api.route('/login')
class Login(Resource):
    @api.expect(user_basic_format)
    def post(self):
        data = api.payload

        user = User.query.filter_by(email=data['email']).first()

        if user is not None and user.verify_password(data['password']):

            login_user(user)

            token = user.generate_token(user.id)

            response = {
                'message': 'You logged in successfully.',
                'access_token': token.decode()
            }
            return response

        abort(401, 'Invalid email or password, Please try again')


@api.route('/logout')
class Logout(Resource):
    @api.expect(user_basic_format)
    def post(self):
        data = api.payload

        if current_user.is_anonymous:
            abort(403, 'You are not logged in.')

        if data['email'] == current_user.email and current_user.verify_password(data['password']):
            logout_user()
            response = {
                'message': 'You have successfully logged out'
            }
            return response

        response = {
            'message': 'Incorrect credentials supplied.'
        }
        return response

@api.route('/reset-password', methods=['POST'])
class ResetPassword(Resource):
    def post(self):
        data = api.payload

        if current_user.is_anonymous:
            response = {
                'message' : 'You are not logged in.'
            }
            return response

        if current_user.verify_password(data['current_password']):
            current_user.reset_password(data['new_password'])
            response = {
                'message' : 'You have successfully changed your password.'
            }
            return response

        response = {
            'message' : 'incorrect old password supplied.'
        }

        return response

@api.route('/category')
class CategoriesAddOrGet(Resource):
    @api.doc(security='apikey')
    @api.expect(category_format)
    def post(self):
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # Go ahead and handle the request, the user is authenticated
                data = request.get_json()
                if data['name']:
                    category = Category(name = data['name'], user_id = user_id)

                    db.session.add(category)
                    db.session.commit()

                    response = {'id' : category.id,
                        'category_name' : category.name,
                        'created_by' : current_user.first_name
                    }

                    return response, 201

            else:
                # user is not legit, so the payload is an error message
                message = user_id
                abort(400, 'message')

    @api.doc(security='apikey')
    def get(self):
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                #set the limit if it has been provided by the user
                lim = request.args.get('limit', None)
                #set the offset if the user provided
                off= request.args.get('offset', 0)

                if lim and off:
                    categories = Category.query.filter_by(user_id=user_id).limit(lim).offset(off).all()
                elif lim:
                    categories = Category.query.filter_by(user_id=user_id).limit(lim).all()
                elif off:
                    categories = Category.query.filter_by(user_id=user_id).offset(off).all()
                else:
                    categories = Category.query.filter_by(user_id=user_id).all()

                name = request.args.get('q', None)

                if name:
                    categories = Category.query.filter_by(user_id=user_id).filter_by(name=name).all()

                if name and not categories:
                    abort(404, 'Not found')

                output = []

                for category in categories:
                    category_data = {}
                    category_data['id'] = category.id
                    category_data['Name'] = category.name
                    output.append(category_data)

                return {'categories' : output}

            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return response


@api.route('/category/<category_id>')
class CategoryFunctions(Resource):
    @api.doc(security='apikey')
    def get(self, category_id):
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):

                category = Category.query.filter_by(user_id=user_id).filter_by(id=category_id).first()

                if not category:
                    return {'message' : 'No category found'}

                category_data = {}
                category_data['id'] = category.id
                category_data['Name'] = category.name

                return {'category': category_data}

            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return response

    @api.doc(security='apikey')
    @api.expect(category_format)
    def put(self, category_id):
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                category = Category.query.filter_by(user_id=user_id).filter_by(id=category_id).first()

                if not category:
                    return {'message' : 'category does not exists'}

                data = request.get_json()
                if data['name']:
                    prev_name = category.name
                    category.name = data['name']
                    db.session.commit()

                    return {'message' : 'Category <' + prev_name + '> changed to <' + category.name + '>'}

            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return response

    @api.doc(security='apikey')
    def delete(self, category_id):
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                category = Category.query.filter_by(user_id=user_id).filter_by(id=category_id).first()
                category_name = category.name

                if not category:
                    return {'message' : 'No category found'}

                db.session.delete(category)
                db.session.commit()

                return {'message' : 'Category ' + category_name + ' deleted successfully'}

            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return response


@api.route('/category/<category_id>/recipe')
class RecipesGetOrAdd(Resource):
    @api.doc(security='apikey')
    def get(self, category_id):
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                category = Category.query.filter_by(user_id=user_id).filter_by(id=category_id).first()

                if not category:
                    return {'message' : 'category does not exists'}

                #set the limit if it has been provided by the user
                lim = request.args.get('limit', None)
                #set the offset if the user provided
                off= request.args.get('offset', 0)

                if lim:
                    recipes = Recipe.query.filter_by(category_id=category_id).limit(lim).offset(off).all()
                else:
                    recipes = category.category_recipes

                title = request.args.get('q', None)

                if title:
                    recipes = Recipe.query.filter_by(category_id=category_id).filter_by(title=title).all()

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

                return {'recipes' : output}

            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return response


    @api.doc(security='apikey')
    @api.expect(recipe_format)
    def post(self, category_id):
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                category = Category.query.filter_by(user_id=user_id).filter_by(id=category_id).first()

                if not category:
                    return {'message' : 'category does not exists'}

                data = request.get_json()

                ingredient = None
                ingredients = []
                ingredient_num = 1
                while 'ingredient{}'.format(ingredient_num) in data:
                    ingredient = data['ingredient{}'.format(ingredient_num)]
                    ingredients.append(ingredient)

                    ingredient_num += 1

                category.add_recipe(data['title'], ingredients, data['directions'], 'noImage')

                return {'message' : 'recipe added successfully'}


            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return response


@api.route('/category/<category_id>/recipe/<recipe_id>')
class RecipeFunctions(Resource):
    @api.doc(security='apikey')
    def get(self, category_id, recipe_id):
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                category = Category.query.filter_by(user_id=user_id).filter_by(id=category_id).first()

                if not category:
                    return {'message' : 'category does not exists'}

                recipe = Recipe.query.filter_by(category_id=category.id).filter_by(id=recipe_id).first()

                if not recipe:
                    return {'message' : 'recipe does not exists'}

                recipe_data = {}

                recipe_data['id'] = recipe.id
                recipe_data['title'] = recipe.title

                ing_num = 1
                for ingredient in recipe.recipe_ingredients:
                    recipe_data['ingredient{}'.format(ing_num)] = ingredient.ing
                    ing_num += 1

                recipe_data['directions'] = recipe.directions

                return recipe_data

        else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return response

    @api.doc(security='apikey')
    @api.expect(recipe_format)
    def put(self, category_id, recipe_id):
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                data = request.get_json()

                category = Category.query.filter_by(user_id=user_id).filter_by(id=category_id).first()

                if not category:
                    return {'message' : 'category does not exists'}

                category.edit_recipe(data, id=recipe_id)

                return {'message' : 'Edited successfully'}

            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return response

    @api.doc(security='apikey')
    def delete(self, category_id, recipe_id):
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                category = Category.query.filter_by(user_id=user_id).filter_by(id=category_id).first()

                if not category:
                    return {'message' : 'category does not exists'}

                recipe = Recipe.query.filter_by(category_id=category.id).filter_by(id=recipe_id).first()

                if not recipe:
                    return {'message' : 'recipe does not exists'}

                db.session.delete(recipe)
                db.session.commit()

                return {'message' : 'Recipe deleted successfully'}

            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return response
