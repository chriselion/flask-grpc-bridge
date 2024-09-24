from tests.example.app import app


def test_app():
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200


def test_hello_rpc_json():
    client = app.test_client()
    resp = client.post("/Greeter/SayHello/", json={"name": "Monty"})

    assert resp.status_code == 200

    body = resp.json
    assert body == {"message": "Hello, Monty"}
