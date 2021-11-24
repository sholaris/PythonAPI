from fastapi import status, HTTPException, Depends, APIRouter
from starlette.responses import Response

from app import oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from .. import schemas, models, utils

router = APIRouter(prefix='/users', tags=['Users'])

# url   POST /users 
# desc  Create new user
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def create_user(user: schemas.UserBase, db: Session = Depends(get_db)):
    user.password = utils.hash(user.password)
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# url   GET /users/:id 
# desc  Read user profile
@router.get("/{id}", response_model=schemas.User)
def get_profile(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} does not exist!")
    return user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db), curr_user: int = Depends(oauth2.get_current_user)):
    query = db.query(models.User).filter(models.User.id == id)
    user = query.first()

    if user == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User with id {id} does not exist!')

    if user.id != curr_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to perform requested action')

    query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
