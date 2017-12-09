from flask import jsonify, request
from flask_login import login_required, login_user, logout_user, current_user


from . import api
from app import db
from ..models import Category, User

@api.route('/register', methods=['POST'])
def create_user():
    data = request.get_json()

    '''
    return jsonify({
        'email' : data['email'],
        'username' : data['username'],
        'firstname' : data['first_name'],
        'lastname' : data['last_name'],
        'password' : data['password']
    })'''

    user = User(email = data['email'],
                username = data['username'],
                first_name = data['first_name'],
                last_name = data['last_name'],
                password = data['password'])

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
            'message' : 'You logged in successfully.',
            'token' : token
        }

        return jsonify(response)

    response = {
        'message': 'Invalid email or password, Please try again'
    }
    return jsonify(response)

@api.route('/logout', methods=['POST'])
def logout():
    data = request.get_json()

    if data['email'] == current_user.email and current_user.verify_password(data['password']):
        logout_user()
        response = {
            'message': 'You have successfully logged out'
        }
        return response

    response = {
        'message': 'Incorrect credentials supplied.'
    }
    return response

@api.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()

    if current_user.verify_password(data['current password']):
        current_user.password(data['new password'])
        response = {
            'message' : 'You have successfully changed your password.'
        }
        return response

    response = {
        'message' : 'incorrect old password supplied.'
    }

    return response

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