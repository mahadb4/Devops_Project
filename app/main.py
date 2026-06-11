from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db, wait_for_database
from app.models import Student

STUDENT_REG_NO = "2312241"


@asynccontextmanager
async def lifespan(application: FastAPI):
    wait_for_database()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="2312241 DevOps Project", lifespan=lifespan)


class StudentCreate(BaseModel):
    name: str
    reg_no: str
    email: Optional[str] = None
    course: Optional[str] = None


def student_to_dict(student):
    return {
        "id": student.id,
        "name": student.name,
        "reg_no": student.reg_no,
        "email": student.email,
        "course": student.course,
    }


@app.get("/")
def root():
    return {
        "message": "Mahad Baloch DevOps microservice is running",
        "student": STUDENT_REG_NO,
    }


@app.get("/health")
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Database not connected") from exc

    return {
        "status": "ok",
        "db": db_status,
        "student": STUDENT_REG_NO,
    }


@app.post("/students")
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    existing_student = (
        db.query(Student).filter(Student.reg_no == student.reg_no).first()
    )
    if existing_student:
        raise HTTPException(status_code=400, detail="Student already exists")

    new_student = Student(
        name=student.name,
        reg_no=student.reg_no,
        email=student.email,
        course=student.course,
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return student_to_dict(new_student)


@app.get("/students")
def get_students(db: Session = Depends(get_db)):
    students = db.query(Student).order_by(Student.id).all()
    return [student_to_dict(student) for student in students]


@app.get("/students/{reg_no}")
def get_student(reg_no: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.reg_no == reg_no).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student_to_dict(student)
