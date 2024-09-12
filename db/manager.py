from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import engine
from sqlalchemy.orm import sessionmaker, Session

from db.base import Base
from db.document import Document


class DbManager:
    def __init__(self):
        self.engine = create_engine("sqlite:///elmehrath.db", echo=True)
        Base.metadata.create_all(self.engine)

        self.Session = sessionmaker(bind=self.engine)

    def add_document(self, document):
        session = self.Session()
        session.add(document)
        session.commit()
        document_id = document.id
        return document_id

    def update_document_message_id(self, document_id, message_id):
        with self.Session.begin() as session:
            document = session.query(Document).filter_by(id=document_id).first()
            document.message_id = message_id

    def delete(self, document_id):
        with self.Session.begin() as session:
            session.query(Document).filter_by(id=document_id).first()
