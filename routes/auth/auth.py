from models.auth.handler import AuthRequestSchema, AuthResponse, AuthReject, AuthResponseSchema, AuthRejectSchema, \
    AuthRefreshRequest, AuthRefreshRequestSchema
from flask import request, Blueprint, jsonify, make_response
from datetime import datetime, timedelta
from functools import wraps
from base64 import encode
import jwt
import os

auth_api = Blueprint("auth", __name__, url_prefix="/api/auth")

# Wrapper to validate the authentication
def auth_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        reject_schema = AuthRejectSchema(many=False)
        if not token:
            return reject_schema.dump(AuthReject("Token not found")), 403
        if len(token.split(" ")) != 2 and token.split(" ")[0].lower() != "bearer":
            return reject_schema.dump(AuthReject("Invalid token")), 403
        try:
            payload = jwt.decode(str(token.split(" ")[1]), key=os.getenv('SECRET_KEY'), algorithms="HS256")
            if payload['token_type'] != "ACCESS_TOKEN":
                return reject_schema.dump(AuthReject("Invalid token type")), 403
            try:
                if datetime.utcnow() > datetime.strptime(payload['expiration'], '%Y-%m-%d %H:%M:%S.%f'):
                    return reject_schema.dump(AuthReject("Token expired")), 403
            except Exception as e:
                return reject_schema.dump(AuthReject(e)), 403
        except Exception as e:
            return reject_schema.dump(AuthReject(e)), 403
        return func(*args, **kwargs)

    return decorated

# Generate access token
def grant_access_token(username):
    return jwt.encode({
        'token_type': "ACCESS_TOKEN",
        'username': username,
        'expiration': str(datetime.utcnow() + timedelta(minutes=60))
    }, os.getenv("SECRET_KEY"))

# Generate refresh token
def grant_refresh_token(username):
    return jwt.encode({
        'token_type': "REFRESH_TOKEN",
        'username': username,
        'expiration': str(datetime.utcnow() + timedelta(days=30))
    }, os.getenv("SECRET_KEY"))


# Need to get the new access_token from the refresh_token, but before expired the access_token
def grant_access_token_from_refresh_token(access_token, refresh_token):
    username = jwt.decode(access_token).items
    print(username)

# ---------------------------------------------------------------------------------------------
# TODO - Sample endpoint => You can remove this after the implementation
@auth_api.route("/authenticate", methods=['GET'])
@auth_required
def authenticate():
    return make_response(jsonify({"data": "Authenticated!"}))
# ---------------------------------------------------------------------------------------------

@auth_api.route("/refresh", methods=['POST'])
@auth_required
def new_token():
    auth_schema = AuthResponseSchema(many=False)
    reject_schema = AuthRejectSchema(many=False)
    auth_request = AuthRefreshRequestSchema().load(request.get_json())
    refresh_payload = jwt.decode(auth_request['refresh_token'], key=os.getenv('SECRET_KEY'), algorithms="HS256")
    if refresh_payload['token_type'] != "REFRESH_TOKEN":
        return reject_schema.dump(AuthReject("Invalid token")), 403
    return jsonify(
        auth_schema.dump(AuthResponse(grant_access_token(refresh_payload['username']), auth_request['refresh_token'])))

@auth_api.route("/login", methods=['POST'])
def auth_login():
    auth_request = AuthRequestSchema().load(request.get_json())
    if auth_request['username'] != "" and auth_request['password'] == "1234":
        access_token = grant_access_token(auth_request['username']),
        refresh_token = grant_refresh_token(auth_request['username'])
        auth_schema = AuthResponseSchema(many=False)
        return jsonify(auth_schema.dump(AuthResponse(access_token, refresh_token)))
    else:
        reject_schema = AuthRejectSchema(many=False)
        return make_response(reject_schema.dump(AuthReject("Invalid username or password")), 403)
