from typing import Optional

from fastapi import FastAPI, Response, status, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from Network_Analysis.Test_App import models
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

# Replace these values with your actual database connection details
# db_params = {
#     "dbname": "fastapi",
#     "user": "postgres",
#     "password": "T@rkesh@2512",
#     "host": "127.0.0.1",
#     "port": "5432",
# }
#
# try:
#     connection = psycopg2.connect(**db_params,cursor_factory=RealDictCursor)
#     cursor = connection.cursor()
#     print("Database connection successful")
# except (Exception, psycopg2.Error) as error:
#     print("Error while connecting to PostgreSQL:", error)

# uvicorn.exe main:app --reload   ----command to execute

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Post(BaseModel):
    name: str
    surname: str
    rating: Optional[int] = None


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


@app.get("/")
async def hello_world():
    return {"message": "Hello World"}


@app.get("/sqlachemy")
def getsql(db: Session = Depends(get_db)):
    return {"status": "Success"}


@app.get("/posts")
def get_posts():
    query = '''select * from public.posts'''
    cursor.execute(query)
    records = cursor.fetchall()
    return {"data": records}


@app.post("/posts")
def create_posts(post: Post):
    cursor.execute(''' Insert Into posts (name,surname,rating) values(%s,%s,%s) returning * ''',
                   (post.name, post.surname, post.rating))
    new_post = cursor.fetchone()
    connection.commit()
    return {"msg": new_post}


@app.get("/posts/{id}")
def get_single_post(id: str):
    cursor.execute("""select * from posts where rating=%s""", (str(id),))
    posts = cursor.fetchone()
    print(posts)
    # posts=find_post(id)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"posts not found with id {id}")
    return {"data": posts}


@app.delete("/posts/{id}")
def delete_posts(id: str):
    cursor.execute("""delete from posts where rating=%s returning *""", (str(id),))
    deleted_post = cursor.fetchone()
    print(deleted_post)
    connection.commit()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exists")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.patch("/posts/{id}")
def patch_post(id: str, post: Post):
    cursor.execute("""update posts set name=%s where rating=%s returning *""", (post.name, str(id)))
    updated_post = cursor.fetchone()
    connection.commit()
    return {"updated data": updated_post}
