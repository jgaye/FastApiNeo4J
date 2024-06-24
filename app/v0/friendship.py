from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.data.graph_connector import GraphConnector, PersonNotFound
from app.schemas.input import FriendInput
from app.schemas.output import Person

router = APIRouter(
    prefix="/people/{name}/friends",
    tags=["Friendship"],
)

graph_connector = GraphConnector()


@router.post("/", summary="Create friend relationship")
async def post_person_friend(name: str, friend_info: FriendInput) -> Person:
    """
    Creates a friends relationship between two persons
    :return: the person which originate the friendship
    """
    try:
        person = graph_connector.create_friend_relationship(name, friend_info)
    except PersonNotFound as exc:
        raise HTTPException(status_code=404, detail=exc.message)
    return Person(**person)


@router.delete(
    "/{friend_name}",
    summary="Remove friend relationship",
    status_code=204,
)
async def delete_person_friend_relationship(name: str, friend_name: str):
    graph_connector.remove_friend_relationship(name, friend_name)
