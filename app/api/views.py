from flask import Flask, jsonify, make_response, render_template

from . import api
from .. import db
from ..models import User, Ingredient, Recipe

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
def get_recipes():
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
