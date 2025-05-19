# kafka/kafka_management/producer.py

import logging

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
from config.settings import settings

log = logging.getLogger("kafka-producer")

producer: AIOKafkaProducer | None = None


# ─────────── lifecycle ─────────────────────────────────────────────
async def start_producer() -> None:
    global producer
    producer = AIOKafkaProducer(**settings.kafka_producer_config())
    await producer.start()


async def stop_producer() -> None:
    if producer:
        await producer.stop()


# ─────────── publish helper ────────────────────────────────────────
async def publish_event(
    topic_key: str,
    key: str,
    payload: bytes,
    *,
    headers: list[tuple[str, bytes]] | None = None,
) -> None:
    """
    Publish a message to the gateway’s Kafka cluster.

    Parameters
    ----------
    topic_key :
        Logical key from ``kafka_topics.yml`` (e.g. "events", "metrics").
    key :
        Kafka message key (UTF-8 string).
    payload :
        Raw message bytes (JSON, Avro, …).
    headers :
        Optional list of (header_key, header_value) tuples.
    """
    if producer is None:
        raise RuntimeError("Producer not started")

    # Resolve the concrete topic name from the YAML catalog
    svc = settings.SERVICE_NAME           # e.g. "wallet", "api", "default"
    try:
        topic = settings.KAFKA_CATALOG[svc]["topics"][topic_key]
    except KeyError as exc:
        raise RuntimeError(
            f"Unknown topic_key={topic_key!r} for service={svc}"
        ) from exc

    # Send the message
    try:
        await producer.send_and_wait(
            topic,
            key=key.encode("utf-8"),
            value=payload,
            headers=headers or [],
        )
        log.debug("Published to %s key=%s", topic, key)
    except KafkaError as err:
        log.error("Kafka publish failed (%s): %s", topic, err)
        raise
