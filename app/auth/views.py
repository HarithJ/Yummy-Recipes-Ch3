from flask import render_template, redirect, url_for, request, session, g, abort, flash
from flask_login import login_required, login_user, logout_user, current_user

from . import auth
from .. import db
from ..models import User, Ingredient, Recipe


@auth.route('/')
@auth.route('/index.html/')
def index():
    return render_template("index.html")

@auth.route('/login.html/')
def login_page():
    return render_template("login.html")

@auth.route('/profile.html/')
@login_required
def profile(ingredients = None):
    return render_template("profile.html")

@auth.route('/register/', methods=['POST'])
def register():
    global users
    error = None
    # check if the password and ver password are not the same
    if request.form['password'] != request.form['verpassword']:
        error = 'Password does not match the password in verify password field'
        return render_template('index.html', error=error)

    user = User(email = request.form['email'],
                username = request.form['username'],
                first_name = request.form['first_name'],
                last_name = request.form['last_name'],
                password = request.form['password'])

    # add employee to the database
    db.session.add(user)
    db.session.commit()
    flash('You have successfully registered! You may login')

    return redirect(url_for('auth.login_page'))

@auth.route('/validate/', methods=['POST'])
def validate():
    user = User.query.filter_by(email=request.form['email']).first()
    if user is not None and user.verify_password(request.form['password']):
        login_user(user)

        return redirect(url_for('auth.profile'))

    flash("Invalid email or password")
    return redirect(url_for('auth.login_page'))


@auth.route('/addrecipe/', methods=['POST'])
@login_required
def add_recipe():
    ingredient = None
    ingredients = []
    ingredient_num = 1
    while 'ingredient{}'.format(ingredient_num) in request.form:
        ingredient = Ingredient(ing=request.form['ingredient{}'.format(ingredient_num)])
        ingredients.append(ingredient)
        db.session.add(ingredient)
        ingredient_num += 1

    recipe = Recipe(title=request.form['recipetitle'], recipe_ingredients=ingredients, directions=request.form['directions'])

    current_user.user_recipes.append(recipe)


    db.session.add(recipe)
    db.session.commit()

    return redirect(url_for('auth.profile'))

'''
@app.route('/editrecipe/<string:prev_title>', methods=['POST'])
def edit_recipe(prev_title):
    ingredient = None
    ingredients = []
    ingredient_num = 1
    while 'ingredient{}'.format(ingredient_num) in request.form:
        ingredient = request.form['ingredient{}'.format(ingredient_num)]
        ingredients.append(ingredient)
        ingredient_num += 1

    current_user.edit_recipe(prev_title, request.form['recipetitle'], ingredients, request.form['directions'])
    return redirect(url_for('profile'))

@app.route('/deleterecipe/<string:recipe_title>')
def delete_recipe(recipe_title):
    current_user.delete_recipe(recipe_title)
    return redirect(url_for('profile'))
    '''

@auth.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('You have successfully loged out!')
    return redirect(url_for('auth.login_page'))

if __name__== '__main__':
    app.run()
