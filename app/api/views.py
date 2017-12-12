from flask import jsonify, request, make_response
from flask_login import login_required, login_user, logout_user, current_user


from . import api
from app import db
from ..models import Category, User

@api.route('/user', methods=['POST'])
def create_user():
    post_data = request.get_json()

    user1 = User.query.filter_by(username=post_data['username']).first()
    user2 = User.query.filter_by(email=post_data['email']).first()


    if user1 or user2:
        return jsonify({'message' : 'user exists'})

    user = User(email = post_data['email'],
                username = post_data['username'],
                first_name = post_data['first_name'],
                last_name = post_data['last_name'],
                password = post_data['password'])

    # add user to the database
    db.session.add(user)
    db.session.commit()

    return jsonify({'message' : 'user created successfully'})

@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    user = User.query.filter_by(email=data['email']).first()

    if user is not None and user.verify_password(data['password']):

        login_user(user)

        token = user.generate_token(user.id)

        response = {
            'message': 'You logged in successfully.',
            'access_token': token.decode()
        }
        return make_response(jsonify(response)), 200

    response = {
        'message': 'Invalid email or password, Please try again'
    }
    return jsonify(response)

@api.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()

    if current_user.is_anonymous:
        response = {
            'message' : 'You are not logged in.'
        }
        return jsonify(response)

    if data['email'] == current_user.email and current_user.verify_password(data['password']):
        logout_user()
        response = {
            'message': 'You have successfully logged out'
        }
        return jsonify(response)

    response = {
        'message': 'Incorrect credentials supplied.'
    }
    return jsonify(response)

@api.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()

    if current_user.is_anonymous:
        response = {
            'message' : 'You are not logged in.'
        }
        return jsonify(response)

    if current_user.verify_password(data['current_password']):
        current_user.reset_password(data['new_password'])
        response = {
            'message' : 'You have successfully changed your password.'
        }
        return jsonify(response)

    response = {
        'message' : 'incorrect old password supplied.'
    }

    return jsonify(response)

@api.route('/category', methods=['POST', 'GET'])
def get_all_categories():
    # Get the access token from the header
    auth_header = request.headers.get('Authorization')
    access_token = auth_header.split(" ")[1]

    if access_token:
        # Attempt to decode the token and get the User ID
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            # Go ahead and handle the request, the user is authenticated
            if request.method == 'POST':
                data = request.get_json()
                if data['name']:
                    category = Category(name = data['name'], user_id = user_id)

                    db.session.add(category)
                    db.session.commit()

                    response = {'id' : category.id,
                        'category_name' : category.name,
                        'created_by' : category.user_id
                    }

                    return jsonify(response)

            else:
                categories = Category.query.filter_by(user_id=user_id).all()

                output = []

                for category in categories:
                    category_data = {}
                    category_data['id'] = category.id
                    category_data['Name'] = category.name
                    output.append(category_data)

                return jsonify({'categories' : output})

        else:
            # user is not legit, so the payload is an error message
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401


@api.route('/category/<category_id>', methods=['GET'])
def get_one_category(category_id):
    # Get the access token from the header
    auth_header = request.headers.get('Authorization')
    access_token = auth_header.split(" ")[1]

    if access_token:
        # Attempt to decode the token and get the User ID
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):

            category = Category.query.filter_by(user_id=user_id).filter_by(id=category_id).first()

            if not category:
                return jsonify({'message' : 'No category found'})

            category_data = {}
            category_data['id'] = category.id
            category_data['Name'] = category.name

            return jsonify({'category': category_data})

        else:
            # user is not legit, so the payload is an error message
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401



@api.route('/category/<category_id>', methods=['PUT'])
def change_category_name(category_id):
    # Get the access token from the header
    auth_header = request.headers.get('Authorization')
    access_token = auth_header.split(" ")[1]

    if access_token:
        # Attempt to decode the token and get the User ID
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            category = Category.query.filter_by(user_id=user_id).filter_by(id=category_id).first()

            if category:
                return jsonify({'message' : category.name})

            data = request.get_json()
            if data['name']:
                prev_name = category.name
                category.name = data['name']
                db.session.commit()

                return jsonify({'message' : 'Category ' + prev_name + 'changed to ' + category.name})

        else:
            # user is not legit, so the payload is an error message
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401

@api.route('/category/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    # Get the access token from the header
    auth_header = request.headers.get('Authorization')
    access_token = auth_header.split(" ")[1]

    if access_token:
        # Attempt to decode the token and get the User ID
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            category = Category.query.filter_by(user_id=user_id).filter_by(id=category_id).first()
            category_name = category.name

            if not category:
                return jsonify({'message' : 'No category found'})

            db.session.delete(category)

            return jsonify({'message' : 'Category ' + category_name + ' deleted successfully'})

        else:
            # user is not legit, so the payload is an error message
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401