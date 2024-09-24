from flask import Flask
import functools
from tests.example.proto.hello_world_pb2 import HelloRequest, HelloReply
from tests.example.proto import hello_world_pb2

app = Flask(__name__)


@app.route("/")
def hello_world() -> str:
    return "<p>Hello, World!</p>"

def rpc(service_module, service_name, method_name):
    route = f"/{service_name}/{method_name}/"
    #breakpoint()
    module_descriptor = service_module.DESCRIPTOR
    service_descriptor = module_descriptor.services_by_name[service_name]
    method_descriptor = service_descriptor.methods_by_name[method_name]
    # TODO compare against function's input and output types
    # TODO ^ at type-check time
    input_type = method_descriptor.input_type._concrete_class
    output_type = method_descriptor.input_type._concrete_class  # noqa

    def rpc_decorator(func):
        @functools.wraps(func)
        def rpc_inner(*args, **kwargs):
            # Before
            input_message = input_type()
            # TODO from json or binary
            ret = func(input_message)
            # After
            # TODO to json or binary
            return str(ret)

        print(f"Registering {route=}")
        app.add_url_rule(route, view_func=rpc_inner)

        return rpc_inner


    return rpc_decorator

@rpc(hello_world_pb2, "Greeter", "SayHello")
def rpc_impl(req: HelloRequest) -> HelloReply:
    message = "Hello, " + (req.name or "world")
    resp = HelloReply(message=message)
    return resp

print(app.url_map)
