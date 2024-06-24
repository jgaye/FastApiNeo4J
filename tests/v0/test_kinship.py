import urllib.parse

from app.data.graph_connector import GraphConnector
from app.schemas.input import PersonInput, ChildInput


def test_post_person_child(client):
    GraphConnector().create_person(
        PersonInput(firstname="John", lastname="Doe", nickname="Johnny")
    )
    GraphConnector().create_person(PersonInput(firstname="Mom", lastname="Doe"))

    expected = {
        "name": "Mom Doe",
        "nickname": None,
        "parent_of": [
            {
                "name": "John Doe",
                "person_at": "http://localhost:8000/people/John%20Doe",
            }
        ],
        "child_of": [],
        "friends_with": [],
        "firstname": "Mom",
        "lastname": "Doe",
        "person_at": "http://localhost:8000/people/Mom%20Doe",
        "ancestors_at": "http://localhost:8000/people/Mom%20Doe/ancestors",
    }
    response = client.post(
        f"/v0/people/{urllib.parse.quote('Mom Doe')}/children",
        json={"child_name": "John Doe"},
    )
    assert response.status_code == 200
    assert response.json() == expected


def test_post_person_child_idempotent(client):
    # TODO Leaving this failing test on purpose
    GraphConnector().create_person(
        PersonInput(firstname="John", lastname="Doe", nickname="Johnny")
    )
    GraphConnector().create_person(PersonInput(firstname="Mom", lastname="Doe"))

    expected = {
        "name": "Mom Doe",
        "nickname": None,
        "parent_of": [
            {
                "name": "John Doe",
                "person_at": "http://localhost:8000/people/John%20Doe",
            }
        ],
        "child_of": [],
        "friends_with": [],
        "firstname": "Mom",
        "lastname": "Doe",
        "person_at": "http://localhost:8000/people/Mom%20Doe",
        "ancestors_at": "http://localhost:8000/people/Mom%20Doe/ancestors",
    }
    response1 = client.post(
        f"/v0/people/{urllib.parse.quote('Mom Doe')}/children",
        json={"child_name": "John Doe"},
    )
    response2 = client.post(
        f"/v0/people/{urllib.parse.quote('Mom Doe')}/children",
        json={"child_name": "John Doe"},
    )
    assert response2.status_code == 200
    assert response2.json() == expected


def test_post_person_child_not_found(client):
    response = client.post(
        f"/v0/people/{urllib.parse.quote('Mom Doe')}/children",
        json={"child_name": "John Doe"},
    )
    assert response.status_code == 404


def test_delete_person_child_relationship(client):
    GraphConnector().create_person(
        PersonInput(firstname="John", lastname="Doe", nickname="Johnny")
    )
    GraphConnector().create_person(PersonInput(firstname="Mom", lastname="Doe"))
    GraphConnector().create_child_relationship(
        "Mom Doe", ChildInput(child_name="John Doe")
    )

    response = client.delete(
        f"/v0/people/{urllib.parse.quote('Mom Doe')}/children/{urllib.parse.quote('John Doe')}",
    )
    assert response.status_code == 204

    assert GraphConnector().fetch_person("Mom Doe")["parent_of"] == []
    assert GraphConnector().fetch_person("John Doe")["child_of"] == []


def test_delete_person_child_relationship_person_doesnt_exist(client):
    response = client.delete(
        f"/v0/people/{urllib.parse.quote('Mom Doe')}/children/{urllib.parse.quote('John Doe')}",
    )
    assert response.status_code == 204
