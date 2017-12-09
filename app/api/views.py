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

    if current_user.verify_password(data['current_password']):
        return jsonify({"msg" : "user verified"})
        current_user.password(data['new_password'])
        response = {
            'message' : 'You have successfully changed your password.'
        }
        return jsonify(response)

    response = {
        'message' : 'incorrect old password supplied.'
    }

    return jsonify(response)

@api.route('/category', methods=['GET'])
def get_all_categories():
    categories = Category.query.all()

    output = []

    for category in categories:
        category_data = {}
        category_data['id'] = category.id
        category_data['Name'] = category.name
        output.append(category_data)

    return jsonify({'categories' : output})

@api.route('/category/<category_id>', methods=['GET'])
def get_one_category(category_id):
    category = Category.query.filter_by(id=category_id).first()

    if not category:
        return jsonify({'message' : 'No category found'})

    category_data = {}
    category_data['id'] = category.id
    category_data['Name'] = category.name

    return jsonify({'category': category_data})

@api.route('/category', methods=['POST'])
def create_category():
    return ''

@api.route('/category', methods=['PUT'])
def change_category_name():
    return ''

@api.route('/category', methods=['DELETE'])
def delete_category():
    return ''