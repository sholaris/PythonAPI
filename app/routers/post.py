from fastapi import Response, status, HTTPException, Depends, APIRouter
from typing import List, Optional
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import schemas, models, oauth2

router = APIRouter(prefix='/posts', tags=['Posts'])

# url   GET /posts
# desc  Read all posts
@router.get("/", response_model=List[schemas.PostVote])
def get_posts(db: Session = Depends(get_db), curr_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
   
    # getting all posts data with count of votes + searching + limit + skip filters
    results = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    return results

# url   GET /posts/:id
# desc  Read one post
@router.get("/{id}", response_model=schemas.PostVote)
def get_post(id: int, db: Session = Depends(get_db), curr_user: int = Depends(oauth2.get_current_user)):

    post = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id {id} was not found!')
    
    return post

# url   POST /posts 
# desc  Create new post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostBase, db: Session = Depends(get_db), curr_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published))
    # conn.commit()
    # new_post = cursor.fetchone()
    new_post = models.Post(user_id=curr_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# url   DELETE /posts/:id
# desc  Delete post by id
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), curr_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id {id} does not exist!')
    
    if post.user_id != curr_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Not authorized to perform requested action')

    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# url   PUT /posts/:id 
# desc  Update post by id
@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostBase, db: Session = Depends(get_db), curr_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id {id} does not exist!')
    
    if post.user_id != curr_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Not authorized to perform requested action')


    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()