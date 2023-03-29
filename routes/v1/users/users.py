from flask import Blueprint, request, jsonify
from models.user.handler import UserSchema
from routes.auth.auth import auth_required
from routes import database_conn
from flask_cors import CORS, cross_origin


user_api = Blueprint("users", __name__)

# define mongodb collection
user_collection = database_conn['users']


@user_api.route('/api/v1/users', methods=['GET', 'POST'])
@cross_origin()
@auth_required
def users():
    if request.method == 'POST':
        new_user = UserSchema().load(request.get_json())
        user_collection.insert_one(new_user)
        return {"data": "Record added successfully"}, 201

    if request.method == 'GET':
        try:
            req_user = user_collection.find_one({"email": request.args['email']})
            req_user["_id"] = str(req_user["_id"])
            print("req_user", req_user)
            return jsonify(req_user), 200
        except:
            current_users = []
            for user in user_collection.find():
                user['_id'] = str(user['_id'])
                current_users.append(user)
            return jsonify(current_users), 200
        
@user_api.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response