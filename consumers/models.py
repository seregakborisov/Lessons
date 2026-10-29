from pydantic import BaseModel


class UserDelete(BaseModel):
    user_id: int


class UserRegistration(BaseModel):
    user_id: int
