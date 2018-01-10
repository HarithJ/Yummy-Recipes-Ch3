import json

from test_base import BaseTestCase
from app.models import Recipe

class RecipeTestCase(BaseTestCase):
    """This class represents the testing for recipes"""

    def create_recipe(self, token, context, cat_id=1, title="Recipe Create Test", ingredients=None, directions=None, rec_num=1):
        """This helper method helps to create a recipe
        It takes in 2 required parameters:
            1. token
            2. context
        and it takes in 5 optional parameters:
            1. the category id in which the recipe will be created, default is set to 1
            2. title of the recipe, default=Recipe Create Test
            3. list of ingredients for the recipe
            4. directions for cooking the recipe
            5. the number of recipes to be created

        It creates five categories which will be used to store recipes.
        If just one recipe is created, then return the response given by creating that recipe.
        else return nothing
        """

        # Set the ingredients and directions for the recipe if not provided
        if ingredients == None:
            ingredients = []
            for i in range(3):
                ingredients.append('ingredient{}'.format(i+1))

        if directions == None:
            directions = 'Testing the writing of directions for recipe titled "{}"'.format(title)

        if rec_num == 1:
            recipe_data = {
                'title' : title,
                'ingredient1' : ingredients[0],
                'ingredient2' : ingredients[1],
                'ingredient3' : ingredients[2],
                'directions' : directions
            }
            # Create the recipe using the link in the app through the context given and return the response
            return context.post('/api/v1.0/category/{}/recipe'.format(cat_id), headers=dict(Authorization="Bearer " + token), data=json.dumps(recipe_data), content_type='application/json')

        # else if more than one recipes are to be created
        else:
            # Loop through the number of recipes that need to be created
            for i in range(rec_num):
                # set the title by using the title and appending the current number
                title = "{}{}".format(title, i+1)

                #set the directions, if not provided
                if directions == None:
                    directions = 'Testing the writing of directions for recipe titled "{}"'.format(title)
                #else if the directions are provided just append the title of current recipe
                else:
                    directions = "{} {}".format(directions, title)


                #create recipe data
                recipe_data = {
                    'title' : title,
                    'ingredient1' : ingredients[0],
                    'ingredient2' : ingredients[1],
                    'ingredient3' : ingredients[2],
                    'directions' : directions
                }

                # create the recipe using the link in the app
                context.post('/api/v1.0/category/{}/recipe'.format(cat_id), headers=dict(Authorization="Bearer " + token), data=json.dumps(recipe_data), content_type='application/json')


    def test_recipe_creation(self):
        """Test that the API can create a recipe"""
        # get the token and context
        token_and_context = self.get_token()
        token = token_and_context['token']
        context = token_and_context['context']

        # Create 5 categories using create_category method, named category1 to category5
        self.create_category(token=token, context=context, cat_num=5)

        # create a recipe titled 'Recipe Create Test' in category id 1;
        # the title is set by the helper function 'create_recipe',
        # the helper function creates recipes in category id 1, if the arg is not provided
        response = self.create_recipe(token, context)
        self.assertEquals(response.status_code, 201)

        # check if the recipe exists in the db
        recipe = Recipe.query.filter_by(category_id=1).filter_by(title='Recipe Create Test').first()
        assert recipe

    def test_get_all_recipes(self):
        """Test that the Api can get all the recipes"""
        # get the token and context
        token_and_context = self.get_token()
        token = token_and_context['token']
        context = token_and_context['context']

        # Create 5 categories using create_category method, named category1 to category5
        self.create_category(token=token, context=context, cat_num=5)

        # create 5 recipes in category id 1;
        # the helper function creates recipes in category id 1, if the arg is not provided
        self.create_recipe(token, context, rec_num=5)

        # call the link to get the response
        response = context.get('/api/v1.0/category/1/recipe', headers=dict(Authorization="Bearer " + token))
        self.assertEquals(response.status_code, 200)

        # Extract recipes from the response
        recipes = json.loads(response.data)['recipes']
        self.assertEqual(len(recipes), 5)