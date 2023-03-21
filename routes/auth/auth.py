from models.auth.handler import AuthRequestSchema, AuthResponse, AuthReject, AuthResponseSchema, AuthRejectSchema, AuthRefreshRequest, AuthRefreshRequestSchema, AuthSignupRequestSchema
from flask import request, Blueprint, jsonify, make_response, redirect
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from utils.email_sender.handler import send_welcome_email
from routes import database_conn
from functools import wraps
import datetime as dt
import requests
from dotenv import load_dotenv
import jwt
import os

# load environment variables
load_dotenv()

# Define the api wrapper and collection connection
auth_api = Blueprint("auth", __name__, url_prefix="/api/auth")
auth_col = database_conn['users']
hasher = Fernet(os.getenv("HASH_KEY"))

# Wrapper to validate the authentication
def auth_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token  = request.headers.get('Authorization')
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
                'expiration': str(datetime.utcnow() + timedelta(seconds=int(os.getenv("ACCESS_TOKEN_EXP"))))
            }, os.getenv("SECRET_KEY"))

# Generate refresh token
def grant_refresh_token(username):
    return jwt.encode({
                'token_type': "REFRESH_TOKEN",
                'username': username,
                'expiration': str(datetime.utcnow() + timedelta(seconds=int(os.getenv("REFRESH_TOKEN_EXP"))))
            }, os.getenv("SECRET_KEY"))

def is_user_exist(email):
    db_res = auth_col.find_one({ "email" : email })
    if db_res == None:
        return False
    return True

def is_password_valid(email, password):
    db_res = auth_col.find_one({ "email" : email })
    if db_res == None:
        return False
    if password == hasher.decrypt(db_res['password']).decode():
        return True
    return False

# Open link in https://accounts.google.com/o/oauth2/v2/auth?scope=https%3A//www.googleapis.com/auth/userinfo.email%20https%3A//www.googleapis.com/auth/userinfo.profile&access_type=offline&include_granted_scopes=true&response_type=code&redirect_uri=http%3A//localhost:8000/api/auth/google/callback&client_id=484685770657-g5upv6bcnc5e98j5r4p365sbeq1af6ms.apps.googleusercontent.com
@auth_api.route("/authenticate", methods=['GET'])
def authenticate():
    return make_response(jsonify({
         "access_token" : request.args.get("access_token"),
         "refresh_token" : request.args.get("refresh_token")
    }))

# Google callback endpoint - CreateAccount/Generate Access Tokens
@auth_api.route("/google/callback")
def google_callback():
    reject_schema = AuthRejectSchema(many=False)

    callback_uri = "http://{host}/api/auth/google/callback".format(host=os.getenv("HOST"))

    token_url = "https://oauth2.googleapis.com/token?code={code}&client_id={client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&grant_type=authorization_code".format(
        code=request.args.get('code'), client_id=os.getenv("GOOGLE_CLIENT_ID"), client_secret=os.getenv("GOOGLE_CLIENT_SECRET"), redirect_uri=callback_uri)

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    token_res = requests.post(token_url, headers=headers)
    if token_res.status_code != 200:
        return reject_schema.dump(AuthReject("Unable authenticate with Google server")), 403
    
    profile_url = "https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token={access_token}".format(
        access_token=token_res.json()['access_token'])
    profile_res = requests.get(profile_url)
    if profile_res.status_code != 200:
        return reject_schema.dump(AuthReject("Unable get tokens from Google server")), 403 
    
    user_res = profile_res.json()
    if auth_col.find_one({"email": user_res['email']}) == None:
        insert_res = auth_col.insert_one({
            "name": user_res['name'],
            "email": user_res['email'],
            "image_url": user_res['image_url'],
            "provider": "google",
            "created_at": dt.datetime.now()
        })
        if insert_res == None:
            return reject_schema.dump(AuthReject("Unable to create new user record")), 500

    send_welcome_email(user_res['email'], user_res['name'])

    redirect_url = "http://{host}/api/auth/authenticate?access_token={access_token}&refresh_token={refresh_token}".format(
        host=os.getenv("HOST"), access_token=grant_access_token(user_res['email']), refresh_token=grant_refresh_token(user_res['email'])
    )
    return redirect(redirect_url, code=302)

# Get new access tokens from refresh token
@auth_api.route("/refresh", methods=['POST'])
@auth_required
def new_token():
    auth_schema = AuthResponseSchema(many=False)
    reject_schema = AuthRejectSchema(many=False)
    auth_request = AuthRefreshRequestSchema().load(request.get_json())
    refresh_payload = jwt.decode(auth_request['refresh_token'], key=os.getenv('SECRET_KEY'), algorithms="HS256")
    if refresh_payload['token_type'] != "REFRESH_TOKEN":
        return reject_schema.dump(AuthReject("Invalid token")), 403
    return jsonify(auth_schema.dump(AuthResponse(grant_access_token(refresh_payload['username']), auth_request['refresh_token']))) 

@auth_api.route("/signup", methods=['POST'])
def auth_signup():
    auth_signup = AuthSignupRequestSchema().load(request.get_json())
    if auth_signup['email'] != "" and auth_signup['password'] != "" and auth_signup['name'] != "" and not is_user_exist(auth_signup['email']):
        encrpy_password = hasher.encrypt(auth_signup['password'].encode())
        insert_res = auth_col.insert_one({
            "name": auth_signup['name'],
            "email": auth_signup['email'],
            "password": encrpy_password.decode(),
            "image_url": "",
            "provider": "local",
            "created_at": dt.datetime.now(),
        })
        if insert_res == None:
            return reject_schema.dump(AuthReject("Unable to create new user record")), 500
        current_user = list(auth_col.find({ "email" : auth_signup['email'] }))[0]
        current_user['_id'] = str(current_user['_id'])
        return jsonify(current_user)
    reject_schema = AuthRejectSchema(many=False)
    return make_response(reject_schema.dump(AuthReject("User already exist or invalid request")), 409)

# Login using user credentials
@auth_api.route("/login", methods=['POST'])
def auth_login():
    auth_request = AuthRequestSchema().load(request.get_json())
    if auth_request['username'] != "" and is_password_valid(auth_request['username'], auth_request['password']):
        access_token = grant_access_token(auth_request['username']),
        refresh_token = grant_refresh_token(auth_request['username'])
        auth_schema = AuthResponseSchema(many=False)
        return jsonify(auth_schema.dump(AuthResponse(access_token, refresh_token)))
    reject_schema = AuthRejectSchema(many=False)
    return make_response(reject_schema.dump(AuthReject("Invalid username or password")), 403)