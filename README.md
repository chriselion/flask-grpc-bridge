# flask-grpc-bridge
Bridge between Flask and gRPC. `flask_grpc_bridge` allows you to define RPC services and methods using protobufs,
but serve them using Flask. The resulting Flask endpoints can accept either JSON or binary representations of the
request messages, and return the corresponding response message.

## Who is this for?
Two cases that I've run across in various jobs:
* Existing Flask services that want some stronger typing and validation on the incoming requests, or that are being
called from strongly-typed languages (like golang), and want to use a shared schema, or don't want to deal with JSON
requests and responses.
* Existing gRPC services that want to be called from web browsers (or other systems that might not have good protobuf
support). These clients need to be able to pass JSON requests and receive JSON responses, but they don't want to
rewrite the service logic.

## Example usage
Given a gRPC service definition (from the [gRPC documentation](https://grpc.io/docs/what-is-grpc/introduction/)):
```protobuf
// hello_world.proto
syntax = "proto3";

// The greeter service definition.
service Greeter {
  // Sends a greeting
  rpc SayHello (HelloRequest) returns (HelloReply) {}
}

// The request message containing the user's name.
message HelloRequest {
  string name = 1;
}

// The response message containing the greetings
message HelloReply {
  string message = 1;
}
```

You can set up a regular Flask app, and add a bridge for the gRPC service:
```python
app = Flask(__name__)
bridge = Bridge(app, hello_world_pb2, "Greeter")
```
Then write the implementation and decorate it:

```python
@bridge.rpc()
def SayHello(req: HelloRequest) -> HelloReply:
    message = "Hello, " + (req.name or "world")
    resp = HelloReply(message=message)
    return resp
```

This will register a `/Greeter/SayHello/` route with the Flask app.
* When the endpoint receives a JSON request, it will be converted to a `HelloRequest` message and passed to the
`SayHello` function. The returned `HelloReply` message will be converted to JSON and returned in the response.
* If the endpoint receives a request with `Content-Type: application/protobuf` header, it will treat the body as a
serialized protobuf, and deserialize it as a `HelloRequest` message. Similarly, the returned `HelloReply` will be
serialized and returned (using the same `Content-Type` header).

## Future work
* Short term:
  * Better error handling and messaging.
  * More options for protobuf <-> JSON conversion (e.g. control over the `ignore_unknown_fields` flag, http methods)
* Long term:
  * Client-side code generation
  * Support for some options from [Transcoding HTTP/JSON to gRPC](https://cloud.google.com/endpoints/docs/grpc/transcoding)
  * OpenAPI schema generation
