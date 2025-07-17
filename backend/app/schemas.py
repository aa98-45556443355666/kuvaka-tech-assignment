"""
Pydantic schemas for request and response validation throughout the API.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    """
    Base schema for user-related data.
    """
    mobile: str

class UserCreate(UserBase):
    """
    Schema for user creation requests.
    """
    password: Optional[str] = None

class UserOut(UserBase):
    """
    Schema for user output responses.
    """
    id: int
    created_at: datetime
    is_active: bool
    class Config:
        orm_mode = True

class OTPRequest(BaseModel):
    """
    Schema for OTP request payloads.
    """
    mobile: str
    purpose: str = Field(..., pattern="^(login|reset)$")

class OTPVerify(BaseModel):
    """
    Schema for OTP verification payloads.
    """
    mobile: str
    otp_code: str
    purpose: str

class Token(BaseModel):
    """
    Schema for JWT token responses.
    """
    access_token: str
    token_type: str = "bearer"

class ChatroomBase(BaseModel):
    """
    Base schema for chatroom-related data.
    """
    name: str

class ChatroomCreate(ChatroomBase):
    """
    Schema for chatroom creation requests.
    """
    access_token: str

class ChatroomOut(ChatroomBase):
    """
    Schema for chatroom output responses.
    """
    id: int
    created_at: datetime
    class Config:
        orm_mode = True

class MessageBase(BaseModel):
    """
    Base schema for message-related data.
    """
    content: str

class MessageCreate(MessageBase):
    """
    Schema for message creation requests.
    """
    access_token: str

class MessageOut(MessageBase):
    """
    Schema for message output responses.
    """
    id: int
    sender: str
    created_at: datetime
    class Config:
        orm_mode = True

class SubscriptionOut(BaseModel):
    """
    Schema for subscription status output.
    """
    tier: str
    status: str
    started_at: Optional[datetime]
    ends_at: Optional[datetime]
    class Config:
        orm_mode = True

class APIResponse(BaseModel):
    """
    Standard API response schema.
    """
    status: str
    message: str
    data: Optional[dict] = None 

class ChangePasswordRequest(BaseModel):
    """
    Schema for change password requests.
    """
    access_token: str
    new_password: str 