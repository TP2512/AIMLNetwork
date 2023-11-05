from fastapi import FastAPI,Response,status,HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor

# Replace these values with your actual database connection details
db_params = {
    "dbname": "EZLifeDev_svgb-ezlife-app",
    "user": "airspan",
    "password": "Airspan@123",
    "host": "10.34.0.171",
    "port": "5432",
}

try:
    connection = psycopg2.connect(**db_params,cursor_factory=RealDictCursor)
    cursor = connection.cursor()
    print("Database connection successful")
except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL:", error)
finally:
    if cursor:
        cursor.close()
    if connection:
        connection.close()


#uvicorn.exe main:app --reload   ----command to execute

app = FastAPI()

class Post(BaseModel):
    name : str
    surname : str
    rating : Optional[int] = None

my_posts=[{"title":"title post 1","content":"content of post 1","id":1},{"title":"title post 2","content":"content of post 2","id":2}]

def find_post(id):
    for p in my_posts:
        if p["id"]==id:
            return p
@app.get("/")
async def hello_world():
    return {"message": "Hello World"}

@app.get("/posts")
def get_posts():
    query='''select * from public.posts'''
    cursor.execute(query)
    records=cursor.fetchall()
    return {"data":records}
@app.get("/user")
async def username(username,password):
    return {"name": "Tarkesh"}

@app.post("/createusers")
def username( payload : dict = Body(...)):
    print(payload)
    return {"msg": "user created"}

@app.post("/createuser")
def username( payload : Post):
    print(payload.rating)
    print(payload.dict())
    return {"msg": "user created"}

@app.post("/posts",status_code=status.HTTP_201_CREATED)
def post_blog(post: Post):
    print(post)
    my_posts.append(post.dict())
    print(my_posts)
    return {"data has been posted"}

@app.get("/acp/{id}")
def get_acp(id: int,response:Response):
    posts=find_post(id)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"posts not found with id {id}")
    return {"data":posts}

