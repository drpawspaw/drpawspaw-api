from app import app
import pytest
import json

# Define test_client from the app
client = app.test_client()

@pytest.mark.order1
def test_signup():
    print("Running - POST /api/auth/signup")
    signup_rq = {
        "email": "testuser@drpawspaw.com",
        "password": "12345",
        "name": "TestUser"
    }
    signup_res = client.post(
        "/api/auth/signup",
        data=json.dumps(signup_rq),
        headers={"Content-Type": "application/json"}
    )
    assert signup_res.status_code == 201
    if signup_res.status_code == 201:
        json_sign_res = json.loads(signup_res.data.decode('utf-8'))
        pytest.auth_id = json_sign_res['_id']

@pytest.mark.order2
def test_login():
    print("Running - POST /api/auth/login")
    login_rq = {
        "username": "test@drpawspaw.com",
        "password": "12345"
    }
    login_res = client.post(
        "/api/auth/login",
        data=json.dumps(login_rq),
        headers={"Content-Type": "application/json"}
    )
    assert login_res.status_code == 200
    if login_res.status_code == 200:
        json_res = json.loads(login_res.data.decode('utf-8'))
        pytest.access_token = json_res['access_token']

def test_chat():
    print("Running - POST /api/v1/chats")
    message_rq_greet = {
        "message": "Hi",
        "session": "20191157"
    }
    mrg = client.post("/api/v1/chats",
        data=json.dumps(message_rq_greet),
        headers={"Content-Type": "application/json"}
    )
    assert mrg.status_code == 200

    print("Running - POST /api/v1/chats - Test Case #1")
    message_rq_limitation = {
        "message": "My dog has bad fever and diarrhoea and running nose ?",
        "session": "20191157"
    }
    mrl = client.post("/api/v1/chats",
        data=json.dumps(message_rq_limitation),
        headers={"Content-Type": "application/json"}
    )
    assert mrl.status_code == 200
    mrl_res = json.loads(mrl.data.decode('utf-8'))
    assert mrl_res['type'] == "LIMITATION"
    assert mrl_res['treatments'] == ""
    assert mrl_res['suggestions'] == []
    print("Running - POST /api/v1/chats - Test Case #2")
    message_rq_suggestion = {
        "message": "My dog has been vomiting and has diarrhoea ?",
        "session": "20191157"
    }
    mrs = client.post("/api/v1/chats",
        data=json.dumps(message_rq_suggestion),
        headers={"Content-Type": "application/json"}
    )
    assert mrs.status_code == 200
    mrs_res = json.loads(mrs.data.decode('utf-8'))
    assert mrs_res['type'] == "SUGGESTION"
    assert mrs_res['treatments'] == ""
    assert mrs_res['suggestions'] != []
    
    print("Running - POST /api/v1/chats - Test Case #3")
    message_rq_prediction = {
        "message": "My dog has high fever and running nose ?",
        "session": "20191157"
    }
    mrp = client.post("/api/v1/chats",
        data=json.dumps(message_rq_prediction),
        headers={"Content-Type": "application/json"}
    )
    assert mrp.status_code == 200
    mrp_res = json.loads(mrp.data.decode('utf-8'))
    assert mrp_res['type'] == "PREDICTION"
    assert mrp_res['treatments'] != ""
    assert mrp_res['suggestions'] == []

def test_pets():
    print("Running - POST /api/v1/pets")
    create_req = {
        "name": "Tommy",
        "birthdate": "2023-03-06T00:00:00.000+05:30",
        "lastVaccinationDate": "2023-04-17T08:29:54.770+05:30",
        "lastVaccination": "Rabies + Parvo",
        "category": "dog",
        "bread": "Shitzu",
        "owner": pytest.auth_id,
        "isNotificationEnabled": False
    }
    petr = client.post("/api/v1/pets",
        data=json.dumps(create_req),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {token}".format(token=pytest.access_token)
        }
    )
    assert petr.status_code == 201
    mrp_res = json.loads(petr.data.decode('utf-8'))
    
    print("Running - GET /api/v1/pets?owner=<id>")
    pets = client.get("/api/v1/pets?owner={id}".format(id=pytest.auth_id),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {token}".format(token=pytest.access_token)
            }
    )
    assert pets.status_code == 200
    pets_res = json.loads(pets.data.decode('utf-8'))
    if len(pets_res) != 0:
        pytest.pet_id = pets_res[0]['_id']

    if pytest.pet_id != "":
        print("Running - PUT /api/v1/pets/<id>")
        update_req = {
            "name": "TommyUpdated",
            "birthdate": "2023-03-06T00:00:00.000+05:30",
            "lastVaccinationDate": "2023-04-17T08:29:54.770+05:30",
            "lastVaccination": "Rabies + Parvo",
            "category": "dog",
            "bread": "Shitzu",
            "owner": pytest.auth_id,
            "isNotificationEnabled": False
        }
        petr = client.put("/api/v1/pets/{id}".format(id=pytest.pet_id),
            data=json.dumps(update_req),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {token}".format(token=pytest.access_token)
            }
        )
        assert petr.status_code == 200
        curr_pet = client.get("/api/v1/pets?id={id}".format(id=pytest.pet_id),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {token}".format(token=pytest.access_token)
            }
        )
        petr_res = json.loads(curr_pet.data.decode('utf-8'))
        assert petr_res['name'] == "TommyUpdated"

def test_static_routes():
    print("Running - GET /api/v1/static/vaccines")
    response = client.get("/api/v1/static/vaccines")
    json_res = json.loads(response.data.decode('utf-8'))
    assert type(json_res) is list
    assert response.status_code == 200

    print("Running - GET /api/v1/static/treatments")
    response = client.get("/api/v1/static/treatments")
    json_res = json.loads(response.data.decode('utf-8'))
    assert type(json_res) is list
    assert response.status_code == 200

# Test cleanup - delete user accounts and pet accounts
@pytest.mark.last
def test_cleanup():
    if pytest.auth_id != "":
        print("Running - DELETE /api/auth/deactivate/<id>")
        endpoint = "/api/auth/deactivate/{id}".format(id=pytest.auth_id)
        response = client.delete(endpoint)
        assert response.status_code == 200
        
        if pytest.pet_id != "":
            print("Running - DELETE /api/v1/pets/<id>")
            endpoint = "/api/v1/pets/{id}".format(id=pytest.pet_id)
            response = client.delete(endpoint, 
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer {token}".format(token=pytest.access_token)
                }
            )
            assert response.status_code == 200