import unittest

from io import BytesIO
from flask import url_for
from flask_testing import TestCase

from app import create_app
from app.models import User, Category, Globals

class TestBase(TestCase):

    def create_app(self):

        config_name = 'testing'
        app = create_app(config_name)

        return app

    def setUp(self):
        """
        Will be called before every test
        """
        #: create a test user
        Globals.users['Harith'] = User('Harith', 'harithjaved@gmail.com', 'abc123', "I am a Tester")


    def tearDown(self):
        """
        Will be called after every test
        """
        Globals.current_user = None
        Globals.users = {}

class authentication(TestBase):
    """
    Tests for registration and login when provided appropriate credentials,
    and also when provided incorrect credentials
    """
    def test_validation_incorrect_credentials(self):
        """
        Test that when login form is provided with incorrect credentials,
        it redirects to login page with a flash msg
        """
        response = self.client.post(url_for('auth.validate'), data=dict(
            name = 'incorrect',
            password = 'incorrect'
            ), follow_redirects=True)

        self.assertIn(b'Incorrect Credentials Entered', response.data)

    def test_validation_correct_credentials(self):
        """
        Test that when login form is provided with correct credentials,
        it redirects to profile page
        """
        response = self.client.post(url_for('auth.validate'), data=dict(
            name = 'Harith',
            password = 'abc123'
            ))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, url_for('categories.profile'))

    def test_registration(self):
        """
        Test that a user can register successfully
        """
        response = self.client.post(url_for('auth.register'), data=dict(
            name = 'regTest',
            email = 'reg@test.com',
            password = 'testing',
            verpassword = 'testing',
            details = 'testing'
            ), follow_redirects=True)

        self.assertIn('regTest', Globals.users)

class TestFunctionality(TestBase):

    def setUp(self):
        """
        Will be called before every test
        """
        #: create a test user
        Globals.users['Harith'] = User('Harith', 'harithjaved@gmail.com', 'abc123', "I am a Tester")

        Globals.current_user = Globals.users['Harith']

    def test_add_category(self):
        """
        Test that a user can successfully add in a category
        """
        response = self.client.post(url_for('categories.add_category'), data=dict(
            category_name = 'Yummy Recipes'
            ), follow_redirects=True)

        self.assertIn('Yummy Recipes', Globals.current_user.categories)

    def test_add_recipe(self):
        """
        Test that a user can successfully add a recipe
        """
        response = self.client.post(url_for('categories.add_category'), data=dict(
            category_name = 'Yummy Recipes'
            ), follow_redirects=True)


        Globals.current_category = Globals.current_user.return_category('Yummy Recipes')

        response = self.client.post(url_for('recipes.add_recipe'), content_type='multipart/form-data', data=dict(
            recipetitle = 'Ugali',
            ingredient1 = 'Maize Flour',
            ingredient2 = 'Water',
            directions = 'Heat water, pour in maize flour, stir well.',
            recipe_image = (BytesIO(b''), '')
            ), follow_redirects=True)

        recipe = Globals.current_category.recipes['Ugali']

        self.assertIn('Ugali', Globals.current_category.recipes)

        self.assertEqual('Ugali', recipe.title)
        self.assertIn('Maize Flour', recipe.ingredients)
        self.assertIn('Water', recipe.ingredients)
        self.assertEqual('Heat water, pour in maize flour, stir well.', recipe.directions)
        self.assertEqual('noImage', recipe.image_name)


class TestCategories(TestBase):
    def setUp(self):
        """
        Will be called before every test
        """
        #: create a test user
        Globals.users['Harith'] = User('Harith', 'harithjaved@gmail.com', 'abc123', "I am a Tester")

        #: login the user
        Globals.current_user = Globals.users['Harith']

        #: create Category
        Globals.current_user.add_category('Yummy Recipes')

    def test_edit_category(self):
        """
        Test that a user can edit a category
        """
        response = self.client.post(url_for('categories.edit_category_name', prev_name='Yummy Recipes'), data=dict(
            category_name = 'Name Edited'
            ))

        self.assertIn('Name Edited', Globals.current_user.categories)
        self.assertNotIn('Yummy Recipes', Globals.current_user.categories)

    def test_delete_category(self):
        """
        Test that a user can delete a category
        """
        self.assertIn('Yummy Recipes', Globals.current_user.categories)

        reponse = self.client.get(url_for('categories.delete_category', category_name='Yummy Recipes'))

        self.assertNotIn('Yummy Recipes', Globals.current_user.categories)

class TestRecipes(TestBase):
    def setUp(self):
        """
        Will be called before every test
        """
        #: create a test user
        Globals.users['Harith'] = User('Harith', 'harithjaved@gmail.com', 'abc123', "I am a Tester")

        #: login the user
        Globals.current_user = Globals.users['Harith']

        #: create Category
        Globals.current_user.add_category('Yummy Recipes')

        #: set current category, where recipes will be created
        Globals.current_category = Globals.current_user.return_category('Yummy Recipes')

        #: create a default recipe
        Globals.current_category.add_recipe('Ugali', ['Maize Flour', 'Water'], 'Heat water, pour in maize flour, stir well.', 'noImage')

    def test_edit_recipe(self):
        """
        Test that a user can edit a recipe
        """
        response = self.client.post(url_for('recipes.edit_recipe', prev_title='Ugali'), data=dict(
            recipetitle = 'Edited',
            ingredient1 = 'Edited Ing1',
            ingredient2 = 'Edited Ing2',
            directions = 'Edited directions',
            recipe_image = (BytesIO(b''), ''),
            hidden_recipe_image = 'noImage'
            ), follow_redirects=True)

        recipe = Globals.current_category.recipes['Edited']


        self.assertEqual('Edited', recipe.title)
        self.assertIn('Edited Ing1', recipe.ingredients)
        self.assertIn('Edited Ing2', recipe.ingredients)
        self.assertEqual('Edited directions', recipe.directions)
        self.assertEqual('noImage', recipe.image_name)

        self.assertIn('Edited', Globals.current_category.recipes)
        self.assertNotIn('Ugali', Globals.current_category.recipes)

    def test_delete_recipe(self):
        """
        Test that a user can successfully delete a recipe
        """
        self.assertIn('Ugali', Globals.current_category.recipes)

        response = self.client.get(url_for('recipes.delete_recipe', recipe_title='Ugali'), follow_redirects=True)

        self.assertNotIn('Ugali', Globals.current_category.recipes)


class TestViews(TestBase):

    def test_index_view(self):
        """
        Test that registration page is accessible without login
        """
        response = self.client.get(url_for('auth.index'))
        self.assertEqual(response.status_code, 200)

    def test_login_view(self):
        """
        Test that login page is accessible without login
        """
        response = self.client.get(url_for('auth.login_page'))
        self.assertEqual(response.status_code, 200)


    def test_profile(self):
        """
        Test that user profile is inaccessible without login
        and redirects to login page
        """
        target_url = url_for('categories.profile')
        redirect_url = url_for('auth.login_page')

        response = self.client.get(target_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_categories_page(self):
        """
        Test that categories page is inaccessible without login
        and redirects to login page
        """
        target_url = url_for('categories.categories_page')
        redirect_url = url_for('auth.login_page')

        response = self.client.get(target_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_recipes_page(self):
        """
        Test that recipes page is inaccessible without login
        and redirects to login page
        """
        target_url = url_for('recipes.recipes_page')
        redirect_url = url_for('auth.login_page')

        response = self.client.get(target_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

if __name__ == '__main__':
    unittest.main()