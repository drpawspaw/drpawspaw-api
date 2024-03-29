from flask import Blueprint, request, jsonify
from models.user.handler import UserSchema
from routes import database_conn
from flask_cors import CORS, cross_origin

static_api = Blueprint("static", __name__)

# define mongodb collection
vaccine_collection = database_conn['vaccines']
treatment_collection = database_conn['treatments']

@static_api.route("/api/v1/static/vaccines", methods=['GET'], endpoint='getVaccines')
@cross_origin()
def get_vaccines():
    if request.method == 'GET':
        vaccines = []
        for vaccine in vaccine_collection.find():
            vaccine['_id'] = str(vaccine['_id'])
            vaccines.append(vaccine)
        return jsonify(vaccines), 200

@static_api.route("/api/v1/static/treatments", methods=['GET'], endpoint='getTreatments')
@cross_origin()
def get_vaccines():
    if request.method == 'GET':
        treatments = []
        for treat in treatment_collection.find():
            treat['_id'] = str(treat['_id'])
            treatments.append(treat)
        return jsonify(treatments), 200

@static_api.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response