from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session

from .. import database as dtb
from .. import models, Schemas
from .. import utils

router = APIRouter()


@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=Schemas.PostedUser)
def create_posts(user: Schemas.UserCreate, db: Session = Depends(dtb.get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_pwd = utils.hash(user.password)
    user.password = hashed_pwd
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
