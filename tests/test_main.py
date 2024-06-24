from app.data.graph_connector import GraphConnector


def test_ping(client):
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}


def test_reset(client):
    response = client.get("/reset")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

    graph_connector = GraphConnector()
    results, keys, summary = graph_connector.driver.execute_query(
        "MATCH(n) RETURN COUNT(n)"
    )
    assert results[0][0] == 46
