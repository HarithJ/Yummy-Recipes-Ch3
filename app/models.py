class Category:
    """ A class of categories, which takes category's name as the first argument.
    This class also keeps track of recipes that will be for this particular class.
    The instance of this class will have the ability to do the following:
        1. Add a recipe through add_recipe method which takes the title of the recipe, ingredients, and directions as its argument.
        2. Edit a recipe by using edit_recipe method which takes the previous title, the new title, ingredients, and directions as arguments.
        3. Delete a recipe by using delete_recipe method that takes the recipe's title that needs to be deleted as its argument
        4. Edit current category by changing its name to a new name.
    """

    def __init__(self, category_name):
        self.category_name = category_name
        self.recipes = {}

    def add_recipe(self, title, ingredients, directions, recipe_image):
        self.recipes[title] = Recipe(title, ingredients, directions, recipe_image)

    def edit_recipe(self, prev_title, title, ingredients, directions, recipe_image):
        self.recipes.pop(prev_title)
        self.recipes[title] = Recipe(title, ingredients, directions, recipe_image)

    def delete_recipe(self, recipe_title):
        self.recipes.pop(recipe_title)

    def edit_category(self, category_name):
        self.category_name = category_name


class Recipe:
    """This is a class that will represent a recipe.
    It takes a title for the recipe, it's ingredients and directions as arguments.
    """
    def __init__(self, title, ingredients, directions, image_name):
        self.title = title
        self.ingredients = ingredients
        self.directions = directions
        self.image_name = image_name

class User():
    """This class will represent a user.
    It takes the user's name, his email, his password, and details as arguments.
    It also keeps track of categories of the user, so each user will have his/her own list of categories
    The class has the following methods:
        1. is_valid(password): which takes a password as an argument and returns True is the password provided matches the users password
        2. add_category(category_name): It adds a category, and takes category's name as the argument
        3. delete_category(category_name): It deletes a category whose name is provided as an arg
        4. edit_category(prev_name, new_name): This renames 'prev_category' with a new name provided as the 2nd arg
            (this also calls the edit_category method presented in Category class)
        5. return_category(category_name): It returns an instance of the Class Category, given that category's name
    """
    def __init__(self, name, email, password, details):
        self.name = name
        self.email = email
        self.password = password
        self.details = details
        self.categories = {}

    def is_valid(self, password):
        return self.password == password

    def add_category(self, category_name):
        self.categories[category_name] = Category(category_name)

    def delete_category(self, category_name):
        self.categories.pop(category_name)

    def edit_category(self, prev_name, new_name):

        self.categories[prev_name].edit_category(new_name)
        self.categories[new_name] = self.categories.pop(prev_name)

    def return_category(self, category_name):
        return self.categories[category_name]

class Globals():
    """These are global variables that keep track of:
        1. registered users
        2. the user which is currently logged in
        3. The category which a user is at currently
    """
    users = {}
    current_user = None
    current_category = None