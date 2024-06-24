""" main """

from __future__ import annotations

from fastapi import FastAPI

from app.data.graph_connector import (
    GraphConnector,
)
from app.v0 import people, kinship, friendship, advanced

graph_connector = GraphConnector()
app = FastAPI(
    title="FastAPI and Neo4J",
    description="API built for Neo4j with FastAPI",
    version="0.1",
    docs_url="/docs",
    redoc_url="/redoc",
)


app.include_router(
    people.router,
    prefix="/v0",
)
app.include_router(
    kinship.router,
    prefix="/v0",
)
app.include_router(
    friendship.router,
    prefix="/v0",
)
app.include_router(
    advanced.router,
    prefix="/v0",
)


@app.get("/ping", tags=["Admin"])
async def ping():
    return {"status": "OK"}


@app.get("/reset", summary="Reset Neo4J content", tags=["Admin"])
async def reset():
    graph_connector.reset_db()
    return {"status": "OK"}
