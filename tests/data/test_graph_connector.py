from unittest.mock import patch

import pytest

from app.data.graph_connector import GraphConnector, PersonNotFound
from app.schemas.input import PersonInput, ChildInput, FriendInput

empty = []
two_people = [
    {"person": {"name": "John Doe", "nickname": "Johnny"}},
    {
        "person": {
            "name": "Jeanne Doe",
        }
    },
]
friends = [{"friend.name": "My Friend"}]
parents = [{"parent.name": "My Parent"}]
children = [{"child.name": "My Child"}]


@patch.object(
    GraphConnector,
    "fetch_friends_parents_children",
    return_value=(friends, parents, children),
)
def test_unpack_person(mock_fetch_friends_parents_children):
    expected = {
        "name": "John Doe",
        "nickname": "Johnny",
        "parent_of": [{"name": "My Child"}],
        "child_of": [{"name": "My Parent"}],
        "friends_with": [{"name": "My Friend"}],
    }
    assert GraphConnector().unpack_person(two_people[0]["person"]) == expected
    assert mock_fetch_friends_parents_children.call_count == 1


@patch.object(GraphConnector, "run_query", return_value=two_people)
@patch.object(
    GraphConnector,
    "fetch_friends_parents_children",
    return_value=(friends, parents, children),
)
def test_list_people(mock_fetch_friends_parents_children, mock_run_query):
    expected = [
        {
            "name": "John Doe",
            "nickname": "Johnny",
            "parent_of": [{"name": "My Child"}],
            "child_of": [{"name": "My Parent"}],
            "friends_with": [{"name": "My Friend"}],
        },
        {
            "name": "Jeanne Doe",
            "parent_of": [{"name": "My Child"}],
            "child_of": [{"name": "My Parent"}],
            "friends_with": [{"name": "My Friend"}],
        },
    ]
    assert GraphConnector().list_people() == expected
    assert mock_run_query.call_count == 1
    assert mock_fetch_friends_parents_children.call_count == 2


@patch.object(GraphConnector, "run_query", return_value=two_people)
@patch.object(
    GraphConnector, "fetch_friends_parents_children", return_value=(empty, empty, empty)
)
def test_list_people_with_no_friends_or_family(
    mock_fetch_friends_parents_children, mock_run_query
):
    expected = [
        {
            "name": "John Doe",
            "nickname": "Johnny",
            "parent_of": [],
            "child_of": [],
            "friends_with": [],
        },
        {
            "name": "Jeanne Doe",
            "parent_of": [],
            "child_of": [],
            "friends_with": [],
        },
    ]
    assert GraphConnector().list_people() == expected
    assert mock_run_query.call_count == 1
    assert mock_fetch_friends_parents_children.call_count == 2


@patch.object(GraphConnector, "run_query", return_value=empty)
def test_list_people_empty(mock_run_query):
    expected = []
    assert GraphConnector().list_people() == expected
    assert mock_run_query.call_count == 1


@patch.object(GraphConnector, "run_query", return_value=[two_people[0]])
@patch.object(
    GraphConnector,
    "fetch_friends_parents_children",
    return_value=(friends, parents, children),
)
def test_fetch_person(mock_fetch_friends_parents_children, mock_run_query):
    expected = {
        "name": "John Doe",
        "nickname": "Johnny",
        "parent_of": [{"name": "My Child"}],
        "child_of": [{"name": "My Parent"}],
        "friends_with": [{"name": "My Friend"}],
    }
    assert GraphConnector().fetch_person(two_people[0]["person"]["name"]) == expected
    assert mock_run_query.call_count == 1
    assert mock_fetch_friends_parents_children.call_count == 1


@patch.object(GraphConnector, "run_query", return_value=empty)
def test_fetch_person_not_found(mock_run_query):
    with pytest.raises(PersonNotFound):
        GraphConnector().fetch_person(two_people[0]["person"]["name"])


@patch.object(GraphConnector, "run_query", return_value=two_people)
@patch.object(
    GraphConnector,
    "fetch_friends_parents_children",
    return_value=(friends, parents, children),
)
def test_fetch_person_ancestors(mock_fetch_friends_parents_children, mock_run_query):
    expected = [
        {
            "name": "John Doe",
            "nickname": "Johnny",
            "parent_of": [{"name": "My Child"}],
            "child_of": [{"name": "My Parent"}],
            "friends_with": [{"name": "My Friend"}],
        },
        {
            "name": "Jeanne Doe",
            "parent_of": [{"name": "My Child"}],
            "child_of": [{"name": "My Parent"}],
            "friends_with": [{"name": "My Friend"}],
        },
    ]
    assert (
        GraphConnector().fetch_person_ancestors(two_people[0]["person"]["name"])
        == expected
    )
    assert mock_run_query.call_count == 1
    assert mock_fetch_friends_parents_children.call_count == 2


@patch.object(GraphConnector, "run_query", return_value=empty)
def test_fetch_person_ancestors_empty(mock_run_query):
    expected = []
    assert (
        GraphConnector().fetch_person_ancestors(two_people[0]["person"]["name"])
        == expected
    )
    assert mock_run_query.call_count == 1


@patch.object(GraphConnector, "run_query", return_value=two_people)
@patch.object(
    GraphConnector,
    "fetch_friends_parents_children",
    return_value=(friends, parents, children),
)
def test_fetch_person_family_friends(
    mock_fetch_friends_parents_children, mock_run_query
):
    expected = [
        {
            "name": "John Doe",
            "nickname": "Johnny",
            "parent_of": [{"name": "My Child"}],
            "child_of": [{"name": "My Parent"}],
            "friends_with": [{"name": "My Friend"}],
        },
        {
            "name": "Jeanne Doe",
            "parent_of": [{"name": "My Child"}],
            "child_of": [{"name": "My Parent"}],
            "friends_with": [{"name": "My Friend"}],
        },
    ]
    assert (
        GraphConnector().fetch_person_family_friends(two_people[0]["person"]["name"])
        == expected
    )
    assert mock_run_query.call_count == 1
    assert mock_fetch_friends_parents_children.call_count == 2


@patch.object(GraphConnector, "run_query", return_value=empty)
def test_fetch_person_family_friends_empty(mock_run_query):
    expected = []
    assert (
        GraphConnector().fetch_person_family_friends(two_people[0]["person"]["name"])
        == expected
    )
    assert mock_run_query.call_count == 1


@patch.object(GraphConnector, "run_query", return_value=two_people)
@patch.object(
    GraphConnector,
    "fetch_friends_parents_children",
    return_value=(empty, empty, empty),
)
def test_create_person(mock_fetch_friends_parents_children, mock_run_query):
    expected = {
        "name": "John Doe",
        "nickname": "Johnny",
        "parent_of": [],
        "child_of": [],
        "friends_with": [],
    }
    assert (
        GraphConnector().create_person(
            PersonInput(firstname="John", lastname="Doe", nickname="Johnny")
        )
        == expected
    )
    assert mock_run_query.call_count == 1
    assert mock_fetch_friends_parents_children.call_count == 1


@patch.object(GraphConnector, "run_query", return_value=two_people)
@patch.object(
    GraphConnector,
    "fetch_friends_parents_children",
    return_value=(empty, empty, empty),
)
def test_update_person(mock_fetch_friends_parents_children, mock_run_query):
    expected = {
        "name": "John Doe",
        "nickname": "Johnny",
        "parent_of": [],
        "child_of": [],
        "friends_with": [],
    }
    assert (
        GraphConnector().update_person(
            two_people[0]["person"]["name"],
            PersonInput(firstname="John", lastname="Doe", nickname="Johnny"),
        )
        == expected
    )
    assert mock_run_query.call_count == 1
    assert mock_fetch_friends_parents_children.call_count == 1


@patch.object(GraphConnector, "run_query", return_value=empty)
def test_update_person_not_found(mock_run_query):
    with pytest.raises(PersonNotFound):
        GraphConnector().update_person(
            two_people[0]["person"]["name"],
            PersonInput(firstname="John", lastname="Doe", nickname="Johnny"),
        )


@patch.object(GraphConnector, "run_query", return_value=two_people)
def test_remove_person(mock_run_query):
    assert GraphConnector().remove_person(two_people[0]["person"]["name"]) is None
    assert mock_run_query.call_count == 1


@patch.object(GraphConnector, "run_query", return_value=two_people)
@patch.object(
    GraphConnector,
    "fetch_friends_parents_children",
    return_value=(empty, empty, children),
)
def test_create_child_relationship(mock_fetch_friends_parents_children, mock_run_query):
    expected = {
        "name": "John Doe",
        "nickname": "Johnny",
        "parent_of": [{"name": "My Child"}],
        "child_of": [],
        "friends_with": [],
    }
    assert (
        GraphConnector().create_child_relationship(
            two_people[0]["person"]["name"],
            ChildInput(child_name=two_people[1]["person"]["name"]),
        )
        == expected
    )
    assert mock_run_query.call_count == 1
    assert mock_fetch_friends_parents_children.call_count == 1


@patch.object(GraphConnector, "run_query", return_value=empty)
def test_create_child_relationship_not_found(mock_run_query):
    with pytest.raises(PersonNotFound):
        GraphConnector().create_child_relationship(
            two_people[0]["person"]["name"],
            ChildInput(child_name=two_people[1]["person"]["name"]),
        )


@patch.object(GraphConnector, "run_query", return_value=two_people)
def test_remove_child_relationship(mock_run_query):
    assert (
        GraphConnector().remove_child_relationship(
            two_people[0]["person"]["name"],
            two_people[1]["person"]["name"],
        )
        is None
    )
    assert mock_run_query.call_count == 1


@patch.object(GraphConnector, "run_query", return_value=two_people)
@patch.object(
    GraphConnector,
    "fetch_friends_parents_children",
    return_value=(friends, empty, empty),
)
def test_create_friend_relationship(
    mock_fetch_friends_parents_children, mock_run_query
):
    expected = {
        "name": "John Doe",
        "nickname": "Johnny",
        "parent_of": [],
        "child_of": [],
        "friends_with": [{"name": "My Friend"}],
    }
    assert (
        GraphConnector().create_friend_relationship(
            two_people[0]["person"]["name"],
            FriendInput(friend_name=two_people[1]["person"]["name"]),
        )
        == expected
    )
    assert mock_run_query.call_count == 1
    assert mock_fetch_friends_parents_children.call_count == 1


@patch.object(GraphConnector, "run_query", return_value=empty)
def test_create_friend_relationship_not_found(mock_run_query):
    with pytest.raises(PersonNotFound):
        GraphConnector().create_friend_relationship(
            two_people[0]["person"]["name"],
            FriendInput(friend_name=two_people[1]["person"]["name"]),
        )


@patch.object(GraphConnector, "run_query", return_value=two_people)
def test_remove_friend_relationship(mock_run_query):
    assert (
        GraphConnector().remove_friend_relationship(
            two_people[0]["person"]["name"],
            two_people[1]["person"]["name"],
        )
        is None
    )
    assert mock_run_query.call_count == 1
