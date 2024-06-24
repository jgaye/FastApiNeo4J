import urllib.parse

import pytest

from app.data.graph_connector import GraphConnector, PersonNotFound
from app.schemas.input import PersonInput, ChildInput, FriendInput


def test_list_people(client):
    # initiate a person in the empty DB
    GraphConnector().create_person(
        PersonInput(firstname="John", lastname="Doe", nickname="Johnny")
    )

    # We should retrieve that person
    expected = {
        "people": [
            {
                "name": "John Doe",
                "nickname": "Johnny",
                "parent_of": [],
                "child_of": [],
                "friends_with": [],
                "firstname": "John",
                "lastname": "Doe",
                "person_at": "http://localhost:8000/people/John%20Doe",
                "ancestors_at": "http://localhost:8000/people/John%20Doe/ancestors",
            }
        ]
    }
    response = client.get("/v0/people")
    assert response.status_code == 200
    assert response.json() == expected


def test_list_people_empty(client):
    expected = {"people": []}
    response = client.get("/v0/people")
    assert response.status_code == 200
    assert response.json() == expected


def test_post_person(client):
    expected = {
        "name": "John Doe",
        "nickname": "Johnny",
        "parent_of": [],
        "child_of": [],
        "friends_with": [],
        "firstname": "John",
        "lastname": "Doe",
        "person_at": "http://localhost:8000/people/John%20Doe",
        "ancestors_at": "http://localhost:8000/people/John%20Doe/ancestors",
    }
    response = client.post(
        "/v0/people",
        json={"firstname": "John", "lastname": "Doe", "nickname": "Johnny"},
    )
    assert response.status_code == 200
    assert response.json() == expected


def test_get_person(client):
    # initiate a person in the empty DB
    GraphConnector().create_person(
        PersonInput(firstname="John", lastname="Doe", nickname="Johnny")
    )

    # We should retrieve that person
    expected = {
        "name": "John Doe",
        "nickname": "Johnny",
        "parent_of": [],
        "child_of": [],
        "friends_with": [],
        "firstname": "John",
        "lastname": "Doe",
        "person_at": "http://localhost:8000/people/John%20Doe",
        "ancestors_at": "http://localhost:8000/people/John%20Doe/ancestors",
    }
    response = client.get(f"/v0/people/{urllib.parse.quote('John Doe')}")
    assert response.status_code == 200
    assert response.json() == expected


def test_get_person_with_relationships(client):
    # initiate a person in the empty DB, and a parent, friend and child
    GraphConnector().create_person(
        PersonInput(firstname="John", lastname="Doe", nickname="Johnny")
    )
    GraphConnector().create_person(PersonInput(firstname="Mom", lastname="Doe"))
    GraphConnector().create_child_relationship(
        "Mom Doe", ChildInput(child_name="John Doe")
    )
    GraphConnector().create_person(PersonInput(firstname="Child", lastname="Doe"))
    GraphConnector().create_child_relationship(
        "John Doe", ChildInput(child_name="Child Doe")
    )
    GraphConnector().create_person(PersonInput(firstname="Friend", lastname="Doe"))
    GraphConnector().create_friend_relationship(
        "John Doe", FriendInput(friend_name="Friend Doe")
    )

    # We should retrieve that person with those relationships
    expected = {
        "name": "John Doe",
        "nickname": "Johnny",
        "parent_of": [
            {
                "name": "Child Doe",
                "person_at": "http://localhost:8000/people/Child%20Doe",
            }
        ],
        "child_of": [
            {"name": "Mom Doe", "person_at": "http://localhost:8000/people/Mom%20Doe"}
        ],
        "friends_with": [
            {
                "name": "Friend Doe",
                "person_at": "http://localhost:8000/people/Friend%20Doe",
            }
        ],
        "firstname": "John",
        "lastname": "Doe",
        "person_at": "http://localhost:8000/people/John%20Doe",
        "ancestors_at": "http://localhost:8000/people/John%20Doe/ancestors",
    }
    response = client.get(f"/v0/people/{urllib.parse.quote('John Doe')}")
    assert response.status_code == 200
    assert response.json() == expected


def test_get_person_not_found(client):
    response = client.get("/v0/people/JojoLasticot")
    assert response.status_code == 404


def test_put_person(client):
    GraphConnector().create_person(
        PersonInput(firstname="John", lastname="Doe", nickname="Johnny")
    )
    expected = {
        "name": "Jon Dow",
        "nickname": "Jojo",
        "parent_of": [],
        "child_of": [],
        "friends_with": [],
        "firstname": "Jon",
        "lastname": "Dow",
        "person_at": "http://localhost:8000/people/Jon%20Dow",
        "ancestors_at": "http://localhost:8000/people/Jon%20Dow/ancestors",
    }
    response = client.put(
        f"/v0/people/{urllib.parse.quote('John Doe')}",
        json={"firstname": "Jon", "lastname": "Dow", "nickname": "Jojo"},
    )
    assert response.status_code == 200
    assert response.json() == expected


def test_put_person_not_found(client):
    response = client.put(
        f"/v0/people/{urllib.parse.quote('John Doe')}",
        json={"firstname": "Jon", "lastname": "Dow", "nickname": "Jojo"},
    )
    assert response.status_code == 404


def test_delete_person(client):
    GraphConnector().create_person(
        PersonInput(firstname="John", lastname="Doe", nickname="Johnny")
    )
    response = client.delete(f"/v0/people/{urllib.parse.quote('John Doe')}")
    assert response.status_code == 204
    with pytest.raises(PersonNotFound):
        GraphConnector().fetch_person("John Doe")


def test_delete_person_not_found(client):
    response = client.delete("/v0/people/JojoLasticot")
    assert response.status_code == 204
