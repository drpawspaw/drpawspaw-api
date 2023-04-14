from flask import Blueprint, request, jsonify, make_response
from google.cloud import dialogflow
from models.chat.handler import ChatSchema
from flask_cors import CORS, cross_origin
from rdflib import Graph, Namespace, Literal, RDF, URIRef
from linker.ned import entity_linker
from routes import database_conn

import os

# define mongodb collections
treatment_collection = database_conn['treatments']

chatbot_api = Blueprint("chatbot", __name__)
decision_request_intent = "projects/drpawpaw-20191157/agent/intents/11a8f35f-f36c-44ab-b6a0-fd9fb69e99e4"

def handle_chat(message, session):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(os.getenv("DIALOGFLOW_PROJECT"), session)
    text_input = dialogflow.TextInput(text=message, language_code='en-US')
    query_input = dialogflow.QueryInput(text=text_input)

    # Get the intent detection and generate output from the DialogFlow
    result = session_client.detect_intent(request={"session": session, "query_input": query_input})

    # Create response object
    response = {}
    response['query'] = result.query_result.query_text
    response['response'] = result.query_result.fulfillment_text
    response['intent'] = result.query_result.intent.display_name
    response['confidence'] = result.query_result.intent_detection_confidence
    response['type'] = "GENERAL"
    response['suggestions'] = [] # By default this will be an empty array, To keep the response entity constant,
    response['treatments'] = ""

    # If the intent recognize as "PREDICTION REQUEST", then pass the message to entity_linker for the prediction
    if result.query_result.intent.name == decision_request_intent:
        pred_resp = entity_linker(result.query_result.query_text)
        response['type'] = pred_resp['result_type']

        # Limitation 
        if pred_resp['result_type'] == 'LIMITATION':
            response['type'] = "LIMITATION"
            response['response'] = "Based on the information that we have, we are unable to determine what disease it is because we do not have the necessary expertise."
        # Suggestion - In here, user will get list of symptoms for the prediction.
        elif pred_resp['result_type'] == 'SUGGESTION':
            response['type'] = "SUGGESTION"
            response['response'] = "According to the information that has been provided to us, we are unable to identify the specific disease; however, it may be {diseases}. It would be helpful to perform a more accurate prediction if you could provide more symptoms out of the following symptoms.".format(diseases= ", ".join(pred_resp['predicted_disease']))
            response['suggestions'] = pred_resp['symptom_suggestions']
        # Prediction
        else:
            response['response'] = "We are able to predict the disease as {disease}".format(disease= pred_resp['predicted_disease'])
            # Get the treatment from treatments collection
            for treat in treatment_collection.find():
                if treat['disease'].lower() == pred_resp['predicted_disease'].lower():
                    response['treatments'] = "Here are the treatments for {disease} ".format(disease=pred_resp['predicted_disease']) + " is " + treat['treatments'] + " " + " (Source: {source}).".format(source= treat['source'])
            response['type'] = "PREDICTION"
    return response

@chatbot_api.route("/api/v1/chats", methods=['POST'])
@cross_origin()
def dialogflow_detect_intent():
    req = ChatSchema().load(request.get_json())
    response = handle_chat(req['message'], req['session'])
    return jsonify(response), 200

@chatbot_api.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response