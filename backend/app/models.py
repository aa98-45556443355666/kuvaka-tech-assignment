from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    """
    SQLAlchemy model for application users.
    Each user is identified by a unique mobile number and may have associated chatrooms and a subscription.
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    mobile = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    chatrooms = relationship("Chatroom", back_populates="owner")
    subscription = relationship("Subscription", uselist=False, back_populates="user")

class OTP(Base):
    """
    Stores OTP codes for authentication and password reset purposes.
    """
    __tablename__ = "otps"
    id = Column(Integer, primary_key=True, index=True)
    mobile = Column(String, index=True, nullable=False)
    otp_code = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    purpose = Column(String, nullable=False)  # 'login' or 'reset'

class Chatroom(Base):
    """
    Represents a chatroom owned by a user, containing multiple messages.
    """
    __tablename__ = "chatrooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    owner = relationship("User", back_populates="chatrooms")
    messages = relationship("Message", back_populates="chatroom")

class Message(Base):
    """
    Stores individual messages in a chatroom, sent by either the user or Gemini.
    """
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    chatroom_id = Column(Integer, ForeignKey("chatrooms.id"))
    sender = Column(String, nullable=False)  # 'user' or 'gemini'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    chatroom = relationship("Chatroom", back_populates="messages")

class Subscription(Base):
    """
    Stores subscription details for a user, including tier and Stripe integration.
    """
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    tier = Column(String, default="basic")  # 'basic' or 'pro'
    stripe_subscription_id = Column(String, nullable=True)
    status = Column(String, default="inactive")
    started_at = Column(DateTime, nullable=True)
    ends_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="subscription") 