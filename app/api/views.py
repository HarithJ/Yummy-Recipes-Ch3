from flask import Flask, jsonify, make_response, render_template, request
from functools import wraps

from . import api
from .. import db
from ..models import User, Ingredient, Recipe

def token_required(f):
    @wraps(f)

    def decorated (*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing'}), 401


        data = jwt.decode(token, 'asd')
        api_current_user = User.query.get(data['id'])
        #login_user(current_user)

        if api_current_user is None:
            return jsonify({
                'message': 'Token is invalid!',
                'data': data,
                'current': api_current_user.email
            }), 401


        return f(api_current_user, *args, **kwargs)

    return decorated

def turn_recipe_in_obj(recipe):
    #store ingredients
    ingredients = ''
    for i in recipe.recipe_ingredients:
        ingredients += i.ing + ','

    # creat an object of recipe
    obj = {
        "id": recipe.id,
        "title": recipe.title,
        "ingredients": ingredients,
        "directions": recipe.directions
    }
    return obj

@api.route('/api/v1.0/recipes', methods=['GET'])
@token_required
def get_recipes(current_user):
    recipes = Recipe.query.all()

    #return render_template("test.html", recipes=recipes)
    results = []
    for recipe in recipes:

        obj = turn_recipe_in_obj(recipe)
        #Append that object in results
        results.append(obj)

    return jsonify(results)

@api.route('/api/v1.0/recipes/<recipe_name>', methods=['GET'])
def get_one_recipe(recipe_name):
    recipe = Recipe.query.filter_by(title=recipe_name).first()

    if not recipe:
        return jsonify({'message': 'No recipe found!'})

    recipe_obj = turn_recipe_in_obj(recipe)

    return jsonify(recipe_obj)
