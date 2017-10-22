import os
import unittest
#import webapp
from webapp.app import *

class appTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def register(self, name, email, password, details):
        return self.app.post('/register/', data=dict(
            name = name,
            email = email,
            password = password,
            verpassword = password,
            details = details
            ), follow_redirects=True)

    def login(self, name, password):
        return self.app.post('/validate/', data=dict(
            name = name,
            password = password
            ), follow_redirects=True)


    # Ensure the Homepage loads correctly
    def test_index(self):
        response = self.app.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Ensure there is text on home page saying 'Login' (Because its a registration page, and has a link to a login page)
    def test_index_text(self):
        response = self.app.get('/', content_type='html/text')
        self.assertTrue(b'Login' in response.data)

    # Ensure that the user registration behaves correctly
    def test_registration(self):
        response = self.register('admin', 'admin@gmail.com', 'default', 'A user for testing purposes')
        self.assertIn(b'Sign in!!!', response.data)

    # Ensure the app behaves correctly given the correct credentials
    def test_login_crct_credentials(self):
        self.register('admin', 'admin@gmail.com', 'default', 'A user for testing purposes')
        response = self.login('admin', 'default')
        self.assertIn (b'Welcome admin', response.data)
'''
    #Ensure that users can add in new recipes
    def test_add_recipe(self):
        #self.register('admin', 'admin@gmail.com', 'default', 'A user for testing purposes')
        #self.login('admin', 'default')
        response = self.app.post('/addrecipe/', data=dict(
            recipetitle = 'Fish Masala',
            ingredient1 = '1/2 cup light corn syrup',
            directions = 'To make the dough, place the flours, salt, sugar and yeast into a large bowl and stir. Make a well in the centre of the flour and pour in the water, gradually mixing in the flour to form a soft dough.'
            ), follow_redirects=True)
        self.assertIn(b'Fish Masala', response.data)'''

if __name__ == '__main__':
    unittest.main()