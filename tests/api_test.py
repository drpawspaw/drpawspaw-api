from app import app
import pytest
import json

# Define test_client from the app
client = app.test_client()

# def test_signup():
#     print("Running - POST /api/auth/signup")
#     signup_rq = {
#         "email": "testuser@drpawspaw.com",
#         "password": "12345",
#         "name": "TestUser"
#     }
#     signup_res = client.post(
#         "/api/auth/signup",
#         data=json.dumps(signup_rq),
#         headers={"Content-Type": "application/json"}
#     )
#     assert signup_res.status_code == 201
#     if signup_res.status_code == 201:
#         json_sign_res = json.loads(signup_res.data.decode('utf-8'))
#         pytest.auth_id = json_sign_res['_id']

# def test_login():
#     print("Running - POST /api/auth/login")
#     login_rq = {
#         "username": "test@drpawspaw.com",
#         "password": "12345"
#     }
#     login_res = client.post(
#         "/api/auth/login",
#         data=json.dumps(login_rq),
#         headers={"Content-Type": "application/json"}
#     )
#     assert login_res.status_code == 200
#     if login_res.status_code == 200:
#         json_res = json.loads(login_res.data.decode('utf-8'))
#         access_token = json_res['access_token']

# def test_chat():
#     print("Running - POST /api/v1/chats")
#     message_rq_greet = {
#         "message": "Hi",
#         "session": "20191157"
#     }
#     mrg = client.post("/api/v1/chats",
#         data=json.dumps(message_rq_greet),
#         headers={"Content-Type": "application/json"}
#     )
#     assert mrg.status_code == 200

#     print("Running - POST /api/v1/chats - Test Case #1")
#     message_rq_limitation = {
#         "message": "My dog has bad fever and diarrhoea and running nose ?",
#         "session": "20191157"
#     }
#     mrl = client.post("/api/v1/chats",
#         data=json.dumps(message_rq_limitation),
#         headers={"Content-Type": "application/json"}
#     )
#     assert mrl.status_code == 200
#     mrl_res = json.loads(mrl.data.decode('utf-8'))
#     assert mrl_res['type'] == "LIMITATION"
#     assert mrl_res['treatments'] == ""
#     assert mrl_res['suggestions'] == []

#     print("Running - POST /api/v1/chats - Test Case #2")
#     message_rq_suggestion = {
#         "message": "My dog has been vomiting and has diarrhoea ?",
#         "session": "20191157"
#     }
#     mrs = client.post("/api/v1/chats",
#         data=json.dumps(message_rq_suggestion),
#         headers={"Content-Type": "application/json"}
#     )
#     assert mrs.status_code == 200
#     mrs_res = json.loads(mrs.data.decode('utf-8'))
#     assert mrs_res['type'] == "SUGGESTION"
#     assert mrs_res['treatments'] == ""
#     assert mrs_res['suggestions'] != []
    
#     print("Running - POST /api/v1/chats - Test Case #3")
#     message_rq_prediction = {
#         "message": "My dog has high fever and running nose ?",
#         "session": "20191157"
#     }
#     mrp = client.post("/api/v1/chats",
#         data=json.dumps(message_rq_prediction),
#         headers={"Content-Type": "application/json"}
#     )
#     assert mrp.status_code == 200
#     mrp_res = json.loads(mrp.data.decode('utf-8'))
#     assert mrp_res['type'] == "PREDICTION"
#     assert mrp_res['treatments'] != ""
#     assert mrp_res['suggestions'] == []

# def test_static_routes():
#     print("Running - GET /api/v1/static/vaccines")
#     response = client.get("/api/v1/static/vaccines")
#     json_res = json.loads(response.data.decode('utf-8'))
#     assert type(json_res) is list
#     assert response.status_code == 200

#     print("Running - GET /api/v1/static/treatments")
#     response = client.get("/api/v1/static/treatments")
#     json_res = json.loads(response.data.decode('utf-8'))
#     assert type(json_res) is list
#     assert response.status_code == 200

# Test cleanup - delete user accounts and pet accounts
# def test_cleanup():
#     if pytest.auth_id != "":
#         print("Running - DELETE /api/auth/deactivate/<id>")
#         endpoint = "/api/auth/deactivate/{id}".format(id=pytest.auth_id)
#         response = client.delete(endpoint)
#         assert response.status_code == 200