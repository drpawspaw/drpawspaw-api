from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To
from routes import database_conn
from models.pets.handler import PetSchema
from bson.objectid import ObjectId
import os
import datetime

# define mongodb collection
pet_collection = database_conn['pets']
user_collection = database_conn['users']

def send_reminder_email(email, pet, owner, vaccine, date):
    to_emails = [(email, owner)]
    message = Mail(
        from_email=os.getenv("SENDGRID_SENDER"),
        to_emails=to_emails
    )
    message.dynamic_template_data = {
        "owner_name": owner,
        "pet_name": pet,
        "vaccination_name": vaccine,
        "vaccination_date": date
    }
    message.template_id = os.getenv("SENDGRID_TEMPLATE_ID")
    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        code, body, headers = response.status_code, response.body, response.headers
        print("{SUCESS}: Email send successfully")
    except Exception as e:
        print("{ERROR}: Unable to send the email", e)

def email_scheduler():
    for pet in pet_collection.find():
        if pet['lastVaccinationDate'].isoformat().split('T')[0] == datetime.datetime.now().strftime('%Y-%m-%d'):
            # Get user details from database
            try:
                print("owner", pet["owner"])
                owner = user_collection.find_one({"_id": ObjectId(pet["owner"])})
                send_reminder_email(
                    owner["email"], 
                    pet["name"],
                    owner['name'],
                    pet["lastVaccination"],
                    pet['lastVaccinationDate'].isoformat().split('T')[0]
                )
            except Exception as ex:
                print("{ERROR}: Unable to send email notification", ex)