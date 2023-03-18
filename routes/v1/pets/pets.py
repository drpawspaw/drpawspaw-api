from flask import Blueprint, request, jsonify
from models.pets.handler import PetSchema, VaccineEmailSchema
from routes import database_conn
from utils.email_sender.handler import send_reminder_email
from bson.objectid import ObjectId
import datetime

pet_api = Blueprint("pets", __name__, url_prefix="/api/v1/pets")

# define mongodb collection
pet_collection = database_conn['pets']

@pet_api.route('/', methods=['POST', 'GET'])
def pets():
    # Create new pet profile
    if request.method == 'POST':
        new_pet = PetSchema().load(request.get_json())
        pet_collection.insert_one(new_pet)
        return {  "data": "Record added successfully" }, 201

    # Retreive all the pets
    if request.method == 'GET':
        try:
            req_pet = pet_collection.find_one({"_id": ObjectId(request.args['id'])})
            req_pet['_id'] = str(req_pet['_id'])
            return jsonify(req_pet), 200
        except:
            pets = []
            for pet in pet_collection.find():
                pet['_id'] = str(pet['_id'])
                pets.append(pet)
            return jsonify(pets), 200
        return { "data": "Unable to retreive the data" }, 500

@pet_api.route("/vaccine-reminder", methods=['POST'])
def send_reminder():
    email_req = VaccineEmailSchema().load(request.get_json())
    return send_reminder_email(
        email_req['email'], 
        email_req['pet'], 
        email_req['owner'], 
        email_req['vaccine'], 
        email_req['date'].strftime("%d %b, %Y")
    )
