from pydantic import BaseModel

class UserDelete(BaseModel):
    user_id: int