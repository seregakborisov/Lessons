from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status, Depends

from .schemas import *
from db import models
from .router import apiRouter as router
from db.base import get_session


async def get_lesson(db: AsyncSession, lesson_id: int) -> models.Lesson | None:
    return await db.get(models.Lesson, lesson_id)


@router.get("/", response_model=list[LessonRead])
async def get_lessons(
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_session),
) -> list[models.Lesson]:
    # 1. Создаём запрос SELECT
    stmt = select(models.Lesson)

    # 2. Добавляем фильтр, если он нужен
    if is_active is not None:
        stmt = stmt.where(models.Lesson.is_active == is_active)

    # 3. Применяем пагинацию
    stmt = stmt.offset(skip).limit(limit)

    # 4. Выполняем запрос
    result = await db.execute(stmt)

    # 5. Извлекаем ORM-объекты
    return result.scalars().all()


@router.post("/", response_model=LessonRead, status_code=status.HTTP_201_CREATED)
async def create_lesson(
    data: LessonCreate, db: AsyncSession = Depends(get_session)
) -> models.Lesson:
    lesson = models.Lesson(**data.model_dump())
    db.add(lesson)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lesson with name '{data.name}' already exists",
        )
    await db.refresh(lesson)
    return lesson


@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson_fix(
    lesson_id: int, db: AsyncSession = Depends(get_session)
) -> None:
    lesson = await get_lesson(db, lesson_id)
    if lesson is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lesson not found")
    await db.delete(lesson)
    await db.commit()


@router.post("/create_lesson", response_model=LessonRead, status_code=status.HTTP_201_CREATED,)
async def create_lesson(
    data: LessonCreate,
    db: AsyncSession = Depends(get_session),
) -> models.Lesson:
    lesson = models.Lesson(**data.model_dump())
    db.add(lesson)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Lesson with name '{data.name}' already exists",
        )

    await db.refresh(lesson)
    return lesson