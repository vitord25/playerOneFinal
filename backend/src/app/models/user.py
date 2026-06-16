"""The model representing the User table"""
import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.app.core.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    profile_image_url = Column(String(500), nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    organized_parties = relationship("Party", back_populates="organizer", foreign_keys="Party.organizer_id")
    party_memberships = relationship("PartyMember", back_populates="user", foreign_keys="PartyMember.user_id")
    messages = relationship("Message", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")