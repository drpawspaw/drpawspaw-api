from flask import Blueprint, request, jsonify
from models.pets.handler import TreatmentSchema, VaccineSchema
from routes import database_conn
from bson.objectid import ObjectId
from routes.auth.auth import auth_required
from flask_cors import CORS, cross_origin
import datetime

vaccines_api = Blueprint("vaccines", __name__)

# define mongodb collections
vaccine_collection = database_conn['vaccines']
pet_collection = database_conn['pets']

@vaccines_api.route("/api/v1/vaccines", methods=['GET', 'POST'])
@cross_origin()
@auth_required
def vaccines():
    if request.method == 'POST':
        new_vaccines = VaccineSchema().load(request.get_json())
        vaccine_collection.insert_one(new_vaccines)
        return {  "data": "Record added successfully" }, 201
    
    # In here, API should contain owner's id, then
    # 1. Retrieve all the pets for his/her accounts
    # 2. By looping through the array of pets, we will check the next vaccine
    # 3. If there any of vaccines, then we will add it to a seperate list and return it
    if request.method == 'GET':
        try:
            vaccine_list = []
            # Get all the pets
            for pet in pet_collection.find():
                if pet['owner'] == request.args['owner']:
                    # Get all the vaccines
                    for vaccine in vaccine_collection.find():
                        vaccine_date = pet['birthdate'] + datetime.timedelta(days=vaccine['time_period']*7)
                        # Filter it out by upcoming vaccine or past vaccine
                        if vaccine_date>datetime.datetime.now():
                            up_vaccine = {}
                            up_vaccine['pet'] = pet['name']
                            up_vaccine['vaccine'] = vaccine['name']
                            up_vaccine['description'] = vaccine['description']
                            up_vaccine['date'] = vaccine_date
                            vaccine_list.append(up_vaccine)
            return jsonify(vaccine_list), 200
        except Exception as e:
            print("Exception: ",e)
            return { "data": "Unable to read the data" }, 500

@vaccines_api.route("/api/v1/vaccines/<id>", methods=['DELETE'])
@cross_origin()
@auth_required
def vaccines_delete():
    if request.method == 'DELETE':
        result = vaccine_collection.find_one_and_delete(
            {"_id" : ObjectId(id)}
        )
        if result["_id"] == ObjectId(id):
            return { "data": "Deleted successfully" }, 200
        return { "data": "Unable to delete the record" }, 500

@vaccines_api.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response