"""
Dependency functions for database sessions and user authentication in FastAPI routes.
"""
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from .database import SessionLocal
from .utils import decode_access_token
from .models import User
from .config import settings

def get_db():
    """
    Dependency that provides a SQLAlchemy database session.
    Yields:
        Session: SQLAlchemy session object.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Retrieve the current authenticated user from the request (body for POST/PUT).
    Raises HTTP 401 if authentication fails.
    """
    token = None
    source = None
    # Only get token from body for POST/PUT
    if request.method in ("POST", "PUT"):
        try:
            body = await request.json()
            token = body.get("access_token")
            if token:
                source = "body"
        except Exception:
            pass
    if token:
        print(f"[get_current_user] Token found in {source}.")
    else:
        print("[get_current_user] No token found.")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        print("[get_current_user] Raising 401: No token provided.")
        raise credentials_exception
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        print("[get_current_user] Raising 401: Invalid token or missing 'sub'.")
        raise credentials_exception
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None:
        print("[get_current_user] Raising 401: User not found.")
        raise credentials_exception
    print(f"[get_current_user] Authenticated user id: {user.id}")
    return user

async def get_current_user_from_schema(schema_obj, db: Session):
    """
    Retrieve the current authenticated user from a Pydantic schema object.
    Raises HTTP 401 if authentication fails.
    """
    token = getattr(schema_obj, 'access_token', None)
    if not token:
        print("[get_current_user_from_schema] No token found in schema.")
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        print("[get_current_user_from_schema] Raising 401: Invalid token or missing 'sub'.")
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None:
        print("[get_current_user_from_schema] Raising 401: User not found.")
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    print(f"[get_current_user_from_schema] Authenticated user id: {user.id}")
    return user

async def get_current_user_from_query(token: str, db: Session):
    """
    Retrieve the current authenticated user from a query parameter token.
    Raises HTTP 401 if authentication fails.
    """
    if not token:
        print("[get_current_user_from_query] No token found in query.")
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        print("[get_current_user_from_query] Raising 401: Invalid token or missing 'sub'.")
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None:
        print("[get_current_user_from_query] Raising 401: User not found.")
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    print(f"[get_current_user_from_query] Authenticated user id: {user.id}")
    return user 