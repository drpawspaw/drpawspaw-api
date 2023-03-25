from flask import Blueprint, request, jsonify
from models.pets.handler import TreatmentSchema, VaccineSchema
from routes import database_conn
from bson.objectid import ObjectId
from routes.auth.auth import auth_required
from flask_cors import CORS, cross_origin
import datetime

vaccines_api = Blueprint("vaccines", __name__, url_prefix="/api/v1/vaccines")

# define mongodb collections
treatment_collection = database_conn['treatments']
vaccine_collection = database_conn['vaccines']
pet_collection = database_conn['pets']

@vaccines_api.route("/", methods=['GET', 'POST'])
# @auth_required
@cross_origin
def vaccines():
    if request.method == 'POST':
        new_vaccines = VaccineSchema().load(request.get_json())
        vaccine_collection.insert_one(new_pet)
        return {  "data": "Record added successfully" }, 201
    
    # In here, API should contain owner's id, then
    # 1. Retrieve all the pets for his/her accounts
    # 2. By looping through the array of pets, we will check the next vaccine
    # 3. If there any of vaccines, then we will add it to a seperate list and return it
    if request.method == 'GET':
        try:
            # Request pet by profile id
            # req_pet = pet_collection.find_one({"_id": ObjectId(request.args['id'])})
            # req_pet['_id'] = str(req_pet['_id'])
            return { "data": "Data retrieved successfully" }, 200
        except:
            return { "data": "Unable to read the data" }, 500
            # Request pets by owner id
            # vaccines = []
            # for pet in pet_collection.find():
            #     if pet['owner'] == request.args['owner']:
            #         pet['_id'] = str(pet['_id'])
            #         vaccines.append(pet)
            # return jsonify(owner_pet), 200

@vaccines_api.route("/<id>", methods=['DELETE'])
# @auth_required
@cross_origin()
def vaccines_delete():
    if request.method == 'DELETE':
        result = vaccine_collection.find_one_and_delete(
            {"_id" : ObjectId(id)}
        )
        if result["_id"] == ObjectId(id):
            return { "data": "Deleted successfully" }, 200
        return { "data": "Unable to delete the record" }, 500