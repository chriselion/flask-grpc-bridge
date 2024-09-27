from __future__ import annotations
import types

from flask import Flask, request, Response
import functools
from google.protobuf import json_format
from google.protobuf.message import Message
from werkzeug.exceptions import UnsupportedMediaType

from typing import TypeVar, Callable

try:
    from typing import ParamSpec
except ImportError:
    # Support pre-3.10 versions
    from typing_extensions import ParamSpec  # type: ignore[assignment]

CONTENT_TYPE_HEADER = "Content-Type"
# TODO Support more - https://stackoverflow.com/questions/30505408/what-is-the-correct-protobuf-content-type
PROTOBUF_CONTENT_TYPE = "application/protobuf"

P = ParamSpec("P")
R = TypeVar("R", bound=Message)


class Bridge:
    def __init__(self, app: Flask, service_module: types.ModuleType, service_name: str):
        self.app = app
        self.service_name = service_name
        self.module_descriptor = service_module.DESCRIPTOR
        self.service_descriptor = self.module_descriptor.services_by_name[service_name]

    def rpc(
        self, method_name: str | None = None
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        # TODO type annotations so wrapped types aren't lost
        def rpc_decorator(func: Callable[P, R]) -> Callable[P, R]:
            nonlocal method_name
            method_name = method_name or func.__name__

            # TODO return type? Whatever Flask methods are supposed to be
            @functools.wraps(func)
            def rpc_inner(*args: P.args, **kwargs: P.kwargs):

                method_descriptor = self.service_descriptor.methods_by_name[method_name]
                # TODO compare against function's input and output type annotations
                # TODO ^ at type-check time
                input_type = method_descriptor.input_type._concrete_class
                output_type = method_descriptor.input_type._concrete_class  # noqa

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
                        response_bytes,
                        200,
                        {CONTENT_TYPE_HEADER: PROTOBUF_CONTENT_TYPE},
                    )
                else:
                    # TODO parse options, handle int64
                    response_json = json_format.MessageToDict(ret)
                    return response_json

            route = f"/{self.service_name}/{method_name}/"
            print(f"Registering {route=}")
            # TODO option for methods
            self.app.add_url_rule(route, view_func=rpc_inner, methods=["POST"])

            # Return the original decorated function here (not rpc_inner like you'd do in a normal decorator)
            # So that it can still be called without the request/Response stuff.
            # This makes sure it still works as e.g. a gRPC handler
            return func

        return rpc_decorator
