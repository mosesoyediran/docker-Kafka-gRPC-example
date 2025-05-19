import asyncio
import json
import logging
from typing import Any

from aiokafka import AIOKafkaConsumer
from config.settings import settings

logger = logging.getLogger("event-router")

def make_consumer(
    topic_key: str,
    *,
    group_id: str | None = None,
    **overrides,
) -> AIOKafkaConsumer:
    """
    Factory that returns a ready-to-use AIOKafkaConsumer.

    Parameters
    ----------
    topic_key :
        Key inside ``settings.kafka_topics`` (e.g. "EVENTS", "METRICS").
    group_id :
        Optional override.  Defaults to the service-specific group ID from settings.
    overrides :
        Extra keyword arguments forwarded verbatim to ``AIOKafkaConsumer`` –
        handy for things like ``enable_auto_commit=True`` in dev, TLS, etc.
    """
    # resolve the topic name from settings
    topic = settings.kafka_topics[topic_key]

    # start with base consumer config from settings
    cfg = settings.kafka_consumer_config.copy()

    # allow overriding group_id if provided
    if group_id is not None:
        cfg["group_id"] = group_id

    # default behavior flags
    cfg.update(
        enable_auto_commit=False,
        auto_offset_reset="earliest",
    )

    # apply any extra overrides
    cfg.update(overrides)

    # create and return the consumer
    return AIOKafkaConsumer(topic, **cfg)


class ConsumerLoop:
    """Thin wrapper that drives any AIOKafkaConsumer."""

    def __init__(self, consumer: AIOKafkaConsumer, handlers: dict[str, Any]) -> None:
        self.consumer = consumer
        self.handlers = handlers

    async def run(self) -> None:
        await self.consumer.start()
        try:
            async for msg in self.consumer:
                await self.handle(msg)
                await self.consumer.commit()
        finally:
            await self.consumer.stop()

    async def handle(self, msg):
        # 1) Always log raw message
        key = msg.key.decode() if msg.key else None
        value = msg.value.decode(errors="replace")
        logger.info("🔄 message-in: topic=%s key=%s value=%s",
                    msg.topic, key, value)

        # 2) Dispatch based on payload["type"]
        try:
            payload = json.loads(msg.value)
        except json.JSONDecodeError:
            logger.error("❌ Invalid JSON: %s", value)
            return

        et = payload.get("type")
        fn = self.handlers.get(et)
        if not fn:
            logger.debug("⚠ No handler for event.type=%r", et)
            return

        # 3) Call the handler
        try:
            await fn(payload)
            logger.info("✅ Handled %s → %s", et, fn.__name__)
        except Exception:
            logger.exception("❌ Error in handler %s for %s", fn, et)
