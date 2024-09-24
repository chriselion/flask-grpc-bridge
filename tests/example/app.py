from flask import Flask, request, Response
import functools
from tests.example.proto.hello_world_pb2 import HelloRequest, HelloReply
from tests.example.proto import hello_world_pb2
from google.protobuf import json_format
from werkzeug.exceptions import UnsupportedMediaType

app = Flask(__name__)


@app.route("/")
def hello_world() -> str:
    return "<p>Hello, World!</p>"


CONTENT_TYPE_HEADER = "Content-Type"
# TODO Support more - https://stackoverflow.com/questions/30505408/what-is-the-correct-protobuf-content-type
PROTOBUF_CONTENT_TYPE = "application/protobuf"


def rpc(service_module, service_name, method_name):
    route = f"/{service_name}/{method_name}/"

    module_descriptor = service_module.DESCRIPTOR
    service_descriptor = module_descriptor.services_by_name[service_name]
    method_descriptor = service_descriptor.methods_by_name[method_name]
    # TODO compare against function's input and output type annotations
    # TODO ^ at type-check time
    input_type = method_descriptor.input_type._concrete_class
    output_type = method_descriptor.input_type._concrete_class  # noqa

    def rpc_decorator(func):
        @functools.wraps(func)
        def rpc_inner(*args, **kwargs):

            input_message = input_type()
            # Read the request from either the json body, or directly as bytes
            try:
                # TODO parse options
                json_format.ParseDict(
                    request.json, input_message, ignore_unknown_fields=True
                )
                is_body_proto = False
            except UnsupportedMediaType:
                is_body_proto = True
                input_message.ParseFromString(request.data)
            # TODO handle parse errors, unknown fields etc as 4xx

            # Make the function call
            ret = func(input_message)

            # Return the response in the same format
            if is_body_proto:
                response_bytes = ret.SerializeToString()
                return Response(
                    response_bytes, 200, {CONTENT_TYPE_HEADER: PROTOBUF_CONTENT_TYPE}
                )
            else:
                # TODO parse options, handle int64
                response_json = json_format.MessageToDict(ret)
                return response_json

        print(f"Registering {route=}")
        app.add_url_rule(route, view_func=rpc_inner, methods=["POST"])

        return rpc_inner

    return rpc_decorator


@rpc(hello_world_pb2, "Greeter", "SayHello")
def rpc_impl(req: HelloRequest) -> HelloReply:
    message = "Hello, " + (req.name or "world")
    resp = HelloReply(message=message)
    return resp


print(app.url_map)
