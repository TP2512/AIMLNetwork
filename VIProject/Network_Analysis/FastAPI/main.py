from fastapi import FastAPI
from database import Base, engine
import database as dtb
import models
from routers import post, user

models.db.Base.metadata.create_all(bind=dtb.engine)
app = FastAPI()
app.include_router(post.router)
app.include_router(user.router)


@app.get("/")
def root():
    return {"message": "Your at my project"}

# @app.get("/posts")
# def get_posts():
#     query = '''select * from public.posts'''
#     cursor.execute(query)
#     records=cursor.fetchall()
#     return {"data": records}
#
# @app.post("/posts")
# def create_posts( post : Post):
#     cursor.execute(''' Insert Into posts (name,surname,rating) values(%s,%s,%s) returning * ''',(post.name,post.surname,post.rating))
#     new_post=cursor.fetchone()
#     connection.commit()
#     return {"msg":new_post}
#
# @app.get("/posts/{id}")
# def get_single_post(id: str):
#     cursor.execute("""select * from posts where rating=%s""",(str(id),))
#     posts=cursor.fetchone()
#     print(posts)
#     # posts=find_post(id)
#     if not posts:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"posts not found with id {id}")
#     return {"data":posts}
#
# @app.delete("/posts/{id}")
# def delete_posts(id:str):
#     cursor.execute("""delete from posts where rating=%s returning *""",(str(id),))
#     deleted_post=cursor.fetchone()
#     print(deleted_post)
#     connection.commit()
#     if deleted_post==None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with id: {id} does not exists")
#     return Response(status_code=status.HTTP_204_NO_CONTENT)
#
# @app.patch("/posts/{id}")
# def patch_post(id:str,post:Post):
#     cursor.execute("""update posts set name=%s where rating=%s returning *""",(post.name,str(id)))
#     updated_post=cursor.fetchone()
#     connection.commit()
#     return {"updated data":updated_post}

# # Replace these values with your actual database connection details
# db_params = {
#     "dbname": "EZLifeDev_svgb-ezlife-app",
#     "user": "airspan",
#     "password": "Airspan@123",
#     "host": "10.34.0.171",
#     "port": "5432",
# }
#
# try:
#     connection = psycopg2.connect(**db_params,cursor_factory=RealDictCursor)
#     cursor = connection.cursor()
#     print("Database connection successful")
# except (Exception, psycopg2.Error) as error:
#     print("Error while connecting to PostgreSQL:", error)
# finally:
#     if cursor:
#         cursor.close()
#     if connection:
#         connection.close()
#
#
# #uvicorn.exe main:app --reload   ----command to execute
#
# app = FastAPI()
#
# class Post(BaseModel):
#     name : str
#     surname : str
#     rating : Optional[int] = None
#
# my_posts=[{"title":"title post 1","content":"content of post 1","id":1},{"title":"title post 2","content":"content of post 2","id":2}]
#
# def find_post(id):
#     for p in my_posts:
#         if p["id"]==id:
#             return p
# @app.get("/")
# async def hello_world():
#     return {"message": "Hello World"}
#
# @app.get("/posts")
# def get_posts():
#     query='''select * from public.posts'''
#     cursor.execute(query)
#     records=cursor.fetchall()
#     return {"data":records}
# @app.get("/user")
# async def username(username,password):
#     return {"name": "Tarkesh"}
#
# @app.post("/createusers")
# def username( payload : dict = Body(...)):
#     print(payload)
#     return {"msg": "user created"}
#
# @app.post("/createuser")
# def username( payload : Post):
#     print(payload.rating)
#     print(payload.dict())
#     return {"msg": "user created"}
#
# @app.post("/posts",status_code=status.HTTP_201_CREATED)
# def post_blog(post: Post):
#     print(post)
#     my_posts.append(post.dict())
#     print(my_posts)
#     return {"data has been posted"}
#
# @app.get("/acp/{id}")
# def get_acp(id: int,response:Response):
#     posts=find_post(id)
#     if not posts:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"posts not found with id {id}")
#     return {"data":posts}
#
