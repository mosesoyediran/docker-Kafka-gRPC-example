import asyncio
import json

import kafka.kafka_management.producer as producer_mod


async def main():
    await producer_mod.start_producer()
    try:
        # send directly into the topic your consumer listens on:
        await producer_mod.producer.send_and_wait(
            "kafka-default.events",
            key=b"test.key",
            value=json.dumps({
                "type": "user.registered",
                "user_id": "abc",
            }).encode("utf-8"),
        )
        print("✅ Test event published into kafka-default.events")
    finally:
        await producer_mod.stop_producer()

if __name__ == "__main__":
    asyncio.run(main())
