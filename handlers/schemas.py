from pydantic import BaseModel, ConfigDict, Field


class LessonBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    mentor_id: int
    is_active: bool = True
    description: str | None = None


class LessonUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    mentor_id: int | None = None
    is_active: bool | None = None
    description: str | None = None


class LessonRead(LessonBase):
    id: int
    model_config = ConfigDict(from_attributes=True)  # читаем из ORM-объекта


class LessonCreate(BaseModel):
    name: str
    mentor_id: int
    description: str | None = None
    is_active: bool = True


class LessonVisit(BaseModel):
    lesson_name: str
    user_id: int

