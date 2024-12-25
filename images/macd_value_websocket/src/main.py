import asyncio
import json
import logging
import os
import websockets

from kafka import KafkaConsumer
from infrastructure.kafka_service import KafkaService
from infrastructure.config_service import ConfigService

interval = int(os.environ.get('INTERVAL', 0))

logging.basicConfig(level=logging.ERROR)


async def handler(websocket):
    while True:
        try:

            kafka_service = KafkaService()
            topic = (ConfigService()).get_candle_topic_name(interval)

            kafka_service.wait_topic_exists(topic)

            # consumer = KafkaConsumer(
            #     topic,
            #     bootstrap_servers=[(KafkaService()).get_bootstrap()],
            #     auto_offset_reset='latest',
            #     key_deserializer=lambda m: m.decode('utf-8'),
            #     value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            # )
            #
            # for message in consumer:
            #     await websocket.send(message.value)

        except Exception as e:
            print(e)
            break

async def main():

    if interval == 0:
        print("INTERVAL not find")
        return

    async with websockets.serve(handler, "localhost", 8001):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())

