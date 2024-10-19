from ..helpers import get_settings
from .scema_mongo import Student
import bcrypt


class StudentModel:
    def __init__(self, db_client: object):
        self.db_client = db_client
        self.app_settings = get_settings()
        self.collection = self.db_client["students"]

    async def username_exists(self, username: str) -> bool:
        """Check if a username already exists in the database."""
        record = await self.collection.find_one({"username": username})
        return record is not None

    async def hash_password(self, password: str) -> str:
        """Hash the password using bcrypt."""
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return hashed.decode("utf-8")

    async def set_student(self, student: Student):
        """Insert a new student into the database."""
        if await self.username_exists(student.username):
            raise ValueError("Username already exists.")

        student.password = await self.hash_password(student.password)
        result = await self.collection.insert_one(
            student.model_dump(by_alias=True, exclude_unset=True)
        )
        return student

    async def get_all_students(self):
        """Retrieve all student records from the database."""
        students = await self.collection.find().to_list(length=100)
        return [Student(**student) for student in students]

    async def delete_student(self, username: str):
        """Delete a student record by username."""
        result = await self.collection.delete_one({"username": username})
        if result.deleted_count == 0:
            return None
        return {"username": username}

    async def get_transcript_by_username(self, username: str):
        """Retrieve a student transcript by username."""
        record = await self.collection.find_one({"username": username})
        if record is None:
            return None
        return record["transcript"]
