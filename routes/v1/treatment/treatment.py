from flask import Blueprint, request, jsonify
from models.pets.handler import TreatmentSchema, VaccineSchema
from routes import database_conn
from bson.objectid import ObjectId
from routes.auth.auth import auth_required
from flask_cors import CORS, cross_origin
import datetime

treatments_api = Blueprint("treatments", __name__)

# define mongodb collections
treatment_collection = database_conn['treatments']

@treatments_api.route("/api/v1/treatments", methods=['GET', 'POST'])
@cross_origin()
@auth_required
def treatments():
    if request.method == 'GET':
        treatments = []
        for tre in treatment_collection.find():
            tre['_id'] = str(tre['_id'])
            treatments.append(tre)
        return jsonify(treatments), 200

    if request.method == 'POST':
        new_treatment = TreatmentSchema().load(request.get_json())
        treatment_collection.insert_one(new_treatment)
        return {  "data": "Record added successfully" }, 201

@treatments_api.route("/api/v1/treatments/<id>", methods=['DELETE'], endpoint='deleteTreatment')
@cross_origin()
@auth_required
def treatment_delete():
    if request.method == 'DELETE':
        result = treatment_collection.find_one_and_delete(
            {"_id" : ObjectId(id)}
        )
        if result["_id"] == ObjectId(id):
            return { "data": "Deleted successfully" }, 200
        return { "data": "Unable to delete the record" }, 500

@treatments_api.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    return response