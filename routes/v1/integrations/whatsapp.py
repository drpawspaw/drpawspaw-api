from flask import Blueprint, request, jsonify
from flask_cors import CORS, cross_origin
from models.integrations.handler import WhatsAppPayloadSchema
from routes.v1.chatbot.chatbot import handle_chat
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
        user_message = req_body['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        user_number = req_body['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
        print("response: ",handle_chat(user_message, user_number))
        return {}, 200