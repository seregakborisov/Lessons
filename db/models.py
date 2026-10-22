from sqlalchemy import Column
from sqlalchemy import Integer, String, Text, Boolean
from sqlalchemy.orm import relationship, mapped_column
from .base import Base


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    mentor_id = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(Text)
