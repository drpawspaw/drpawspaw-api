from flask import Blueprint, request, jsonify
from models.pets.handler import PetSchema
from routes import database_conn
from utils.email_sender.handler import send_reminder_email
from bson.objectid import ObjectId
from routes.auth.auth import auth_required
from flask_cors import CORS, cross_origin

import datetime

pet_api = Blueprint("pets", __name__, url_prefix="/api/v1/pets")

# define mongodb collection
pet_collection = database_conn['pets']

@pet_api.route('/', methods=['POST', 'GET', 'PUT', 'DELETE'])
@auth_required
@cross_origin()
def retrieve_create_pets():
    # Create new pet profile
    if request.method == 'POST':
        new_pet = PetSchema().load(request.get_json())
        pet_collection.insert_one(new_pet)
        return {  "data": "Record added successfully" }, 201

    if request.method == 'GET':
        try:
            # Request pet by profile id
            req_pet = pet_collection.find_one({"_id": ObjectId(request.args['id'])})
            req_pet['_id'] = str(req_pet['_id'])
            return jsonify(req_pet), 200
        except:
            try:
                # Request pets by owner id
                owner_pet = []
                for pet in pet_collection.find():
                    if pet['owner'] == request.args['owner']:
                        pet['_id'] = str(pet['_id'])
                        owner_pet.append(pet)
                return jsonify(owner_pet), 200
            except:
                # Request all the pets
                pets = []
                for pet in pet_collection.find():
                    pet['_id'] = str(pet['_id'])
                    pets.append(pet)
                return jsonify(pets), 200
        return { "data": "Unable to retreive the records" }, 500
    
@pet_api.route('/<id>', methods=['PUT', 'DELETE'])
@auth_required
@cross_origin()
def update_delete(id):
    if request.method == 'PUT':
        req_update = PetSchema().load(request.get_json())
        result = pet_collection.find_one_and_update(
            {"_id" : ObjectId(id)},
            {"$set": req_update},
            upsert=True
        )
        if result["_id"] == ObjectId(id):
            return { "data": "Updated successfully" }, 200
        return { "data": "Unable to update the record" }, 500

    if request.method == 'DELETE':
        result = pet_collection.find_one_and_delete(
            {"_id" : ObjectId(id)}
        )
        if result["_id"] == ObjectId(id):
            return { "data": "Deleted successfully" }, 200
        return { "data": "Unable to delete the record" }, 500