import unittest
import os
import json
from app import create_app, db
from app.models import User

class AuthTestCase(unittest.TestCase):
    """Test case for the auth blueprint
    """
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        # this user has already been created in the db
        self.user = {
            'first_name' : 'Harith',
            'last_name' : 'Bakhrani',
            'username' : 'harithj',
            'email' : 'harithjaved@gmail.com',
            'password' : 'password'
        }
        self.url = '/api/v1.0/auth/'

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.session.close()
            db.drop_all()
            db.create_all()
            # Create a user in the db
            user = User(email = 'harithjaved@gmail.com',
                        username = 'harithj',
                        first_name = 'Harith',
                        last_name = 'Bakhrani',
                        password = 'password')
            db.session.add(user)
            db.session.commit()

    def test_user_can_register_successfully(self):
        user = {
            'first_name' : 'Tester',
            'last_name' : 'Api',
            'username' : 'apitester',
            'email' : 'tester@api.com',
            'password' : 'abc123456'
        }
        res = self.client().post(self.url + 'register', data=json.dumps(user), content_type='application/json')

        self.assertIn('user created successfully', str(res.data))

    def test_user_can_login_successfully(self):
        login_res = self.client().post(self.url + 'login', data=json.dumps(self.user), content_type='application/json')

        # get the results in json format
        result = json.loads(login_res.data.decode())
        # Test that the response contains success message
        self.assertEqual(result['message'], "You logged in successfully.")
        # Assert that the status code is equal to 200
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(result['access_token'])

    def test_already_registered_user_cannot_register_again(self):
        second_res = self.client().post(self.url + 'register', data=json.dumps(self.user), content_type='application/json')
        self.assertEqual(second_res.status_code, 409)

        # get the results returned in json format
        result = json.loads(second_res.data.decode())
        self.assertEqual(result['message'], "The username has already been taken, please choose another username.")

    def test_non_registered_user_cannot_login(self):
        """Test non registered users cannot login."""
        # define a dictionary to represent an unregistered user
        not_a_user = {
            'email': 'not_a_user@example.com',
            'password': 'nopassword'
        }
        # send a POST request to /auth/login with the data above
        res = self.client().post(self.url + 'login', data=json.dumps(not_a_user), content_type='application/json')
        # get the result in json
        result = json.loads(res.data.decode())

        # assert that this response must contain an error message
        # and an error status code 401(Unauthorized)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(
            result['message'], "Invalid email or password, Please try again")

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
