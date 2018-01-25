import json

from .test_base import BaseTestCase

class CategoryTestCase(BaseTestCase):
    """This class represents the Category test case"""

    def test_category_can_be_created_successfully(self):
        """Test that the Api can create a category"""
        # get the token and context
        token_and_context = self.get_token()
        token = token_and_context['token']
        context = token_and_context['context']

        # Create a category by going to that link
        response = self.create_category(token=token, context=context)
        self.assertEquals(response.status_code, 201)

    def test_category_creation_fails_with_wrong_token(self):
        """Test that the the category is not created when user provides a wrong token"""
        # get the token and context
        token_and_context = self.get_token()
        token = token_and_context['token']
        context = token_and_context['context']

        #put in some random token
        token = "fsdjbdfjkhaey489yy276437grewjba73t4iauht47yhfuy4y37"

        # Create a category by going to that link
        response = self.create_category(token=token, context=context)
        self.assertEquals(response.status_code, 400)

    def test_get_all_categories_successfully(self):
        """Test GET request on categories"""
        # get the token and context
        token_and_context = self.get_token()
        token = token_and_context['token']
        context = token_and_context['context']

        # Create a category using create_category method
        category_create_response = self.create_category(token=token, context=context)
        self.assertEquals(category_create_response.status_code, 201)

        # get all categories by going to that link in the app using login context
        category_get_response = context.get('/api/v1.0/category', headers=dict(Authorization="Bearer " + token))
        self.assertEquals(category_get_response.status_code, 200)

        result = json.loads(category_get_response.data)
        category_result = result['categories'][0]

        self.assertEquals(category_result['Name'], 'Yummy')

    def test_get_limited_categories_successfully(self):
        """Test GET request on category with limit parameter"""
        # get the token and context
        token_and_context = self.get_token()
        token = token_and_context['token']
        context = token_and_context['context']

        # Create 5 categories using create_category method
        self.create_category(token=token, context=context, cat_num=5)

        # get 3 categories by going to that link in the app using login context and limit parameter
        category_get_response = context.get('/api/v1.0/category?limit=3', headers=dict(Authorization="Bearer " + token))
        self.assertEquals(category_get_response.status_code, 200)

        result = json.loads(category_get_response.data)['categories']
        self.assertEquals(len(result), 3)

    def test_get_categories_starting_with_certain_category_successfully(self):
        """Test GET request on category with offset parameter"""
        # get the token and context
        token_and_context = self.get_token()
        token = token_and_context['token']
        context = token_and_context['context']

        # Create 5 categories using create_category method, named category1 to category5
        self.create_category(token=token, context=context, cat_num=5)

        # get 3 categories by going to that link in the app using login context and limit parameter
        category_get_response = context.get('/api/v1.0/category?offset=2', headers=dict(Authorization="Bearer " + token))
        self.assertEquals(category_get_response.status_code, 200)

        #check that 3 categories are returned,
        #and the first one is "category3", because the offset is set to 2
        result = json.loads(category_get_response.data)['categories']
        self.assertEquals(len(result), 3)
        first_category = result[0]
        self.assertEquals(first_category['Name'], 'category3')

    def test_get_limited_categories_starting_with_specific_category_successfully(self):
        """Test GET request on category with offset and limit parameter"""
        # get the token and context
        token_and_context = self.get_token()
        token = token_and_context['token']
        context = token_and_context['context']

        # Create 5 categories using create_category method, named category1 to category5
        self.create_category(token=token, context=context, cat_num=5)

        # get 3 categories by going to that link in the app using login context and limit parameter
        category_get_response = context.get('/api/v1.0/category?limit=2&offset=1', headers=dict(Authorization="Bearer " + token))
        self.assertEquals(category_get_response.status_code, 200)

        #check that 2 categories are returned; because the limit is set to 2
        # and the first category is "category2", because the offset is set to 1
        result = json.loads(category_get_response.data)['categories']
        self.assertEquals(len(result), 2)
        first_category = result[0]
        self.assertEquals(first_category['Name'], 'category2')

    def test_get_a_searched_category_successfully(self):
        """Test GET request on category with offset and limit parameter"""
        # get the token and context
        token_and_context = self.get_token()
        token = token_and_context['token']
        context = token_and_context['context']

        # Create 5 categories using create_category method, named category1 to category5
        self.create_category(token=token, context=context, cat_num=5)

        # get 3 categories by going to that link in the app using login context and limit parameter
        category_get_response = context.get('/api/v1.0/category?q=category3', headers=dict(Authorization="Bearer " + token))
        self.assertEquals(category_get_response.status_code, 200)

        #check that category with name category3 is in the list
        result = json.loads(category_get_response.data)['categories']
        first_category = result[0]
        self.assertEquals(first_category['Name'], 'category3')

    def test_get_one_category_successfully(self):
        """Test GET verb on category by category's id"""
        # get the token and context
        token_and_context = self.get_token()
        token = token_and_context['token']
        context = token_and_context['context']

        # Create 5 categories using create_category method, named category1 to category5
        self.create_category(token=token, context=context, cat_num=5)

        #visit the url using id of 3
        response = context.get('/api/v1.0/category/3', headers=dict(Authorization="Bearer " + token))
        self.assertEquals(response.status_code, 200)

        #check that category with id 3 is in the list
        result = json.loads(response.data)['category']
        self.assertEquals(result['id'], 3)

    def test_editing_a_category_successfully(self):
        """Test PUT verb on category by category's id"""
        # get the token and context
        token_and_context = self.get_token()
        token = token_and_context['token']
        context = token_and_context['context']

        # Create 5 categories using create_category method, named category1 to category5
        self.create_category(token=token, context=context, cat_num=5)

        #visit the url using id of 2
        response = context.put('/api/v1.0/category/2', headers=dict(Authorization="Bearer " + token), data=json.dumps({'name' : 'awesome'}), content_type='application/json')
        self.assertEquals(response.status_code, 200)

        #get category of id 2 and check that it has a changed name; 'awesome'
        response = context.get('/api/v1.0/category/2', headers=dict(Authorization="Bearer " + token))
        self.assertEquals(response.status_code, 200)
        result = json.loads(response.data)['category']
        self.assertEquals(result['Name'], 'awesome')

    def test_deleting_a_category_successfully(self):
        """Test delete verb on category by category's id"""
        # get the token and context
        token_and_context = self.get_token()
        token = token_and_context['token']
        context = token_and_context['context']

        # Create 5 categories using create_category method, named category1 to category5
        self.create_category(token=token, context=context, cat_num=5)

        #visit the delete url using id of 4
        response = context.delete('/api/v1.0/category/4', headers=dict(Authorization="Bearer " + token))
        self.assertEquals(response.status_code, 200)

        #try getting the category and confirm that it does not exist
        response = context.get('/api/v1.0/category?q=category4', headers=dict(Authorization="Bearer " + token))
        self.assertEquals(response.status_code, 404)
