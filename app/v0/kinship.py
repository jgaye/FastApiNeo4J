from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.data.graph_connector import GraphConnector, PersonNotFound
from app.schemas.input import ChildInput
from app.schemas.output import Person

router = APIRouter(
    prefix="/people/{name}/children",
    tags=["Kinship"],
)

graph_connector = GraphConnector()


@router.post(path="/", summary="Create child relationship")
async def post_person_child(name: str, child_info: ChildInput) -> Person:
    """
    Creates a parent relationship between two persons
    :return: the person with the child info
    """
    try:
        person = graph_connector.create_child_relationship(name, child_info)
    except PersonNotFound as exc:
        raise HTTPException(status_code=404, detail=exc.message)
    return Person(**person)


@router.delete(
    "/{child_name}",
    summary="Remove child relationship",
    status_code=204,
)
async def delete_person_child_relationship(name: str, child_name: str):
    graph_connector.remove_child_relationship(name, child_name)
