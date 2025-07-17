"""
Main entry point for the Gemini-style backend system using FastAPI.
Initializes middleware, routers, and database models.
"""
from fastapi import FastAPI
from .middleware import RateLimitMiddleware
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, user, chatroom, subscription
from app.database import engine
from app import models

app = FastAPI()

app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(chatroom.router)
app.include_router(subscription.router)

models.Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Gemini-style backend system running."} 