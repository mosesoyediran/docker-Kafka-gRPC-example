import asyncio
import json
import logging

import grpc
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaTimeoutError
from config.settings import settings
from kafka.kafka_management.generated.kafka_management_pb2 import (
    EventEnvelope, PublishRequest, PublishResponse, SubscribeRequest)
from kafka.kafka_management.generated.kafka_management_pb2_grpc import \
    EventGatewayServicer
from kafka.kafka_management.producer import publish_event
from kafka.kafka_management.ratelimiter import TokenBucket

log = logging.getLogger("event-gateway")

bucket = TokenBucket(rate=settings.GATEWAY_RPS_LIMIT)

class Gateway(EventGatewayServicer):
    async def Publish(self, request: PublishRequest, context):
        # ── 1) Rate-limit per peer (IP:port from gRPC metadata) ───────────
        peer = context.peer()                 # e.g. "ipv4:10.0.0.7:52314"
        if not bucket(peer):
            context.set_code(grpc.StatusCode.RESOURCE_EXHAUSTED)
            context.set_details("Rate limit exceeded")
            return PublishResponse(ok=False, message="rate-limit")

        # ── 2) Pull trace IDs from metadata (if any) ──────────────────────
        md = dict(context.invocation_metadata())
        headers = []
        for hdr in ("trace-id", "span-id"):
            if hdr in md:
                headers.append((hdr, md[hdr].encode()))

        # ── 3) Try the real publish, else DLQ ────────────────────────────
        try:
            await publish_event(
                request.topic_key,
                request.key,
                request.payload,
                headers=headers,
            )
            return PublishResponse(ok=True, message="published")
        except KafkaTimeoutError as exc:
            log.error("Kafka timeout, sending to DLQ: %s", exc)
            # build DLQ envelope
            dlq_payload = json.dumps({
                "failed_topic": request.topic_key,
                "key": request.key,
                "payload": request.payload.decode(errors="replace"),
                "error": str(exc),
            }).encode()
            await publish_event(
                topic_key="DLQ",                    # ❶ map to kafka.dlq
                key=request.key,
                payload=dlq_payload,
            )
            return PublishResponse(ok=False, message="published to DLQ")
        except Exception as exc:
            log.exception("publish failed")
            return PublishResponse(ok=False, message=str(exc))
        
    async def Subscribe(self, request: SubscribeRequest, context):
        # 1) turn logical keys into real Kafka topic names
        svc = settings.SERVICE_NAME
        topics = [
          settings.KAFKA_CATALOG[svc]["topics"][tk]
          for tk in request.topic_keys
        ]

        consumer = AIOKafkaConsumer(
          *topics,
          **settings.kafka_consumer_config,
          auto_offset_reset="latest",
        )
        await consumer.start()
        try:
            async for msg in consumer:
                # yield each message as an EventEnvelope
                hdrs = {k: v for k, v in (msg.headers or [])}
                yield EventEnvelope(
                  topic=msg.topic,
                  key=msg.key.decode(),
                  payload=msg.value,
                  headers=hdrs,
                )
        finally:
            await consumer.stop()