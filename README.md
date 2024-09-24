# flaskRpcBridge
Bridge between Flask and [g]RPC

## Development
```commandline
# Build the image
docker build . -t flask-rpc-bridge:local

# Run unit and integration tests
docker run --rm -it -v $(pwd):/app flask-rpc-bridge:local pytest

# Get a shell for local development
docker run --rm -it -v $(pwd):/app flask-rpc-bridge:local bash
```
