import urllib.parse

from app.data.graph_connector import GraphConnector
from app.schemas.input import PersonInput, ChildInput, FriendInput


def test_get_person_ancestors(client):
    GraphConnector().create_person(
        PersonInput(firstname="John", lastname="Doe", nickname="Johnny")
    )
    GraphConnector().create_person(PersonInput(firstname="Mom", lastname="Doe"))
    GraphConnector().create_child_relationship(
        "Mom Doe", ChildInput(child_name="John Doe")
    )
    GraphConnector().create_person(PersonInput(firstname="Grandma", lastname="Doe"))
    GraphConnector().create_child_relationship(
        "Grandma Doe", ChildInput(child_name="Mom Doe")
    )

    expected = {
        "people": [
            {
                "name": "Mom Doe",
                "nickname": None,
                "parent_of": [
                    {
                        "name": "John Doe",
                        "person_at": "http://localhost:8000/people/John%20Doe",
                    }
                ],
                "child_of": [
                    {
                        "name": "Grandma Doe",
                        "person_at": "http://localhost:8000/people/Grandma%20Doe",
                    }
                ],
                "friends_with": [],
                "firstname": "Mom",
                "lastname": "Doe",
                "person_at": "http://localhost:8000/people/Mom%20Doe",
                "ancestors_at": "http://localhost:8000/people/Mom%20Doe/ancestors",
            },
            {
                "name": "Grandma Doe",
                "nickname": None,
                "parent_of": [
                    {
                        "name": "Mom Doe",
                        "person_at": "http://localhost:8000/people/Mom%20Doe",
                    }
                ],
                "child_of": [],
                "friends_with": [],
                "firstname": "Grandma",
                "lastname": "Doe",
                "person_at": "http://localhost:8000/people/Grandma%20Doe",
                "ancestors_at": "http://localhost:8000/people/Grandma%20Doe/ancestors",
            },
        ]
    }
    response = client.get(f"/v0/people/{urllib.parse.quote('John Doe')}/ancestors")
    assert response.status_code == 200
    assert response.json() == expected


def test_get_person_ancestors_person_doesnt_exists(client):
    # TODO maybe we would prefer a 404, but that would require a pre-check in the API
    expected = {"people": []}
    response = client.get(f"/v0/people/{urllib.parse.quote('John Doe')}/ancestors")
    assert response.status_code == 200
    assert response.json() == expected


def test_get_person_family_friends(client):
    GraphConnector().create_person(
        PersonInput(firstname="John", lastname="Doe", nickname="Johnny")
    )
    GraphConnector().create_person(PersonInput(firstname="John", lastname="Friend"))
    GraphConnector().create_friend_relationship(
        "John Doe", FriendInput(friend_name="John Friend")
    )

    GraphConnector().create_person(PersonInput(firstname="Mom", lastname="Doe"))
    GraphConnector().create_child_relationship(
        "Mom Doe", ChildInput(child_name="John Doe")
    )
    GraphConnector().create_person(PersonInput(firstname="Mom", lastname="Friend"))
    GraphConnector().create_friend_relationship(
        "Mom Doe", FriendInput(friend_name="Mom Friend")
    )

    GraphConnector().create_person(PersonInput(firstname="Child", lastname="Doe"))
    GraphConnector().create_child_relationship(
        "John Doe", ChildInput(child_name="Child Doe")
    )
    GraphConnector().create_person(PersonInput(firstname="Child", lastname="Friend"))
    GraphConnector().create_friend_relationship(
        "Child Doe", FriendInput(friend_name="Child Friend")
    )

    expected = {
        "people": [
            {
                "name": "Child Friend",
                "nickname": None,
                "parent_of": [],
                "child_of": [],
                "friends_with": [
                    {
                        "name": "Child Doe",
                        "person_at": "http://localhost:8000/people/Child%20Doe",
                    }
                ],
                "firstname": "Child",
                "lastname": "Friend",
                "person_at": "http://localhost:8000/people/Child%20Friend",
                "ancestors_at": "http://localhost:8000/people/Child%20Friend/ancestors",
            },
            {
                "name": "Mom Friend",
                "nickname": None,
                "parent_of": [],
                "child_of": [],
                "friends_with": [
                    {
                        "name": "Mom Doe",
                        "person_at": "http://localhost:8000/people/Mom%20Doe",
                    }
                ],
                "firstname": "Mom",
                "lastname": "Friend",
                "person_at": "http://localhost:8000/people/Mom%20Friend",
                "ancestors_at": "http://localhost:8000/people/Mom%20Friend/ancestors",
            },
            {
                "name": "John Friend",
                "nickname": None,
                "parent_of": [],
                "child_of": [],
                "friends_with": [
                    {
                        "name": "John Doe",
                        "person_at": "http://localhost:8000/people/John%20Doe",
                    }
                ],
                "firstname": "John",
                "lastname": "Friend",
                "person_at": "http://localhost:8000/people/John%20Friend",
                "ancestors_at": "http://localhost:8000/people/John%20Friend/ancestors",
            },
        ]
    }

    response = client.get(f"/v0/people/{urllib.parse.quote('John Doe')}/family/friends")
    assert response.status_code == 200
    assert response.json() == expected


def test_get_person_family_friends_person_doesnt_exists(client):
    # TODO maybe we would prefer a 404, but that would require a pre-check in the API
    expected = {"people": []}
    response = client.get(f"/v0/people/{urllib.parse.quote('John Doe')}/family/friends")
    assert response.status_code == 200
    assert response.json() == expected
