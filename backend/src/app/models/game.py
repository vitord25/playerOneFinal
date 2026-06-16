"""The model representing the Game Table"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.app.core.database import Base


class Game(Base):
    __tablename__ = "games"
    __table_args__ = (
        CheckConstraint("minimum_age >= 0", name="ck_game_minimum_age"),
        CheckConstraint("quantity >= 0", name="ck_game_quantity"),
        CheckConstraint("min_players > 0", name="ck_game_min_players"),
        CheckConstraint("max_players >= min_players", name="ck_game_max_players"),
        CheckConstraint("min_duration_minutes > 0", name="ck_game_min_duration"),
        CheckConstraint("max_duration_minutes >= min_duration_minutes", name="ck_game_max_duration"),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    minimum_age = Column(Integer, nullable=False, default=0)
    category = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    available = Column(Boolean, default=True, nullable=False)
    min_players = Column(Integer, nullable=False)
    max_players = Column(Integer, nullable=False)
    min_duration_minutes = Column(Integer, nullable=False)
    max_duration_minutes = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    parties = relationship("Party", back_populates="game")