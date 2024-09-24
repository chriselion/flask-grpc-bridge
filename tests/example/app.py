from flask import Flask
import functools
from tests.example.proto.hello_world_pb2 import HelloRequest, HelloReply

app = Flask(__name__)


@app.route("/")
def hello_world() -> str:
    return "<p>Hello, World!</p>"

def rpc(route):
    def rpc_decorator(func):
        @functools.wraps(func)
        def rpc_inner(*args, **kwargs):
            # Before
            ret = func(*args, **kwargs)
            # After
            return ret
        return rpc_inner

    #print(app.url_map)
    print(f"Registering {route=}")
    app.add_url_rule(route, view_func=rpc_decorator)
    #print(app.url_map)

    return rpc_decorator

@rpc("/Greeter/SayHello/")
def rpc_impl(req: HelloRequest) -> HelloReply:
    message = "Hello, " + (req.name or "world")
    resp = HelloReply(message=message)
    return resp

print(app.url_map)
