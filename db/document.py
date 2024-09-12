from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from datetime import date

from db.base import Base


class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(String, nullable=True)
    url = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    user = Column(Integer, nullable=False)
    subject = Column(String, nullable=True)
    lesson = Column(String, nullable=True)
    author = Column(String, nullable=True)
    highschool = Column(String, nullable=True)
    description = Column(String, nullable=True)
    sent_date = Column(Date, default=date.today)
