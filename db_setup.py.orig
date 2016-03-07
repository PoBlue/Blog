import os
import sys
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

class Blog(Base):
	__tablename__ = 'blog'

	id = Column(Integer,primary_key=True)
	title = Column(String(50),nullable=False)
	content = Column(String(1024),nullable=False)
	time = Column(String(50),nullable=False)

class Login(Base):
	__tablename__ = 'login'

	id = Column(Integer,primary_key=True)
	user_name = Column(String(50),nullable=False)
	pwd = Column(String(50),nullable=False)

engine = create_engine('sqlite:///bolg.db')
Base.metadata.create_all(engine)

