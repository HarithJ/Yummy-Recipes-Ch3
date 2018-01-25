import unittest
import json

from app import create_app, db
from app.models import Category

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        """setup test variables"""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client

        # binds the app with the current context
        ctx = self.app.app_context()
        ctx.push()
        #create all tables
        db.session.close()
        db.drop_all()
        db.create_all()

    def register_user(self, first_name='Tester', last_name='Api', username='apitester', email='tester@api.com', password='abc'):
        """This helper method helps register a test user"""
        user_data = {
            'first_name' : first_name,
            'last_name' : last_name,
            'username' : username,
            'email' : email,
            'password' : password
        }

        return self.client().post('/api/v1.0/register', data=json.dumps(user_data), content_type='application/json')

    def login_user(self, email='tester@api.com', password='abc'):
        """This helper method helps log in a test user in a specific context.
        It returns a dictionary that consists of the login result and the context it self.
        """
        user_data = {
            'email' : email,
            'password' : password
        }

        with self.client() as c:
            return {
                'login_response' : c.post('/api/v1.0/login', data=json.dumps(user_data), content_type='application/json'),
                'context' : c
                }

    def get_token(self):
        """
        This helper method helps to register a test user, log him in
        and return back a dictionary that contains a token and the context.
        """
        self.register_user()

        #get the results from login_user method
        login_dict = self.login_user()
        login_response = login_dict['login_response']
        context = login_dict['context']

        #get the token from the response data of login and pass it
        token = json.loads(login_response.data)
        return {'token' : token['access_token'], 'context' : context}

    def create_category(self, token, context, name="Yummy", cat_num=1):
        """This helper method creates a category.
        It takes in four parameters:
            1. name of the category, default=Yummy
            2. the access token which the user gets after he has logged in
            3. the context in which the app will run
            4. the number of categories to be created
        If just one category is created, then return the response given by creating that category.
        else return nothing
        """
        if cat_num == 1:
            category_data = {'name' : name}

            # Create a category by going to that link in the app using the context given
            return context.post('/api/v1.0/category', headers=dict(Authorization="Bearer " + token), data=json.dumps(category_data), content_type='application/json')
        else:
            # Create cat_num of categories using create_category method, named category1 to category{i}
            i = 1
            name = 'category{}'.format(i)
            while(i <= cat_num):
                category_create_response = self.create_category(token=token, context=context, name=name)
                self.assertEquals(category_create_response.status_code, 201)
                i += 1
                name = 'category{}'.format(i)
