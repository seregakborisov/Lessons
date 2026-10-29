from sqlalchemy import Column
from sqlalchemy import Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship, mapped_column
from .base import Base


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    mentor_id = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(Text)

class Visit(Base):
    __tablename__ = "visit"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"))


