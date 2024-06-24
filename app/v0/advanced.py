from __future__ import annotations

from fastapi import APIRouter

from app.data.graph_connector import GraphConnector
from app.schemas.output import People, Person

router = APIRouter(
    prefix="/people/{name}",
    tags=["Advanced"],
)

graph_connector = GraphConnector()


@router.get("/ancestors", summary="List person's ancestors")
async def get_person_ancestors(name: str) -> People:
    people = graph_connector.fetch_person_ancestors(name)
    return People(people=[Person(**person) for person in people])


@router.get(
    "/family/friends",
    summary="List person's family friends",
)
async def get_person_family_friends(name: str) -> People:
    people = graph_connector.fetch_person_family_friends(name)
    return People(people=[Person(**person) for person in people])
