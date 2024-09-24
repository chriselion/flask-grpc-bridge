from tests.example.app import app


def test_app():
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200

def test_hello_rpc():
    client = app.test_client()
    resp = client.get("/Greeter/SayHello/")
    assert resp.status_code == 200