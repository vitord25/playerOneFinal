"""The model representing the Message Table"""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.app.core.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    party_id = Column(Integer, ForeignKey("parties.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="messages")
    party = relationship("Party", back_populates="messages")