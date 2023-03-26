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
vaccine_collection = database_conn['vaccines']

# send vaccination reminder to the owners
def send_reminder_email(email, pet, owner, vaccine, date):
    to_emails = [(email, owner)]
    message = Mail(
        from_email=os.getenv("SENDGRID_VACCINE_SENDER"),
        to_emails=to_emails
    )
    message.dynamic_template_data = {
        "owner_name": owner,
        "pet_name": pet,
        "vaccination_name": vaccine,
        "vaccination_date": date
    }
    message.template_id = os.getenv("SENDGRID_REMINDER_TEMPLATE_ID")
    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        code, body, headers = response.status_code, response.body, response.headers
        print("{SUCESS}: Email send successfully")
    except Exception as e:
        print("{ERROR}: Unable to send the email", e)
        return { 
            "data" : "Unable to send the email",
            "error": e
        }, 200
    return { "data" : "Email send successfully" }, 200

# send welcome email, once user signup with the platform
def send_welcome_email(email, name):
    to_emails = [(email, name)]
    message = Mail(
        from_email=os.getenv("SENDGRID_WELCOME_SENDER"),
        to_emails=to_emails
    )
    message.dynamic_template_data = {
        "name": name
    }
    message.template_id = os.getenv("SENDGRID_WELCOME_TEMPLATE_ID")
    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        code, body, headers = response.status_code, response.body, response.headers
        print("{SUCESS}: Email send successfully")
    except Exception as e:
        print("{ERROR}: Unable to send the email", e)

# email scheduler function to send reminders, this function running as background scheduler
def email_scheduler():
    for pet in pet_collection.find():
        for vaccine in vaccine_collection.find():
            if (pet['birthdate'] + datetime.timedelta(days=vaccine['time_period']*7)).strftime('%Y-%m-%d') == datetime.datetime.now().strftime('%Y-%m-%d'):
                # Get user details from database
                try:
                    owner = user_collection.find_one({"_id": ObjectId(pet["owner"])})
                    _, status = send_reminder_email(
                        owner["email"], 
                        pet["name"],
                        owner['name'],
                        pet["lastVaccination"],
                        pet['lastVaccinationDate'].isoformat().split('T')[0]
                    )
                    if status == 200:
                        print("{SUCCESS}: Email send successfully")
                except Exception as ex:
                    print("{ERROR}: Unable to send email notification", ex)