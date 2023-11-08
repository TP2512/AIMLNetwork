from .database import Base
from sqlalchemy.sql.expression import null
from sqlalchemy import Column,Integer,String
class Post(Base):
    __tablename__="posts"

    id=Column(Integer,primary_key=True,nullable=False)
    name=Column(String,nullable=False)
    surname=Column(String,nullable=False)
    rating = Column(Integer, nullable=False)

    # created_at=Column()