from sqlalchemy import Column, Integer, String, TIMESTAMP, func, MetaData
import database as db
from database import MetaData
metadata = MetaData()

class Post(db.Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)


class User(db.Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

