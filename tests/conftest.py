from fastapi.testclient import TestClient
import pytest
from app.main import app
from app.database import Base, get_db
from app.config import settings
from app.oauth2 import create_access_token
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_hostname}:{settings.db_port}/{settings.db_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestinSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestinSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    # Dependency function that create and return new user
    user_data = {
        "email": "test_user@gmail.com", 
        "password": "password123"
    }
    res = client.post("/users/", json=user_data)
    new_user = res.json()
    new_user['password'] = user_data["password"]
    assert res.status_code == 201
    return new_user


@pytest.fixture
def test_user_second(client):
    # Dependency function that create and return new user
    user_data = {
        "email": "test_user2@gmail.com", 
        "password": "password321"
    }
    res = client.post("/users/", json=user_data)
    new_user = res.json()
    new_user['password'] = user_data["password"]
    assert res.status_code == 201
    return new_user


@pytest.fixture()
def token(test_user):
    return create_access_token({"user_id": test_user['id']})


@pytest.fixture()
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f'Bearer {token}'
    }

    return client


@pytest.fixture()
def create_posts(test_user, test_user_second, session):
    posts_data = [
        {
            "title": "1st title",
            "content": "content of the 1st post",
            "user_id": test_user['id']
        },
        {
            "title": "2nd title",
            "content": "content of the 2nd post",
            "user_id": test_user['id']
        },
        {
            "title": "3rd title",
            "content": "content of the 3rd post",
            "user_id": test_user['id']
        },
        {
            "title": "some title",
            "content": "some content of the post",
            "user_id": test_user_second['id']
        }]

    def create_post_model(post):
        return models.Post(**post)

    post_models = list(map(create_post_model, posts_data))

    session.add_all(post_models)
    session.commit()
    
    return session.query(models.Post).all()

