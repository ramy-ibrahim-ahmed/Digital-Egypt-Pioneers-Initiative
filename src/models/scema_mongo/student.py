from pydantic import BaseModel, Field
from typing import Optional
from bson.objectid import ObjectId


class Student(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    username: str = Field(..., min_length=8)
    password: str = Field(..., min_length=14)
    transcript: str = Field(...)

    class Config:
        arbitrary_types_allowed = True
