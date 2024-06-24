from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.data.graph_connector import GraphConnector, PersonNotFound
from app.schemas.input import PersonInput
from app.schemas.output import People, Person

router = APIRouter(
    prefix="/people",
    tags=["People"],
)

graph_connector = (
    GraphConnector()
)  # TODO this should be unique for all api (singleton db driver)


@router.get("/", summary="List all people")
async def list_people() -> People:
    people = graph_connector.list_people()
    return People(people=[Person(**person) for person in people])


@router.post("/", summary="Create a person")
async def post_person(person_info: PersonInput) -> Person:
    """
    Adds one person with minimal info
    :return: the person added
    """
    person = graph_connector.create_person(person_info)
    return Person(**person)


@router.get("/{name}", summary="Get a person's info")
async def get_person(name: str) -> Person:
    try:
        person = graph_connector.fetch_person(name)
    except PersonNotFound as exc:
        raise HTTPException(status_code=404, detail=exc.message)
    return Person(**person)


@router.put("/{name}", summary="Update a person's info")
async def put_person(name: str, person_info: PersonInput) -> Person:
    """
    Update all of a person's info at once (no partial update)
    """
    try:
        person = graph_connector.update_person(name, person_info)
    except PersonNotFound as exc:
        raise HTTPException(status_code=404, detail=exc.message)
    return Person(**person)


@router.delete(
    "/{name}",
    summary="Remove a person",
    status_code=204,
)
async def delete_person(name: str):
    """
    Deletes a person, including all the relationships they had with other people
    """
    graph_connector.remove_person(name)
