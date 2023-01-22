from xxlimited import new
from flask import Blueprint, request, jsonify
from models.user.handler import UserSchema
from routes import database_conn

user_api = Blueprint("users", __name__, url_prefix="/api/v1/users")

# define mongodb collection
user_collection = database_conn['users']


@user_api.route('/', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        new_user = UserSchema().load(request.get_json())
        user_collection.insert_one(new_user)
        return {"data": "Record added successfully"}, 201

    if request.method == 'GET':
        current_users = []
        for user in user_collection.find():
            user['_id'] = str(user['_id'])
            current_users.append(user)
        return jsonify(current_users), 200