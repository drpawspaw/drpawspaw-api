import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To

def send_reminder_email(email, pet, owner, vaccine, date):
    to_emails = [(email, owner)]
    print(to_emails)

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
    except Exception as e:
        print("{ERROR}: ", e)
        return {  "data": "Unable to send the email" }, 500
    return {  "data": "Email send successfully" }, 200