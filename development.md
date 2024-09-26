## Development
```commandline
# Build the image
docker build . -t flask-grpc-bridge:local

# Run unit and integration tests
docker run --rm -it -v $(pwd):/app flask-grpc-bridge:local pytest

# Get a shell for local development
docker run --rm -it -v $(pwd):/app flask-grpc-bridge:local bash
```
