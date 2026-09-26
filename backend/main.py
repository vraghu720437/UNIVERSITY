from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from pwdlib import PasswordHash

from database import engine

app = FastAPI(title="University Super App")
password_hash = PasswordHash.recommended()


class StudentRegistration(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    student_id: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    department_id: int
    semester: int = Field(ge=1, le=12)
    section: str = Field(min_length=1, max_length=10)
    email: str | None = None
    phone: str | None = None


@app.get("/")
def home():
    return {
        "message": "Welcome to University Super App",
        "status": "running"
    }


@app.post("/api/students/register")
def register_student(student: StudentRegistration):
    try:
        with engine.begin() as connection:
            user_result = connection.execute(
                text("""
                    INSERT INTO users
                        (username, password_hash, role, email, phone, status)
                    VALUES
                        (:username, :password_hash, 'student',
                         :email, :phone, 'active')
                    RETURNING id
                """),
                {
                    "username": student.username,
                    "password_hash": password_hash.hash(student.password),
                    "email": student.email,
                    "phone": student.phone,
                }
            )

            user_id = user_result.scalar_one()

            student_result = connection.execute(
                text("""
                    INSERT INTO students
                        (user_id, student_id, name, department_id,
                         semester, section, status)
                    VALUES
                        (:user_id, :student_id, :name, :department_id,
                         :semester, :section, 'active')
                    RETURNING id, student_id, name, department_id,
                              semester, section, status
                """),
                {
                    "user_id": user_id,
                    "student_id": student.student_id,
                    "name": student.name,
                    "department_id": student.department_id,
                    "semester": student.semester,
                    "section": student.section,
                }
            )

            new_student = dict(student_result.fetchone()._mapping)

        return {
            "message": "Student registered successfully",
            "student": new_student
        }

    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail=(
                "Registration could not be completed. "
                "The username or student ID may already exist, "
                "or the department ID may be invalid."
            )
        )


@app.get("/api/students")
def get_students():
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT id, student_id, name, department_id,
                       semester, section, status
                FROM students
                ORDER BY id
            """)
        )
        students = [dict(row._mapping) for row in result]

    return {"students": students}