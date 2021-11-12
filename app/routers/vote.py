from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import schemas, database, models, oauth2

router = APIRouter(
    prefix = "/vote",
    tags = ["Vote"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(database.get_db), curr_user: int = Depends(oauth2.get_current_user)):

    # 1. If vote_dir = 1 -> user want to vote for post
    #   1.1 if vote of user_id for post_id exist
    #       raise an exception -> 409 conflict
    #   1.2 else
    #       create new record in vote table
    # 2. If vote_dir = 0 -> user want to delete a vote
    #   2.1 if vote does not exist in db
    #       raise an exception -> 404 not found
    #   2.2 else
    #       delete a vote with user_id and post_id

    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id {vote.post_id} does not exist')

    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == curr_user.id)
    
    found_vote = vote_query.first()

    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'user {curr_user.id} has already voted on post {vote.post_id}')
        
        new_vote = models.Vote(post_id = vote.post_id, user_id = curr_user.id)
        db.add(new_vote)
        db.commit()
        
        return {"message": "vote succesfully added"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'vote does not exist')
        
        vote_query.delete(synchronize_session=False)
        db.commit()
        
        return {"message": "vote succesfully deleted"}