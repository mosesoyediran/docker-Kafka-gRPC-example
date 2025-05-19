import importlib
import logging
import pkgutil
from typing import Any

from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from config.settings import settings

logger = logging.getLogger("event-router")

def discover_handlers() -> dict[str, Any]:
    """
    Scan every <service>.handlers module for @event_handler-decorated functions.
    Returns a mapping event_type → handler coroutine.
    """
    catalog = settings.KAFKA_CATALOG
    handlers: dict[str, Any] = {}

    for service_name in catalog:
        module_name = f"{service_name}.handlers"
        try:
            module = importlib.import_module(module_name)
        except ImportError:
            logger.debug("No handlers module for %s, skipping", service_name)
            continue

        for _, attr_name in pkgutil.iter_modules(module.__path__):
            # (not strictly needed if each handlers.py is flat)
            pass

        for attr in dir(module):
            fn = getattr(module, attr)
            if callable(fn) and hasattr(fn, "_event_type"):
                et = fn._event_type
                if et in handlers:
                    logger.warning("Duplicate handler for %s: %s vs %s",
                                   et, handlers[et], fn)
                handlers[et] = fn
                logger.info("Discovered handler for %s → %s", et, fn)
    return handlers




async def ensure_topics_exist(topics: list[str]) -> None:
    admin = AIOKafkaAdminClient(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        client_id="topic-creator",
    )
    await admin.start()
    try:
        existing = await admin.list_topics()
        missing = [t for t in topics if t not in existing]
        if missing:
            to_create = [
                NewTopic(
                    name=t,
                    num_partitions=3,              # or pull from settings
                    replication_factor=1,         # adjust as needed
                )
                for t in missing
            ]
            await admin.create_topics(new_topics=to_create)
    finally:
        await admin.close()
