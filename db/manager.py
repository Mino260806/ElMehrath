from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from db.base import Base
from db.document import Document


class DbManager:
    def __init__(self):
        self.engine = create_engine("sqlite:///elmehrath.db", echo=True)
        Base.metadata.create_all(self.engine)

        self.Session = sessionmaker(bind=self.engine)

    def add_document(self, document):
        with self.Session.begin() as session:
            session.add(document)

    def delete(self, document_id):
        with self.Session.begin() as session:
            session.query(Document).filter_by(id=document_id).first()
