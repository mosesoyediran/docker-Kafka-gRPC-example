<!-- README.md -->
<h1 align="center">📡 Kafka Event Gateway</h1>
<p align="center">
  A standalone <strong>Kafka</strong> microservice with <strong>gRPC</strong> support for real-time <code>Publish</code> and <code>Subscribe</code> communication.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Kafka-ready-brightgreen.svg" />
  <img src="https://img.shields.io/badge/gRPC-enabled-blue.svg" />
  <img src="https://img.shields.io/badge/Python-3.13.2-blue.svg" />
  <img src="https://img.shields.io/badge/Docker-multi--stage-blue.svg" />
</p>

---

## 🌟 Features

- 🔄 Publish & Subscribe to Kafka topics via **gRPC**
- 🧵 Async **consumer loop** with `aiokafka`
- 🛡 Rate limiting per gRPC peer (IP-based)
- 💥 Built-in **DLQ (Dead Letter Queue)** support
- 🧠 Auto discovery of event handlers
- 🛠 Topic auto-provisioning with `AIOKafkaAdminClient`
- 🧪 Smoke testing support and dynamic stream subscription

---

## 🧱 Tech Stack

| Component      | Tool                          |
|----------------|-------------------------------|
| Language       | Python 3.13.2                 |
| Broker         | Kafka 3.6 (Bitnami, KRaft)    |
| Messaging      | gRPC + Protobuf               |
| Kafka Client   | aiokafka                      |
| Runtime        | Docker (multi-stage builds)   |
| Extras         | Celery, Redis, SQLAlchemy     |

---

## 📂 Project Layout

```
kafka-svc/
├── kafka/
│   └── kafka_management/
│       ├── protos/           # .proto files
│       ├── generated/        # gRPC-generated code
│       ├── producer.py
│       ├── consumer.py
│       ├── grpc_server.py
│       ├── ratelimiter.py
│       └── handlers.py
├── config/settings.py
├── Dockerfile
├── docker-compose.yml
└── proto-builder.Dockerfile
```

---

## 🚀 Getting Started

### 🧬 Clone and Configure

```bash
git clone https://github.com/your-org/kafka-svc.git
cd kafka-svc
cp .env.example .env
```

### 🧱 Build and Run

```bash
docker compose up --build
```

🕐 Wait for all services (kafka1–3, kafka-agent) to become **healthy**.

---

## 🔥 Smoke Test

```bash
python kafka/smoke_test.py
```

Expected output:

```
✅ Test event published into kafka-default.events
```

---

## 🛰 gRPC API Overview

### `Publish`

```proto
rpc Publish(PublishRequest) returns (PublishResponse);
```

Send a message to Kafka.

### `Subscribe`

```proto
rpc Subscribe(SubscribeRequest) returns (stream EventEnvelope);
```

Receive streamed Kafka events as they arrive.

---

## 🧠 Handler Discovery

Just decorate a handler function:

```python
@event_handler("user.created")
async def on_user_created(payload: dict):
    print("👤 New user created:", payload)
```

All handlers are auto-discovered per service on startup.

---

## 📊 Rate Limiting

Each peer (IP:port) is throttled using a token bucket:

```python
bucket = TokenBucket(rate=10, capacity=50)
```

Customizable in `settings.py`.

---

## 🪣 DLQ Support

Failed publishes are rerouted to:

```yaml
DLQ:
  topics:
    events: "kafka.dlq"
```

Logged for inspection via the built-in DLQ watcher.

---

## 📦 Dependency Management

Using `uv` for fast install and clean dependency tracking:

```bash
./run uv:add grpcio
./run deps:install
```

---

## 🔧 Developer Tools

| Task      | Command            |
|-----------|--------------------|
| Lint      | `./run lint`       |
| Format    | `./run format`     |
| Test      | `./run test`       |
| Quality   | `./run quality`    |

---

## 🧪 Test Locally

```bash
./run quality
```

Runs full lint, format, and test pipeline.

---

## 📜 License

MIT © 2025 [@webdev2123](mailto:webdev2123@gmail.com)

---

## 🙌 Contributing

Pull requests welcome! For major changes, please open an issue first to discuss what you'd like to change. Let's build robust Kafka pipelines together 🚀
