from flask import Flask, render_template, redirect, url_for, request, session, g, abort, flash

#config
SECRET_KEY = 'development mode'

app = Flask(__name__, static_folder='../designs/UI', template_folder='../designs/UI')
app.config.from_object(__name__)

class Recipe:
    def __init__(self, title, ingredients, directions):
        self.title = title
        self.ingredients = ingredients
        self.directions = directions

class User:
    def __init__(self, name, email, password, details):
        self.name = name
        self.email = email
        self.password = password
        self.details = details
        self.recipes = {}

    def is_valid(self, password):
        return self.password == password

    def add_recipe(self, title, ingredients, directions):
        self.recipes[title] = Recipe(title, ingredients, directions)

    def edit_recipe(self, prev_title, title, ingredients, directions):
        self.recipes[prev_title] = Recipe(title, ingredients, directions)

    def delete_recipe(self, recipe_title):
        self.recipes.pop(recipe_title)

users = {}
current_user = None

@app.route('/')
@app.route('/index.html/')
def index():
    return render_template("index.html")

@app.route('/login.html/')
def login_page():
    return render_template("login.html")

@app.route('/profile.html/')
def profile(ingredients = None):
    global current_user
    if current_user == None:
        return redirect(url_for('login_page'))
    return render_template("profile.html", recipes=current_user.recipes, user_name=current_user.name)

@app.route('/register/', methods=['POST'])
def register():
    global users
    error = None
    # check if the password and ver password are not the same
    if request.form['password'] != request.form['verpassword']:
        error = 'Password does not match the password in verify password field'
        return render_template('index.html', error=error)

    users[request.form['name']] = User(request.form['name'], request.form['email'], request.form['password'], request.form['details'])
    return redirect(url_for('login_page'))

@app.route('/validate/', methods=['POST'])
def validate():
    global users
    global current_user
    error = None
    if request.form['name'] in users:
        if users[request.form['name']].is_valid(request.form['password']):
            current_user = users[request.form['name']]
            return redirect(url_for('profile'))

    flash("Incorrect Credentials Entered")
    return redirect(url_for('login_page'))

@app.route('/addrecipe/', methods=['POST'])
def add_recipe():
    ingredient = None
    ingredients = []
    ingredient_num = 1
    while 'ingredient{}'.format(ingredient_num) in request.form:
        ingredient = request.form['ingredient{}'.format(ingredient_num)]
        ingredients.append(ingredient)
        ingredient_num += 1

    current_user.add_recipe(request.form['recipetitle'], ingredients, request.form['directions'])
    return redirect(url_for('profile'))

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

@app.route('/logout/')
def logout():
    global current_user
    current_user = None
    return redirect(url_for('login_page'))

if __name__== '__main__':
    app.run()
