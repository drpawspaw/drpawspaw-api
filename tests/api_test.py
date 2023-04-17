from app import app
import pytest
import json

# Define test_client from the app
client = app.test_client()

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
        access_token = json_res['access_token']

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

def test_cleanup():
    if pytest.auth_id != "":
        print("Running - DELETE /api/auth/deactivate/<id>")
        endpoint = "/api/auth/deactivate/{id}".format(id=pytest.auth_id)
        response = client.delete(endpoint)
        assert response.status_code == 200