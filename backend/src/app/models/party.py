"""The model representing the Party table"""
import enum
from sqlalchemy import Column, Integer, String, Date, Time, Enum, DateTime, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.app.core.database import Base


class PartyStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class Party(Base):
    __tablename__ = "parties"
    __table_args__ = (
        CheckConstraint("max_players > 0", name="ck_party_max_players"),
    )

    id = Column(Integer, primary_key=True, index=True)
    organizer_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    location = Column(String(255), nullable=False)
    max_players = Column(Integer, nullable=False)
    status = Column(Enum(PartyStatus), nullable=False, default=PartyStatus.PENDING)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    organizer = relationship("User", back_populates="organized_parties", foreign_keys=[organizer_id])
    game = relationship("Game", back_populates="parties")
    members = relationship("PartyMember", back_populates="party")
    messages = relationship("Message", back_populates="party")