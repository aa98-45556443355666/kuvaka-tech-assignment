"""
Handles user profile endpoints, such as retrieving the current user's information.
"""
from fastapi import APIRouter, Depends, Query
from .. import schemas, deps, models
from sqlalchemy.orm import Session

router = APIRouter(prefix="/user", tags=["user"])

class UserMeRequest(schemas.BaseModel):
    access_token: str

@router.get("/me", response_model=schemas.UserOut)
async def get_me(access_token: str = Query(...), db: Session = Depends(deps.get_db)):
    """
    Retrieve the current authenticated user's profile information.
    """
    # Get current user from access token
    current_user = await deps.get_current_user_from_query(access_token, db)
    return current_user 