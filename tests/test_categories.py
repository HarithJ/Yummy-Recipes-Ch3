import unittest
import os
import json
from app import create_app, db


class CategoryTestCase(unittest.TestCase):
    """This class represents the Category test case"""

    def setUp(self):
        """setup test variables"""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.category_data = {'name' : 'Yummy'}

        # binds the app with the current context
        with self.app.app_context():
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
        To
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

    def test_category_creation(self):
        """Test that the Api can create a category"""
        self.register_user()

        login_dict = self.login_user()
        login_response = login_dict['login_response']
        context = login_dict['context']

        token = json.loads(login_response.data)
        token = token['access_token']

        # Create a category by going to that link
        response = context.post('/api/v1.0/category', headers=dict(Authorization="Bearer " + token), data=json.dumps(self.category_data), content_type='application/json')
        self.assertEquals(response.status_code, 201)