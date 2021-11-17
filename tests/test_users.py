from app import schemas
from app.config import settings
from jose import jwt
import pytest


def test_create_user(client):
    res = client.post('/users/', json={"email": "test_email@gmail.com", "password": "password123"})

    new_user = schemas.User(**res.json())

    assert new_user.email == "test_email@gmail.com"
    assert res.status_code == 201

def test_login_user(client, test_user):
    res = client.post('/login', data={"username": test_user['email'], "password": test_user['password']})
    
    # Validation with use of pydentic schema 
    login_res = schemas.Token(**res.json())

    # Decoding access token
    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=[settings.algorithm])
    id = payload.get("user_id")

    assert id == test_user['id']
    assert login_res.token_type == 'Bearer'
    assert res.status_code == 200
    
@pytest.mark.parametrize('email, password, status_code', [
    ('wrongEmail@gmail.com','password123', 403),
    ('test_user@gmail.com','password123', 403),
    ('wrongEmail@gmail.com','wrongPassword', 403),
    (None, 'password123', 422),
    ('test_user@gmail.com', None, 422)
])
def test_incorrect_login_user(client, email, password, status_code):
    res = client.post("/login", data={"username": email, "password": password})

    assert res.status_code == status_code
    if email and password:
        assert res.json().get('detail') == 'Invalid Credentials'