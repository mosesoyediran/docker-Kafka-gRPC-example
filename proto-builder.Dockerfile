# proto-builder.Dockerfile
FROM python:3.13.2-slim-bookworm

WORKDIR /protos

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && pip install grpcio-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the raw .proto files
COPY kafka/kafka_management/protos/kafka_management.proto ./kafka/kafka_management/protos/

# Generate the Python stubs
RUN mkdir /out
RUN python -m grpc_tools.protoc \
    -Ikafka/kafka_management/protos \
    --python_out=/out \
    --grpc_python_out=/out \
    kafka/kafka_management/protos/kafka_management.proto
