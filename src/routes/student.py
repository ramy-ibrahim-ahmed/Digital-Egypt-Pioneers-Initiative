from fastapi import APIRouter, HTTPException, status, Request, Response
from ..models import StudentModel, Student
from ..controllers import TranscriptController
from .schemas.student_schema import *

import bcrypt

router = APIRouter()


@router.post("/login", status_code=status.HTTP_202_ACCEPTED)
async def add_student(response: Response, student: StudentCreate):

    credentials = MockCollegeCredentials(
        username=student.username,
        password=student.password,
    )

    controller = TranscriptController(credentials=credentials)
    auth = controller.login()
    if not auth:
        raise HTTPException(status_code=400, detail="Invalid credentials!")

    response.set_cookie(key="validated_username", value=student.username)
    return {"message": f"Username {student.username} is valid and stored in a cookie."}


@router.post(
    "/admin/add-student",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_student(response: Response, request: Request, student: StudentCreate):
    student_model = StudentModel(db_client=request.app.db_client)

    if await student_model.username_exists(username=student.username):
        raise HTTPException(status_code=400, detail=f"Username already exists!")

    credentials = MockCollegeCredentials(
        username=student.username,
        password=student.password,
    )

    controller = TranscriptController(credentials)
    transcript = controller.process()

    try:
        hashed_password = bcrypt.hashpw(
            student.password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        student_data = Student(
            username=student.username,
            password=hashed_password,
            transcript=transcript,
        )

        new_student = await student_model.set_student(student_data)

        response.set_cookie(key="validated_username", value=student.username)
        return StudentResponse(
            username=new_student.username,
            message="Student added successfully",
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error adding student: {str(e)}")


@router.get(
    "/admin/students", response_model=StudentsResponse, status_code=status.HTTP_200_OK
)
async def get_all_students(request: Request):
    student_model = StudentModel(db_client=request.app.db_client)
    try:
        all_students = await student_model.get_all_students()
        students_response = [
            StudentResponse(
                username=student.username,
                message="Student record retrieved",
            )
            for student in all_students
        ]

        return StudentsResponse(students=students_response)

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error retrieving students: {str(e)}"
        )


@router.delete(
    "/admin/delete-student/{username}",
    response_model=StudentResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_student(request: Request, response: Response, username: str):
    student_model = StudentModel(db_client=request.app.db_client)
    try:
        deleted_student = await student_model.delete_student(username)
        if deleted_student is None:
            raise HTTPException(status_code=404, detail="Student not found")

        response.delete_cookie("validated_username")

        return StudentResponse(
            username=deleted_student["username"],
            message="Student deleted successfully",
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error deleting student: {str(e)}")
