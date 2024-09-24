#!/usr/bin/env bash
python -m grpc_tools.protoc --python_out=tests/example/proto/ --grpc_python_out=tests/example/proto/ --proto_path=tests/example/proto/ tests/example/proto/hello_world.proto
