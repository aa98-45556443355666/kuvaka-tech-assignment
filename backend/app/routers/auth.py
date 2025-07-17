from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .. import models, schemas, utils, deps
from ..config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=schemas.APIResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(deps.get_db)):
    """
    Register a new user with a mobile number and optional password.
    Returns an error if the mobile is already registered.
    """
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.mobile == user.mobile).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Mobile already registered")
    # Hash password if provided
    password_hash = utils.hash_password(user.password) if user.password else None
    new_user = models.User(mobile=user.mobile, password_hash=password_hash)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return schemas.APIResponse(status="success", message="User registered", data={"user_id": new_user.id})

@router.post("/send-otp", response_model=schemas.APIResponse)
def send_otp(req: schemas.OTPRequest, db: Session = Depends(deps.get_db)):
    """
    Generate and store an OTP for the given mobile and purpose, then return it.
    """
    # Generate OTP and set expiry
    otp_code = utils.generate_otp()
    expires_at = datetime.now() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    db_otp = models.OTP(mobile=req.mobile, otp_code=otp_code, expires_at=expires_at, purpose=req.purpose)
    db.add(db_otp)
    db.commit()
    return schemas.APIResponse(status="success", message="OTP sent", data={"otp": otp_code})

@router.post("/verify-otp", response_model=schemas.Token)
def verify_otp(req: schemas.OTPVerify, db: Session = Depends(deps.get_db)):
    """
    Verify the provided OTP for the given mobile and purpose.
    If valid, return a JWT access token for the user.
    """
    # Check OTP validity and expiry
    db_otp = db.query(models.OTP).filter(models.OTP.mobile == req.mobile, models.OTP.otp_code == req.otp_code, models.OTP.purpose == req.purpose).first()
    if not db_otp or db_otp.expires_at < datetime.now():
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    # Get or create user
    user = db.query(models.User).filter(models.User.mobile == req.mobile).first()
    if not user:
        user = models.User(mobile=req.mobile)
        db.add(user)
        db.commit()
        db.refresh(user)
    # Remove used OTP
    db.delete(db_otp)
    db.commit()
    access_token = utils.create_access_token({"sub": str(user.id)})
    return schemas.Token(access_token=access_token)

@router.post("/forgot-password", response_model=schemas.APIResponse)
def forgot_password(mobile: str = Body(...), db: Session = Depends(deps.get_db)):
    """
    Send an OTP for password reset to the given mobile number.
    """
    # Generate OTP for password reset
    otp_code = utils.generate_otp()
    expires_at = datetime.now() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    db_otp = models.OTP(mobile=mobile, otp_code=otp_code, expires_at=expires_at, purpose="reset")
    db.add(db_otp)
    db.commit()
    return schemas.APIResponse(status="success", message="OTP sent for password reset", data={"otp": otp_code})

@router.post("/change-password", response_model=schemas.APIResponse)
async def change_password(req: schemas.ChangePasswordRequest, current_user: models.User = Depends(deps.get_current_user), db: Session = Depends(deps.get_db)):
    """
    Change the password for the currently authenticated user.
    """
    # Update password hash
    current_user.password_hash = utils.hash_password(req.new_password)
    db.commit()
    return schemas.APIResponse(status="success", message="Password changed successfully") 