import asyncio
import json
import logging
import os
import websockets

from kafka import KafkaConsumer
from infrastructure.kafka_service import KafkaService

logging.basicConfig(level=logging.ERROR)


async def main():
    port = int(os.environ.get('PORT', '8001'))
    topic = os.environ.get('TOPIC', 'macd-values-1-min')

    if topic is None:
        print("TOPIC name not find")
        return

    figi = os.environ.get('FIGI', 'BBG004730N88')

    kafka_service = KafkaService()
    kafka_service.wait_topic_exists(topic)

    async def handler(websocket):
        while True:
            try:
                consumer = KafkaConsumer(
                    topic,
                    bootstrap_servers=[(KafkaService()).get_bootstrap()],
                    group_id=f'websocket-group-{topic}-{figi}',
                    auto_offset_reset='earliest',
                    key_deserializer=lambda m: m.decode('utf-8'),
                    value_deserializer=lambda m: m.decode('utf-8'),
                )

                for message in consumer:
                    if message.key == figi:
                        print(message.key, message.value)
                        await websocket.send(message.value)

            except Exception as e:
                print(e)
                break

    async with websockets.serve(handler, "localhost", port):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
