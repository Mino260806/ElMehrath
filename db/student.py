from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, DateTime
from datetime import date

from db.base import Base


class Student(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    last_contribution_date = Column(DateTime, nullable=False)
