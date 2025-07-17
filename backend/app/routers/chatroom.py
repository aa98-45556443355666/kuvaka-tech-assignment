"""
Handles chatroom creation, listing, retrieval, and messaging, including Gemini AI integration and caching.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .. import models, schemas, deps, cache, gemini
from ..config import settings
from ..database import SessionLocal
from ..cache import get_chatrooms_cache, set_chatrooms_cache, clear_chatrooms_cache
from typing import List
from ..gemini import call_gemini_api
from datetime import datetime

router = APIRouter(prefix="/chatroom", tags=["chatroom"])

@router.post("/", response_model=schemas.ChatroomOut)
async def create_chatroom(chatroom: schemas.ChatroomCreate, db: Session = Depends(deps.get_db)):
    """
    Create a new chatroom for the current user.
    """
    # Get current user from schema
    current_user = await deps.get_current_user_from_schema(chatroom, db)
    new_chatroom = models.Chatroom(name=chatroom.name, owner_id=current_user.id)
    db.add(new_chatroom)
    db.commit()
    db.refresh(new_chatroom)
    # Clear cache to ensure new chatroom appears in list
    clear_chatrooms_cache(current_user.id)
    return new_chatroom

@router.get("/", response_model=List[schemas.ChatroomOut])
async def list_chatrooms(access_token: str = Query(...), db: Session = Depends(deps.get_db)):
    """
    List all chatrooms for the current user, using cache if available.
    """
    # Get current user from access token
    current_user = await deps.get_current_user_from_query(access_token, db)
    cached = get_chatrooms_cache(current_user.id)
    if cached:
        # Ensure only dicts are returned from cache
        if all(isinstance(c, dict) for c in cached):
            return [schemas.ChatroomOut(**c) for c in cached]
        else:
            # Bad cache data, clear and fall back to DB
            print("[list_chatrooms] Bad cache data detected, clearing cache.")
            clear_chatrooms_cache(current_user.id)
    chatrooms = db.query(models.Chatroom).filter(models.Chatroom.owner_id == current_user.id).all()
    # Convert SQLAlchemy objects to dicts for Pydantic
    def chatroom_to_dict(obj):
        d = {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        if isinstance(d.get("created_at"), datetime):
            d["created_at"] = d["created_at"].isoformat()
        return d
    result = [schemas.ChatroomOut(**chatroom_to_dict(c)) for c in chatrooms]
    # Cache as list of dicts with all datetimes as ISO strings
    cache_data = []
    for r in result:
        d = r.model_dump()
        # Convert all datetime fields to ISO strings
        for k, v in d.items():
            if isinstance(v, datetime):
                d[k] = v.isoformat()
        cache_data.append(d)
    set_chatrooms_cache(current_user.id, cache_data)
    return result

@router.get("/{id}", response_model=schemas.ChatroomOut)
async def get_chatroom(id: int, access_token: str = Query(...), db: Session = Depends(deps.get_db)):
    """
    Retrieve a specific chatroom by ID for the current user.
    """
    # Get current user from access token
    current_user = await deps.get_current_user_from_query(access_token, db)
    chatroom = db.query(models.Chatroom).filter(models.Chatroom.id == id, models.Chatroom.owner_id == current_user.id).first()
    if not chatroom:
        raise HTTPException(status_code=404, detail="Chatroom not found")
    return chatroom

@router.post("/{id}/message", response_model=schemas.MessageOut)
async def send_message(id: int, msg: schemas.MessageCreate, db: Session = Depends(deps.get_db)):
    """
    Send a message to a chatroom and get a Gemini AI response.
    """
    # Get current user from schema
    current_user = await deps.get_current_user_from_schema(msg, db)
    chatroom = db.query(models.Chatroom).filter(models.Chatroom.id == id, models.Chatroom.owner_id == current_user.id).first()
    if not chatroom:
        raise HTTPException(status_code=404, detail="Chatroom not found")
    # Save user message
    user_msg = models.Message(chatroom_id=id, sender="user", content=msg.content)
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)
    # Call Gemini API synchronously
    gemini_response = call_gemini_api(msg.content)
    ai_msg = models.Message(chatroom_id=id, sender="gemini", content=gemini_response)
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)
    return ai_msg 