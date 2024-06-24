import pytest
from neo4j import GraphDatabase
from starlette.testclient import TestClient

from app.config import settings
from app.main import app


@pytest.fixture(scope="function")
def client():
    client = TestClient(app)
    return client


@pytest.fixture(scope="session")
def db_driver():
    driver = GraphDatabase.driver(settings.neo4j_uri)
    driver.verify_connectivity()  # TODO catch an error here?
    yield driver
    driver.close()


@pytest.fixture(scope="function", autouse=True)
def clean_db(db_driver):
    # For each test function, clean up the DB
    yield db_driver
    db_driver.execute_query(
        "MATCH (n) DETACH DELETE n", database_=settings.neo4j_database
    )
