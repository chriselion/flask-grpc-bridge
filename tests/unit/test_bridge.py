from flask_rpc_bridge.bridge import CONTENT_TYPE_HEADER, PROTOBUF_CONTENT_TYPE

from tests.example.app import app, SayHello
from tests.example.proto.hello_world_pb2 import HelloReply, HelloRequest


def test_app():
    client = app.test_client()
    resp = client.get("/")
    assert resp.status_code == 200


def test_hello_rpc_json():
    client = app.test_client()
    resp = client.post("/Greeter/SayHello/", json={"name": "Jason"})

    assert resp.status_code == 200

    body = resp.json
    assert body == {"message": "Hello, Jason"}


def test_hello_rpc_binary():
    client = app.test_client()

    req = HelloRequest(name="Benny")
    resp = client.post(
        "/Greeter/SayHello/",
        data=req.SerializeToString(),
        headers={CONTENT_TYPE_HEADER: PROTOBUF_CONTENT_TYPE},
    )

    assert resp.status_code == 200

    resp_message = HelloReply()
    resp_message.ParseFromString(resp.data)
    assert resp_message.message == "Hello, Benny"


def test_original_func():
    # Make sure the original function is callable here
    req = HelloRequest()
    resp = SayHello(req)
    assert resp.message == "Hello, world"
