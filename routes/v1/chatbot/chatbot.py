from flask import Blueprint, request, jsonify, make_response
from google.cloud import dialogflow
from models.chat.handler import ChatSchema
from flask_cors import CORS
import os

chatbot_api = Blueprint("chatbot", __name__, url_prefix="/api/v1/chats")

@chatbot_api.route("/", methods=['POST'])
@cross_origin()
def dialogflow_detect_intent():
    req = ChatSchema().load(request.get_json())
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(os.getenv("DIALOGFLOW_PROJECT"), req['session'])
    text_input = dialogflow.TextInput(text=req['message'], language_code='en-US')
    query_input = dialogflow.QueryInput(text=text_input)
    result = session_client.detect_intent(request={"session": session, "query_input": query_input})

    # TODO - Handle disease part and update the dialogflow model

    response = {}
    response['query'] = result.query_result.query_text
    response['response'] = result.query_result.fulfillment_text
    response['intent'] = result.query_result.intent.display_name
    response['confidence'] = result.query_result.intent_detection_confidence
    return jsonify(response), 200