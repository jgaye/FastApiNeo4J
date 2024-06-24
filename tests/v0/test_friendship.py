import urllib.parse

from app.data.graph_connector import GraphConnector
from app.schemas.input import PersonInput, ChildInput, FriendInput


def test_post_person_friend(client):
    GraphConnector().create_person(
        PersonInput(firstname="John", lastname="Doe", nickname="Johnny")
    )
    GraphConnector().create_person(PersonInput(firstname="John", lastname="Friend"))

    expected = {
        "name": "John Doe",
        "nickname": "Johnny",
        "parent_of": [],
        "child_of": [],
        "friends_with": [
            {
                "name": "John Friend",
                "person_at": "http://localhost:8000/people/John%20Friend",
            }
        ],
        "firstname": "John",
        "lastname": "Doe",
        "person_at": "http://localhost:8000/people/John%20Doe",
        "ancestors_at": "http://localhost:8000/people/John%20Doe/ancestors",
    }
    response = client.post(
        f"/v0/people/{urllib.parse.quote('John Doe')}/friends",
        json={"friend_name": "John Friend"},
    )
    assert response.status_code == 200
    assert response.json() == expected


def test_post_person_friend_idempotent(client):
    # TODO Leaving this failing test on purpose
    GraphConnector().create_person(
        PersonInput(firstname="John", lastname="Doe", nickname="Johnny")
    )
    GraphConnector().create_person(PersonInput(firstname="John", lastname="Friend"))

    expected = {
        "name": "John Doe",
        "nickname": "Johnny",
        "parent_of": [],
        "child_of": [],
        "friends_with": [
            {
                "name": "John Friend",
                "person_at": "http://localhost:8000/people/John%20Friend",
            }
        ],
        "firstname": "John",
        "lastname": "Doe",
        "person_at": "http://localhost:8000/people/John%20Doe",
        "ancestors_at": "http://localhost:8000/people/John%20Doe/ancestors",
    }
    response1 = client.post(
        f"/v0/people/{urllib.parse.quote('John Doe')}/friends",
        json={"friend_name": "John Friend"},
    )
    response2 = client.post(
        f"/v0/people/{urllib.parse.quote('John Doe')}/friends",
        json={"friend_name": "John Friend"},
    )
    assert response2.status_code == 200
    assert response2.json() == expected


def test_post_person_friend_not_found(client):
    response = client.post(
        f"/v0/people/{urllib.parse.quote('John Doe')}/friends",
        json={"friend_name": "John Friend"},
    )
    assert response.status_code == 404


def test_delete_person_friend_relationship(client):
    GraphConnector().create_person(
        PersonInput(firstname="John", lastname="Doe", nickname="Johnny")
    )
    GraphConnector().create_person(PersonInput(firstname="John", lastname="Friend"))
    GraphConnector().create_friend_relationship(
        "John Doe", FriendInput(friend_name="John Friend")
    )

    response = client.delete(
        f"/v0/people/{urllib.parse.quote('John Doe')}/friends/{urllib.parse.quote('John Friend')}",
    )
    assert response.status_code == 204

    assert GraphConnector().fetch_person("John Friend")["friends_with"] == []
    assert GraphConnector().fetch_person("John Doe")["friends_with"] == []


def test_delete_person_friend_relationship_person_doesnt_exist(client):
    response = client.delete(
        f"/v0/people/{urllib.parse.quote('John Doe')}/friends/{urllib.parse.quote('John Friend')}",
    )
    assert response.status_code == 204
