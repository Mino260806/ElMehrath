from datetime import datetime, timedelta

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import engine
from sqlalchemy.orm import sessionmaker, Session

from db.base import Base
from db.document import Document
from db.student import Student
from util import dt_utils


class DbManager:
    def __init__(self):
        self.engine = create_engine("sqlite:///elmehrath.db", echo=True)
        Base.metadata.create_all(self.engine)

        self.Session = sessionmaker(bind=self.engine)

    def add_document(self, document):
        session = self.Session()
        session.add(document)
        existing_user: Student | None = session.query(Student).filter_by(id=document.user).first()
        if existing_user is None:
            print("Adding new user")
            session.add(Student(id=document.user, last_contribution_date=dt_utils.to_utc(document.sent_date)))
        else:
            existing_user.last_contribution_date = document.sent_date

        session.commit()
        document_id = document.id
        return document_id

    def update_document_message_id(self, document_id, message_id):
        with self.Session.begin() as session:
            document = session.query(Document).filter_by(id=document_id).first()
            document.message_id = message_id

    def delete(self, document_id):
        with self.Session.begin() as session:
            document = session.query(Document).filter_by(id=document_id).first()
            if document is not None:
                session.delete(document)
                return document
            return None

    async def find_inactive_users(self, callback):
        current_date = datetime.utcnow()
        min_contribution_date = current_date - timedelta(days=7)
        print(f"min_contribution_date is {min_contribution_date}")
        with self.Session.begin() as session:
            students = session.query(Student).filter(Student.last_contribution_date < min_contribution_date)
            await callback(students)

    def add_student(self, student_id, joined_at, can_exist=False):
        with self.Session.begin() as session:
            if can_exist:
                student = session.query(Student).filter_by(id=student_id).first()
                if student is not None:
                    return False
            student = Student(id=student_id, last_contribution_date=joined_at)
            session.add(student)
            return True

    def update_student_contribution(self, student_id, contribution_date):
        with self.Session.begin() as session:
            student = session.query(Student).filter_by(id=student_id).first()
            student.last_contribution_date = contribution_date
