import unittest
import os
import json
from app import create_app, db

class AuthTestCase(unittest.TestCase):
    """Test case for the auth blueprint
    """
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.user = {
            'first_name' : 'Tester',
            'last_name' : 'Api',
            'username' : 'apitester',
            'email' : 'tester@api.com',
            'password' : 'abc'
        }

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.session.close()
            db.drop_all()
            db.create_all()

    def test_user_registration(self):
        res = self.client().post('/api/v1.0/register', data=json.dumps(self.user), content_type='application/json')

        self.assertIn('user created successfully', str(res.data))

    def test_user_login(self):
        reg_res = self.client().post('/api/v1.0/register', data=json.dumps(self.user), content_type='application/json')
        self.assertEqual(reg_res.status_code, 201)

        login_res = self.client().post('/api/v1.0/login', data=json.dumps(self.user), content_type='application/json')

        # get the results in json format
        result = json.loads(login_res.data.decode())
        # Test that the response contains success message
        self.assertEqual(result['message'], "You logged in successfully.")
        # Assert that the status code is equal to 200
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(result['access_token'])

    def test_already_registered_user(self):
        res = self.client().post('/api/v1.0/register', data=json.dumps(self.user), content_type='application/json')
        self.assertEqual(res.status_code, 201)
        second_res = self.client().post('/api/v1.0/register', data=json.dumps(self.user), content_type='application/json')
        self.assertEqual(second_res.status_code, 409)

        # get the results returned in json format
        result = json.loads(second_res.data.decode())
        self.assertEqual(result['message'], "User already exists. Please login.")

    def test_non_registered_user_login(self):
        """Test non registered users cannot login."""
        # define a dictionary to represent an unregistered user
        not_a_user = {
            'email': 'not_a_user@example.com',
            'password': 'nope'
        }
        # send a POST request to /auth/login with the data above
        res = self.client().post('/api/v1.0/login', data=json.dumps(not_a_user), content_type='application/json')
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
