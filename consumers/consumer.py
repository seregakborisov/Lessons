from aiokafka import AIOKafkaConsumer
from pydantic import ValidationError
from sqlalchemy import delete

from .config import conf
from .models import UserDelete, UserRegistration
from db.models import Lesson
from db.base import async_session


async def run() -> None:
    consumer = AIOKafkaConsumer(
        "my-topic",
        "user-registrations",
        **conf,
    )

    await consumer.start()

    try:
        async for msg in consumer:
            raw_msg = msg.value
            topic = msg.topic

            try:
                if topic == "my-topic":
                    event = UserDelete.model_validate_json(raw_msg)
                    await delete_lessons_fix(event.user_id)

                elif topic == "user-registrations":
                    event = UserRegistration.model_validate_json(raw_msg)
                    await create_lesson(event.user_id)

                else:
                    continue

                await consumer.commit()

            except (ValidationError, Exception) as e:
                print(f"Ошибка обработки сообщения: {e}")
                raise

    finally:
        await consumer.stop()
        print("Consumer closed.")


async def delete_lessons_fix(deleted_user_id: int) -> None:
    async with async_session() as session:
        stmt = delete(Lesson).where(
            Lesson.mentor_id == deleted_user_id
        )

        await session.execute(stmt)
        await session.commit()

        print(f"Lessons for user {deleted_user_id} deleted")


async def create_lesson(user_id: int) -> None:
    async with async_session() as session:
        lesson = Lesson(
            name=f"Lesson for user {user_id}",
            mentor_id=user_id,
        )

        session.add(lesson)
        await session.commit()

        print(f"Lesson for user {user_id} created")