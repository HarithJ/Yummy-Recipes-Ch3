import os
from flask import render_template, redirect, url_for, request, session, g, abort, flash
from werkzeug.utils import secure_filename


from app import category_required, validate_input
from . import recipes
from ..models import Globals
from config import Config

@recipes.route('/recipes', methods=['GET'])
@category_required
def recipes_page():
    return render_template("profile.html", recipes=Globals.current_category.recipes, user_name=Globals.current_user.name)


@recipes.route('/addrecipe/', methods=['POST'])
@category_required
def add_recipe():
    ingredient = None
    ingredients = []
    ingredient_num = 1
    while 'ingredient{}'.format(ingredient_num) in request.form:
        ingredient = request.form['ingredient{}'.format(ingredient_num)]
        if validate_input(ingredient):
            break
        ingredients.append(ingredient)
        ingredient_num += 1

    #: check if the recipe title is blank
    if request.form['recipetitle'] == "":
        flash("Recipe title cannot be blank!")
        return redirect(url_for('recipes.recipes_page', category_name=Globals.current_category.category_name))

    #: upload image, if given
    file = request.files['recipe_image']
    filename = secure_filename(file.filename)

    if filename != "":
        file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
    else:
        filename = "noImage"

    Globals.current_category.add_recipe(request.form['recipetitle'], ingredients, request.form['directions'], filename)
    return redirect(url_for('recipes.recipes_page', category_name=Globals.current_category.category_name))

@recipes.route('/editrecipe/<string:prev_title>', methods=['POST'])
@category_required
def edit_recipe(prev_title):
    ingredient = None
    ingredients = []
    ingredient_num = 1
    while 'ingredient{}'.format(ingredient_num) in request.form:
        ingredient = request.form['ingredient{}'.format(ingredient_num)]
        ingredients.append(ingredient)
        ingredient_num += 1

    file = request.files['recipe_image']
    filename = secure_filename(file.filename)

    if filename != "":
        os.remove(os.path.join(Config.UPLOAD_FOLDER, Globals.current_category.recipes[prev_title].image_name))
        file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
    else:
        filename = secure_filename(request.form['hidden_recipe_image'])

    Globals.current_category.edit_recipe(prev_title, request.form['recipetitle'], ingredients, request.form['directions'], filename)
    return redirect(url_for('recipes.recipes_page', category_name=Globals.current_category.category_name))

@recipes.route('/deleterecipe/<string:recipe_title>')
@category_required
def delete_recipe(recipe_title):
    if Globals.current_category.recipes[recipe_title].image_name != 'noImage':
        os.remove(os.path.join(Config.UPLOAD_FOLDER, Globals.current_category.recipes[recipe_title].image_name))
    Globals.current_category.delete_recipe(recipe_title)
    return redirect(url_for('recipes.recipes_page', category_name=Globals.current_category.category_name))