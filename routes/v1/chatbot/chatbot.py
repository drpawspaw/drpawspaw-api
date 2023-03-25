from flask import Blueprint, request, jsonify, make_response
from google.cloud import dialogflow
from models.chat.handler import ChatSchema
from flask_cors import CORS, cross_origin
from rdflib import Graph, Namespace, Literal, RDF, URIRef
# from linker.ned import entity_linker

import os

chatbot_api = Blueprint("chatbot", __name__, url_prefix="/api/v1/chats")
decision_request_intent = "projects/drpawpaw-20191157/agent/intents/11a8f35f-f36c-44ab-b6a0-fd9fb69e99e4"

@chatbot_api.route("/", methods=['POST'])
@cross_origin()
def dialogflow_detect_intent():
    req = ChatSchema().load(request.get_json())
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(os.getenv("DIALOGFLOW_PROJECT"), req['session'])
    text_input = dialogflow.TextInput(text=req['message'], language_code='en-US')
    query_input = dialogflow.QueryInput(text=text_input)

    # Get the intent detection and generate output from the DialogFlow
    result = session_client.detect_intent(request={"session": session, "query_input": query_input})

    response = {}
    response['query'] = result.query_result.query_text
    response['response'] = result.query_result.fulfillment_text
    response['intent'] = result.query_result.intent.display_name
    response['confidence'] = result.query_result.intent_detection_confidence
    response['type'] = "GENERAL"
    response['suggestions'] = [] # By default this will be an empty array, To keep the response entity constant, 

    # If the intent recognize as "PREDICTION REQUEST", then pass the message to entity_linker for the prediction
    # if result.query_result.intent.name == decision_request_intent:
    #     pred_resp = entity_linker(result.query_result.query_text)
    #     response['type'] = pred_resp['result_type']

    #     # Limitation 
    #     if pred_resp['result_type'] == 'LIMITATION':
    #         response['type'] = "LIMITATION"
    #         response['response'] = "We don't have the knowledge to figure out what disease it is based on the information we have."
    #     # Suggestion - In here, user will get list of symptoms for the prediction.
    #     elif pred_resp['result_type'] == 'SUGGESTION':
    #         response['type'] = "SUGGESTION"
    #         response['response'] = "According to the provided information we are not able to identify extact disease, But it may be {diseases}. If you can provide more symptoms out of follwoing systom, that would be help to perform the prediction more accurate.".format(diseases= ", ".join(pred_resp['predicted_disease']))
    #         response['suggestions'] = pred_resp['symptom_suggestions']
    #     # Prediction
    #     else:
    #         response['response'] = "We are able to predict the disease as {disease}".format(disease= pred_resp['predicted_disease'])
    #         response['type'] = "PREDICTION"

    return jsonify(response), 200