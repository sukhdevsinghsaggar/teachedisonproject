import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import sqlalchemy
 
Base = declarative_base()
 
class Mails(Base):
    __tablename__ = 'Mails'

    id = Column(Integer, primary_key=True)
    subject = Column(String(250), nullable=False)
    body = Column(sqlalchemy.UnicodeText())

engine = create_engine('sqlite:///sentmails.db')
Base.metadata.create_all(engine)
