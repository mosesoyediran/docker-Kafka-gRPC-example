from __future__ import annotations

import asyncio
import logging
import signal
import sys
import time
from contextlib import suppress

import grpc
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError
from config.settings import settings

from kafka.kafka_management.consumer import ConsumerLoop
from kafka.kafka_management.generated.kafka_management_pb2_grpc import \
    add_EventGatewayServicer_to_server
from kafka.kafka_management.grpc_server import Gateway
from kafka.kafka_management.handlers import (discover_handlers,
                                             ensure_topics_exist)
from kafka.kafka_management.producer import start_producer, stop_producer

log = logging.getLogger("kafka-all-in-one")
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s %(message)s")

# ────────────────────────────────────────────────────────────────────────
async def _bootstrap_kafka() -> None:
    """Wait until all brokers are reachable before we start."""
    for hostport in settings.KAFKA_BOOTSTRAP_SERVERS:
        host, port = hostport.split(":")
        for attempt in range(30):
            try:
                reader, writer = await asyncio.open_connection(host, int(port))
                writer.close(); await writer.wait_closed()
                break
            except OSError:
                await asyncio.sleep(1)
        else:
            log.error("Broker %s never became ready", hostport)
            sys.exit(1)

# ────────────────────────────────────────────────────────────────────────
async def _serve_grpc() -> grpc.aio.Server:
    """Create, start and return the gRPC server (don’t block)."""
    server = grpc.aio.server()
    servicer = Gateway()
    
    add_EventGatewayServicer_to_server(servicer, server)
    
    listen_addr = f"[::]:{settings.GRPC_PORT}"
    server.add_insecure_port(listen_addr)
    await server.start()
    log.info("🚀 EventGateway gRPC listening on  %s", listen_addr)
    return server

# ────────────────────────────────────────────────────────────────────────
async def _serve_consumer() -> ConsumerLoop:
    """Create, start and return the consumer loop (don’t block)."""
    # 1) discover all handlers
    handlers = discover_handlers()

    # 2) make sure every <svc>.topics.events exists
    all_event_topics = [
        cfg["topics"]["events"]
        for cfg in settings.KAFKA_CATALOG.values()
            if cfg and "events" in cfg["topics"]          
        ]
    await ensure_topics_exist(all_event_topics)

    # 3) build one big consumer
    raw_consumer = AIOKafkaConsumer(
        *all_event_topics,
        **settings.kafka_consumer_config,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )
    loop = ConsumerLoop(raw_consumer, handlers)
    task = asyncio.create_task(loop.run())
    log.info("✓ Kafka consumer loop started")
    return task

# ────────────────────────────────────────────────────────────────────────
async def _serve_dlq_watch() -> asyncio.Task:
    """Tail the DLQ topic in its own asyncio task."""
    dlq_topic = settings.kafka_topics["DLQ"]         # "kafka.dlq"
    
    cfg = settings.kafka_consumer_config.copy()
    cfg["group_id"] = "dlq-monitor"
    consumer = AIOKafkaConsumer(
        dlq_topic,
        **cfg,
        auto_offset_reset="earliest",
    )
    await consumer.start()

    async def _loop() -> None:
        try:
            async for msg in consumer:
                log.error("💀 DLQ key=%s  payload=%s",
                          msg.key.decode(errors="replace"),
                          msg.value.decode(errors="replace")[:500])
        finally:
            await consumer.stop()

    log.info("✓ DLQ watcher subscribed to %s", dlq_topic)
    return asyncio.create_task(_loop())


# ────────────────────────────────────────────────────────────────────────
async def main() -> None:
    # 0) Wait for brokers
    await _bootstrap_kafka()

    # 1) Start the shared producer
    for _ in range(5):
        try:
            await start_producer()
            break
        except KafkaConnectionError:
            log.warning("Producer bootstrap failed, retrying …")
            await asyncio.sleep(2)
    else:
        sys.exit("❌ Could not start AIOKafkaProducer")

    # 2) Fire up both services
    grpc_server   = await _serve_grpc()
    consumer_task = await _serve_consumer()
    dlq_task      = await _serve_dlq_watch() 

    # 3) Handle Ctrl-C / SIGTERM
    stop_event = asyncio.Event()

    def _graceful(*_: int) -> None:
        log.info("⏻  Shutdown requested — stopping …")
        stop_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        with suppress(NotImplementedError):
            loop.add_signal_handler(sig, _graceful)

    await stop_event.wait()

    # 4) Teardown
    for t in (consumer_task, dlq_task):
        t.cancel()
        with suppress(asyncio.CancelledError):
            await t

    await grpc_server.stop(5)     
    log.info("👋  Bye")

# -----------------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())