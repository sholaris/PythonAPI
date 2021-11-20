from typing import List
import pytest
from app import schemas
from tests.conftest import authorized_client, test_user

# ________________TESTING GET ROUTES________________ #

def test_get_all_posts(authorized_client, create_posts):
    def validate(post):
        return schemas.PostVote(**post)

    res = authorized_client.get("/posts/")
    post_schemas = map(validate, res.json())
    posts_list = list(post_schemas)

    assert len(res.json()) == len(create_posts)
    assert posts_list[0].Post.id == create_posts[0].id
    assert res.status_code == 200

def test_unauthorized_user_get_all_posts(client, create_posts):
    res = client.get("/posts/")

    assert res.status_code == 401

def test_unauthorized_user_get_one_post(client, create_posts):
    res = client.get(f"/posts/{create_posts[0].id}")

    assert res.status_code == 401

def test_get_one_post_not_exist(authorized_client, create_posts):
    res = authorized_client.get(f"/posts/123")

    assert res.status_code == 404

def test_get_one_post(authorized_client, create_posts, test_user):
    res = authorized_client.get(f"/posts/{create_posts[0].id}")
    post = schemas.PostVote(**res.json())
    
    assert post.Post.id == create_posts[0].id
    assert post.Post.title == create_posts[0].title
    assert post.Post.content == create_posts[0].content
    assert post.Post.user_id == test_user['id']
    assert res.status_code == 200

# ________________TESTING POST ROUTES________________ #

@pytest.mark.parametrize("title, content, published", [
    ("awesome new title", "Awesome new content", True),
    ("my favourite mountains", "I love the Tatras ", False),
    ("best holiday destinations", "You should absolutly visit Italy", True)
])
def test_create_posts(authorized_client, create_posts, test_user, title, content, published):
    res = authorized_client.post("/posts/", json={"title": title, "content": content, "published": published})

    new_post = schemas.Post(**res.json())

    assert res.status_code == 201
    assert new_post.title == title
    assert new_post.content == content
    assert new_post.published == published
    assert new_post.user_id == test_user['id']

def test_create_post_default_published_true(authorized_client, create_posts, test_user):
    res = authorized_client.post("/posts/", json={"title": "some title", "content": "some content"})

    new_post = schemas.Post(**res.json())

    assert res.status_code == 201
    assert new_post.title == "some title"
    assert new_post.content == "some content"
    assert new_post.published == True
    assert new_post.user_id == test_user['id']

def test_unauthorized_user_create_post(client):
    res = client.post("/posts/", json={"title": "some title", "content": "some content"})

    assert res.status_code == 401

# ________________TESTING DELETE ROUTES________________ #

def test_unauthorized_user_delete_post(client, test_user, create_posts):
    res = client.delete(f"/posts/{create_posts[0].id}")

    assert res.status_code == 401

def test_delete_post_success(authorized_client, test_user, create_posts):
    res = authorized_client.delete(f"/posts/{create_posts[0].id}")

    assert res.status_code == 204

def test_delete_post_not_exist(authorized_client, test_user, create_posts):
    res = authorized_client.delete(f"/posts/123")

    assert res.status_code == 404

def test_delete_other_user_post(authorized_client, test_user, create_posts):
    res = authorized_client.delete(f"/posts/{create_posts[3].id}")

    assert res.status_code == 403
    assert res.json().get('detail') == 'Not authorized to perform requested action'

# ________________TESTING UPDATE ROUTES________________ #
def test_update_post(authorized_client, test_user, create_posts):
    data = {
        "title": "updated title",
        "content": "updated content"
    }

    res = authorized_client.put(f"/posts/{create_posts[0].id}", json=data)
    updated_post = schemas.Post(**res.json())

    assert res.status_code == 200
    assert updated_post.title == data['title']
    assert updated_post.content == data['content']

def test_update_other_user_post(authorized_client, test_user, test_user_second, create_posts):
    data = {
        "title": "updated title",
        "content": "updated content"
    }

    res = authorized_client.put(f"/posts/{create_posts[3].id}", json=data)

    assert res.status_code == 403
    assert res.json().get('detail') == 'Not authorized to perform requested action'

def test_unauthorized_user_update_post(client, test_user, create_posts):
    res = client.put(f"/posts/{create_posts[0].id}")

    assert res.status_code == 401
    assert res.json().get('detail') == f'Not authenticated'

def test_update_post_not_exist(authorized_client, test_user, create_posts):
    data = {
        "title": "updated title",
        "content": "updated content"
    }

    res = authorized_client.put(f"/posts/123", json=data)

    assert res.status_code == 404
    assert res.json().get('detail') == f'Post with id 123 does not exist!'