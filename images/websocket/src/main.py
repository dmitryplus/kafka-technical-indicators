import asyncio
import json
import logging
import os
import websockets

from kafka import KafkaConsumer
from infrastructure.kafka_service import KafkaService

logging.basicConfig(level=logging.ERROR)


async def main():
    topic = os.environ.get('TOPIC', None)

    if topic is None:
        print("TOPIC name not find")
        return

    kafka_service = KafkaService()
    kafka_service.wait_topic_exists(topic)

    async def handler(websocket):
        while True:
            try:
                consumer = KafkaConsumer(
                    topic,
                    bootstrap_servers=[(KafkaService()).get_bootstrap()],
                    auto_offset_reset='latest',
                    key_deserializer=lambda m: m.decode('utf-8'),
                    value_deserializer=lambda m: m.decode('utf-8'),
                )

                for message in consumer:
                    await websocket.send(message.value)

            except Exception as e:
                print(e)
                break

    async with websockets.serve(handler, "localhost", 8001):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
