import sys
# Add the directory containing Network_Analysis to the Python path
sys.path.append(r'C:\Users\tpujari\Desktop\infrastructuresvg\VIProject')
from typing import List
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from Network_Analysis.FastAPI import database as dtb
from Network_Analysis.FastAPI import models, Schemas

router = APIRouter()


@router.get("/posts", response_model=List[Schemas.GetRes])
def get_posts(db: Session = Depends(dtb.get_db)):
    posts = db.query(models.Post).all()
    return list(posts)


@router.post("/posts", response_model=Schemas.PostRes)
def create_posts(post: Schemas.CreatePost, db: Session = Depends(dtb.get_db)):
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/posts/{id}", response_model=Schemas.GetRes)
def get_single_post(id: str, db: Session = Depends(dtb.get_db)):
    posts = db.query(models.Post).filter(models.Post.id == id).first()
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"posts not found with id {id}")
    return posts


@router.delete("/posts/{id}")
def delete_posts(id: str, db: Session = Depends(dtb.get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exists")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/posts/{id}")
def patch_post(id: str, post: Schemas.Post, db: Session = Depends(dtb.get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    if post_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exists")
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return {"updated data": post_query.first()}
