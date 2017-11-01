import os
import unittest

from flask_testing import TestCase
from flask import abort, url_for

from app import create_app, db
from app.models import User, Recipe, Ingredient

class TestBase(TestCase):
    def create_app(self):

        # pass in test configurations
        config_name = 'testing'
        app = create_app(config_name)
        app.config.update(
            SQLALCHEMY_DATABASE_URI = 'postgresql://testuser:abc123@localhost:5432/testdb'
        )
        return app


    def setUp(self):
        """
        Will be called before every test
        """

        db.create_all() #create all tables

        # create test user
        admin = User(email="admin@admin.com", username="admin", first_name="admin", last_name="admin", password="default")

        # save users to database
        db.session.add(admin)
        db.session.commit()


    def tearDown(self):
        """
        Will be called after every test
        """
        db.session.remove()
        db.drop_all()



class TestModels(TestBase):
    def test_user_model(self):
        """
        Test number of records in Employee table
        """
        self.assertEqual(User.query.count(), 1)

    def test_recipe_model(self):
        """
        Test number of records in Department table
        """

        # create ingredients for the recipe
        ingredients = ["sukuma wiki", "tomatoes", "kitungu maji"]
        ingredient = ""
        db_ingredients = []
        for i in ingredients:
            ingredient = Ingredient(ing=i)

            db_ingredients.append(ingredient)

            db.session.add(ingredient)

        # create recipe
        recipe = Recipe(title="Sukuma wiki", recipe_ingredients=db_ingredients, directions="Boil sukuma wiki together with kitungu maji and tomatoes")

        # save recipe to database

        db.session.add(recipe)
        db.session.commit()

        self.assertEqual(Recipe.query.count(), 1)



    def test_ingredient_model(self):
        '''
        Test number of ingredients in db
        '''
        # create ingredients for the recipe
        ingredients = ["sukuma wiki", "tomatoes", "kitungu maji"]
        ingredient = ""
        db_ingredients = []
        for i in ingredients:
            ingredient = Ingredient(ing=i)

            db_ingredients.append(ingredient)

            db.session.add(ingredient)

        db.session.commit()

        self.assertEqual(Ingredient.query.count(), 3)



class TestViews(TestBase):

    def test_homepage_view(self):
        """
        Test that homepage is accessible without login
        """
        response = self.client.get(url_for('auth.index'))
        self.assertEqual(response.status_code, 200)

    def test_login_view(self):
        """
        Test that login page is accessible without login
        """
        response = self.client.get(url_for('auth.login_page'))
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        """
        Test that logout link is inaccessible without login
        and redirects to login page then to logout
        """
        target_url = url_for('auth.logout')
        redirect_url = url_for('auth.login_page', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_profile_view(self):
        """
        Test that dashboard is inaccessible without login
        and redirects to login page then to dashboard
        """
        target_url = url_for('auth.profile')
        redirect_url = url_for('auth.login_page', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)



if __name__ == '__main__':
    unittest.main()