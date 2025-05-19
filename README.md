# 📡 Kafka Event Gateway — gRPC-Powered Kafka Microservice

<p align="center">
  <img src="https://img.shields.io/badge/Kafka-Ready-brightgreen" alt="Kafka">
  <img src="https://img.shields.io/badge/gRPC-Enabled-blue" alt="gRPC">
  <img src="https://img.shields.io/badge/Python-3.13.2-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Docker-Multi--stage-blue" alt="Docker">
</p>

---

A production-ready **Kafka microservice** that supports:

- 🔄 Event **publishing** and **subscribing** via gRPC
- 💥 Automatic **DLQ (Dead Letter Queue)** for failed messages
- ⚡ Rate-limiting per gRPC client
- 🔍 Dynamic **handler discovery**
- 🧵 Consumer stream processing with `aiokafka`
- 🔐 Custom metadata propagation (e.g. `trace-id`, `span-id`)
- 🛠 Built-in Kafka topic bootstrap (via `AIOKafkaAdminClient`)

---

## 🧱 Tech Stack

- Python 3.13.2
- Kafka 3.6 (Bitnami KRaft mode)
- gRPC + `grpcio`, `grpcio-tools`
- aiokafka for async Kafka interaction
- Pydantic v2 + SQLAlchemy
- Docker (multi-stage, slim-bookworm)

---

## 📂 Project Structure

\`\`\`
kafka-svc/
├── kafka/
│   ├── kafka_management/
│   │   ├── protos/
│   │   ├── generated/
│   │   ├── producer.py
│   │   ├── consumer.py
│   │   ├── grpc_server.py
│   │   ├── ratelimiter.py
│   │   └── handlers.py
│   └── app.py
├── config/
│   └── settings.py
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── proto-builder.Dockerfile
\`\`\`

---

## 🚀 Getting Started

### 1️⃣ Clone & Configure

\`\`\`bash
git clone https://github.com/your-org/kafka-svc.git
cd kafka-svc
cp .env.example .env
\`\`\`

### 2️⃣ Build and Launch

\`\`\`bash
docker compose up --build
\`\`\`

### 3️⃣ Smoke Test

\`\`\`bash
python kafka/smoke_test.py
\`\`\`

---

## 🛰 gRPC Interface

### 📤 Publish

\`\`\`proto
rpc Publish(PublishRequest) returns (PublishResponse);
\`\`\`

### 📥 Subscribe

\`\`\`proto
rpc Subscribe(SubscribeRequest) returns (stream EventEnvelope);
\`\`\`

---

## 💡 Features

| Feature           | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| gRPC Gateway      | Publish/Subscribe to Kafka via gRPC                                         |
| DLQ Handling      | Messages that fail to publish are redirected to a DLQ topic                 |
| Rate Limiting     | Token-bucket per gRPC client IP                                             |
| Auto Topic Init   | Dynamically creates required Kafka topics                                   |
| Consumer Loop     | Dynamic handler resolution based on event type                              |
| Proto Builder     | Use proto-builder.Dockerfile to compile `.proto` files                      |

---

## 🔍 Handler Example

\`\`\`python
@event_handler("user.registered")
async def handle_user_registered(payload: dict):
    print("👤 New user:", payload["user_id"])
\`\`\`

---

## 🧪 Test Locally

\`\`\`bash
./run quality
./run lint
./run test
\`\`\`

---

## 📦 Dependencies

\`\`\`bash
./run deps:install
./run uv:add your-lib-name
\`\`\`

---

## 📜 License

MIT © 2025 [@webdev2123](mailto:webdev2123@gmail.com)
