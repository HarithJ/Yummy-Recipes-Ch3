from flask import jsonify, request

from . import api
from app import db
from ..models import Category, User

@api.route('/user', methods=['POST'])
def create_user():
    data = request.data


    return jsonify({'message' : data['email']})

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