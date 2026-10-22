import threading
from confluent_kafka import Consumer, KafkaError, KafkaException
from .config import conf
from .models import UserDelete
from db.models import Lesson
from db.base import async_session
import asyncio


def run(stop_event: threading.Event) -> None:
    consumer = Consumer(conf)
    consumer.subscribe(["my-topic"]) # TODO: сюда добавить второй топик
    
    try:
        while not stop_event.is_set():
            
            try:
                msg = consumer.poll(timeout=0.5) 
            except KafkaException as e:
                print(e)
                if e.args[0].code() == KafkaError._WAKEUP:
                    break
                raise

            if msg is None:
                print("none")
                continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                print(f"Consumer error: {msg.error()}")
                break

            print(msg.topic(), msg.offset(), msg.timestamp(), msg.value())
            # TODO: тут делать if на топик, и вызывать соответсвующую логику.
            raw_msg = msg.value()
            if raw_msg == None:
                continue

            event = UserDelete.model_validate_json(raw_msg) 
            asyncio.run(delete_lesson(event.user_id))
            consumer.commit(asynchronous=False)
    finally:
        consumer.close()
        print("Consumer closed.")


async def delete_lesson(lesson_id: int):
    async with async_session() as session:
        lesson = await session.get(Lesson, lesson_id)
        await session.delete(lesson)
        await session.commit()

        print("lesson deleted")
