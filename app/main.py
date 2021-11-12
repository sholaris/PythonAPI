# FastAPI modules
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# SQLAlchemy modules
from .database import engine
# SQLAlchemy models
from . import models
# Routes imports
from .routers import post, user, auth, vote

#  Creating tables from models (NOW WE USE ALEMBIC)
# models.Base.metadata.create_all(bind=engine)

# app initiation
app = FastAPI()

# CORS Policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Including routes
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get('/')
def home():
    return {"message": "Hello World"}
