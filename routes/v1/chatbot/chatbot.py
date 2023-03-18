from flask import Blueprint, request, jsonify
import os

chatbot_api = Blueprint("chatbot", __name__, url_prefix="/api/v1/chats")

@chatbot_api.route("/webhook", methods=["POST"])
def handleDialogFlow():
    print(request.get_json())
    if os.getenv("DIALOGFLOW_USERNAME") == request.authorization["username"] and os.getenv("DIALOGFLOW_PASSWORD") == request.authorization["password"]:
        return "authentication completed"
    return "authentication failed"