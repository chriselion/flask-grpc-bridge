from flask import Flask
from tests.example.proto.hello_world_pb2 import HelloRequest, HelloReply
from tests.example.proto import hello_world_pb2
from flask_grpc_bridge.bridge import Bridge

app = Flask(__name__)


@app.route("/")
def hello_world() -> str:
    return "<p>Hello, World!</p>"


bridge = Bridge(app, hello_world_pb2, "Greeter")


@bridge.rpc()
def SayHello(req: HelloRequest) -> HelloReply:
    message = "Hello, " + (req.name or "world")
    resp = HelloReply(message=message)
    return resp


print(app.url_map)
