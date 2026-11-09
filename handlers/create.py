from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status, Depends

from .schemas import *
from db import models
from .router import router
from db.base import get_session

from typing import Annotated
from .authorise import get_current_user

async def get_lesson(db: AsyncSession, lesson_id: int) -> models.Lesson | None:
    return await db.get(models.Lesson, lesson_id)


@router.get("/", response_model=list[LessonRead])
async def get_lessons(
    current_user: Annotated[dict, Depends(get_current_user)],
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

@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson_fix(
    current_user: Annotated[dict, Depends(get_current_user)],
    lesson_id: int, db: AsyncSession = Depends(get_session)
) -> None:
    if current_user["role"] == "Student":
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Студентам запрещено удалять лекции")

    lesson = await get_lesson(db, lesson_id)

    
    if lesson is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lesson not found")
    await db.delete(lesson)
    await db.commit()


@router.post(
    "/create_lesson",
    response_model=LessonRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_lesson(
    current_user: Annotated[dict, Depends(get_current_user)],
    data: LessonCreate,
    db: AsyncSession = Depends(get_session),
) -> models.Lesson:
    if current_user["role"] == "Student":
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Студентам запрещено создавать лекции")
    
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


@router.post(
    "/user_visit",
    response_model=LessonVisit,
    status_code=status.HTTP_201_CREATED,
)
async def user_visit(
    data: LessonVisit,
    db: AsyncSession = Depends(get_session),
) -> LessonVisit:
   
    
    stmt = select(models.Lesson)
    
    stmt = stmt.where(models.Lesson.name == data.lesson_name)

    result = await db.execute(stmt)
    lesson = result.scalar_one_or_none()

    if lesson is None:
        raise Exception('Lesson not found')


    visit = models.Visit(lesson_id = lesson.id, user_id = data.user_id)

    db.add(visit)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User visit '{data.lesson_name}' ",
        )

    await db.refresh(visit)
    return data


