from flask import Flask
from tests.example.proto.hello_world_pb2 import HelloRequest

app = Flask(__name__)


@app.route("/")
def hello_world():
    HelloRequest()
    return "<p>Hello, World!</p>"
