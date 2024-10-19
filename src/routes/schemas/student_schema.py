from pydantic import BaseModel
from typing import List


# Request model for creating a student
class StudentCreate(BaseModel):
    username: str
    password: str


# Response model for a single student
class StudentResponse(BaseModel):
    username: str
    message: str


# Response model for the list of students
class StudentsResponse(BaseModel):
    students: List[StudentResponse]


# Response model for a single student detail
class StudentDetailResponse(BaseModel):
    username: str
    message: str


# Mock CollegeCredentials for testing
class MockCollegeCredentials:
    def __init__(self, username, password):
        self.username = username
        self.password = password
