from app import schemas
import pytest

def test_add_vote_success(authorized_client, create_posts):
    res = authorized_client.post("/vote/", json={"post_id": create_posts[1].id, "dir": 1})

    assert res.status_code == 201
    assert res.json().get('message') == 'vote succesfully added'

def test_add_vote_fail(authorized_client, create_posts, create_vote, test_user):
    res = authorized_client.post("/vote/", json={"post_id": create_posts[1].id, "dir": 1})

    assert res.status_code == 409
    assert res.json().get('detail') == f"user {test_user['id']} has already voted on post {create_posts[1].id}"

def test_vote_not_existing_post(authorized_client, create_posts):
    res = authorized_client.post("/vote/", json={"post_id": 20000, "dir": 1})

    assert res.status_code == 404
    assert res.json().get('detail') == f'post with id {20000} does not exist'

def test_delete_not_existing_vote(authorized_client, create_posts):
    res = authorized_client.post("/vote/", json={"post_id": create_posts[1].id, "dir": 0})

    assert res.status_code == 404
    assert res.json().get('detail') == 'vote does not exist'

def test_unauthorized_user_vote(client, create_posts):
    res = client.post("/vote/", json={"post_id": create_posts[1].id, "dir": 1})

    assert res.status_code == 401
    assert res.json().get('detail') == 'Not authenticated'
