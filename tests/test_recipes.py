import json

from .test_base import BaseTestCase
from app.models import Recipe, Ingredient

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
            directions = 'Testing the writing of directions for recipe titled {}'.format(title)

        if rec_num == 1:
            recipe_data = {
                'title' : title,
                'ingredient1' : ingredients[0],
                'ingredient2' : ingredients[1],
                'ingredient3' : ingredients[2],
                'directions' : directions
            }
            # Create the recipe using the link in the app through the context given and return the response
            return context.post(self.recipe_url + 'category/{}/recipe'.format(cat_id), headers=dict(Authorization="Bearer " + token), data=json.dumps(recipe_data), content_type='application/json')

        # else if more than one recipes are to be created
        else:
            # Loop through the number of recipes that need to be created
            for i in range(rec_num):
                # set the title by using the title and appending the current number
                title = "{}{}".format(title, i+1)

                #set the directions, if not provided
                if directions == None:
                    directions = 'Testing the writing of directions for recipe titled {}'.format(title)
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
                context.post(self.recipe_url + 'category/{}/recipe'.format(cat_id), headers=dict(Authorization="Bearer " + token), data=json.dumps(recipe_data), content_type='application/json')


    def test_recipe_creation_successfully(self):
        """Test that a recipe can be created successfully,
        It gets a token and then creates 5 categories,
        it creates a recipe and then checks if the recipe exists"""

        token_and_context = self.get_token()
        token = token_and_context['token']
        context = token_and_context['context']

        self.create_category(token=token, context=context, cat_num=5)

        response = self.create_recipe(token, context)
        self.assertEquals(response.status_code, 201)

        # check if the recipe exists in the db
        recipe = Recipe.query.filter_by(category_id=1).filter_by(title='Recipe Create Test').first()
        assert recipe

    def test_get_all_recipes_successfully(self):
        """Test all recipes can be fetched"""
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
        response = context.get(self.recipe_url + 'category/1/recipe', headers=dict(Authorization="Bearer " + token))
        self.assertEquals(response.status_code, 200)

        # Extract recipes from the response and check their number
        recipes = json.loads(response.data)['Category1 - recipes']
        self.assertEqual(len(recipes), 5)

    def test_get_limited_recipes_successfully(self):
        """Test GET method on recipes with lim parameter"""
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
        response = context.get(self.recipe_url + 'category/1/recipe?limit=3', headers=dict(Authorization="Bearer " + token))
        self.assertEquals(response.status_code, 200)

        # Extract recipes from the response and check their number
        recipes = json.loads(response.data)['Category1 - recipes']
        self.assertEqual(len(recipes), 3)

    def test_get_limited_recipes_on_a_specific_page(self):
        """Test getting limited recipes starting off with a specific recipe"""
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
        response = context.get(self.recipe_url + 'category/1/recipe?limit=1&page=3', headers=dict(Authorization="Bearer " + token))
        self.assertEquals(response.status_code, 200)

        # Extract recipes from the response and:
        # check number of recipes, it should be 1
        # check that the id of recipe is 3
        recipes = json.loads(response.data)['Category1 - recipes']
        self.assertEqual(len(recipes), 1)
        self.assertEquals(recipes[0]['id'], 3)

    def test_search_recipes_using_recipe_title_successfully(self):
        """Test that the API can search through the recipes by recipe title,
        when given 'q' parameter"""
        # get the token and context
        token_and_context = self.get_token()
        token = token_and_context['token']
        context = token_and_context['context']

        # Create 5 categories using create_category method, named category1 to category5
        self.create_category(token=token, context=context, cat_num=5)

        # create 5 recipes in category id 1;
        # the helper function creates recipes in category id 1, if the arg is not provided
        self.create_recipe(token, context, title='Title to be searched')

        # call the link to get the response
        response = context.get(self.recipe_url + 'category/1/recipe?q=Title to be searched', headers=dict(Authorization="Bearer " + token))
        self.assertEquals(response.status_code, 200)

        # Extract recipes from the response and:
        # check that the id of recipe is 4
        recipes = json.loads(response.data)['Category1 - recipes']
        self.assertEquals(recipes[0]['title'], 'Title To Be Searched')

    def test_get_one_recipe_successfully(self):
        """Test that the API can get one recipe,
        when provided with recipe id"""
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
        response = context.get(self.recipe_url + 'category/1/recipe/3', headers=dict(Authorization="Bearer " + token))
        self.assertEquals(response.status_code, 200)

        # Extract recipes from the response and:
        # check that the id of recipe is 3
        recipes = json.loads(response.data)
        self.assertEquals(recipes['id'], 3)

    def test_editing_a_recipe_successfully(self):
        """Test editing a recipe"""
        # get the token and context
        token_and_context = self.get_token()
        token = token_and_context['token']
        context = token_and_context['context']

        # Create 5 categories using create_category method, named category1 to category5
        self.create_category(token=token, context=context, cat_num=5)

        # create 5 recipes in category id 1;
        # the helper function creates recipes in category id 1, if the arg is not provided
        self.create_recipe(token, context, rec_num=5)

        # call the link to make the change and get the response
        new_title = 'title changed'
        new_ingredient = 'ingredient2 changed'
        new_directions = 'directions changed'
        form = {
            'title' : new_title,
            'ingredient1' : new_ingredient,
            'directions' : new_directions
            }
        response = context.put(self.recipe_url + 'category/1/recipe/3', headers=dict(Authorization="Bearer " + token), data=json.dumps(form), content_type='application/json')
        self.assertEquals(response.status_code, 200)

        # get the third recipe and its ingredient and check its contents
        recipe = Recipe.query.filter_by(category_id=1).filter_by(id=3).first()
        ingredient = Ingredient.query.filter_by(recipe_id=3).filter_by(id=7).first()

        self.assertEquals(recipe.title, new_title)
        self.assertEquals(ingredient.ing, new_ingredient)
        self.assertEquals(recipe.directions, new_directions)

    def test_deleting_a_recipe_successfully(self):
        """Test deleting a recipe"""
        # get the token and context
        token_and_context = self.get_token()
        token = token_and_context['token']
        context = token_and_context['context']

        # Create 5 categories using create_category method, named category1 to category5
        self.create_category(token=token, context=context, cat_num=5)

        # create 5 recipes in category id 1;
        # the helper function creates recipes in category id 1, if the arg is not provided
        self.create_recipe(token, context, rec_num=5)

        # call the link to delete the recipe
        response = context.delete(self.recipe_url + 'category/1/recipe/3', headers=dict(Authorization="Bearer " + token))
        self.assertEquals(response.status_code, 200)

        # get the third recipe and its ingredient and check its contents
        recipe = Recipe.query.filter_by(category_id=1).filter_by(id=3).first()

        self.assertFalse(recipe)
