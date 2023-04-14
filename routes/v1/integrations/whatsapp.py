from flask import Blueprint, request, jsonify
from flask_cors import CORS, cross_origin
from models.integrations.handler import WhatsAppPayloadSchema
from routes.v1.chatbot.chatbot import handle_chat
import requests
import json
import os

whatsapp_hook = Blueprint("integration_whatsapp", __name__)

@whatsapp_hook.route("/api/v1/whatsapp/webhook", methods=['GET', 'POST'])
@cross_origin()
def webhook():
    # authenticate webhook
    if request.method == 'GET':
        try:
            mode = request.args['hub.mode']
            challenge = request.args['hub.challenge']
            token = request.args['hub.verify_token']
            if (mode == "subscribe" and token == os.getenv("WEBHOOK_SECRET")):
                return challenge, 200
            return { "error": "Unable to authenticate webhook"}, 403 
        except:
            return { "error": "Unable to read the webhook"}, 403

    if request.method == 'POST':
        req_body = request.get_json()
        try:
            user_message = req_body['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
            user_number = req_body['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
            response_message = handle_chat(user_message, user_number)
            status = send_reply(response_message['response'], user_number)
            if response_message['treatments'] != "":
                send_reply(response_message['treatments'], user_number)
            if len(response_message['suggestions']) != 0:
                sm = "Here are the suggestions for symptoms - {syms}".format(syms=", ".join(response_message['suggestions'][:5]))
                send_reply(sm, user_number)
            if status == False:
                return { "data": "Unable to send the message" }, 500
            return { "data": "Message send successfully" }, 200
        except Exception as e:
            print("error: ", e)
            return { "data": "Unable to read webhook body" }, 400

def send_reply(message, number):
    headers = {
        'Authorization': "Bearer {token}".format(token=os.getenv("WHATSAPP_ACCESS_TOKEN")),
        'Content-Type': 'application/json'
    }
    payload = json.dumps({
        "messaging_product": "whatsapp",
        "to": str(number),
        "text": {
            "body": message
        }
    })
    res = requests.request("POST", os.getenv("WHATSAPP_ENDPOINT"), headers=headers, data=payload)
    print(res.json())
    return res.status_code == 200