"""The model Representing the request to enter a party by a user, party_member table"""
import enum
from sqlalchemy import Column, Integer, Enum, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.app.core.database import Base


class PartyMemberStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class PartyMember(Base):
    __tablename__ = "party_members"
    __table_args__ = (
        UniqueConstraint("user_id", "party_id", name="uq_party_member"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    party_id = Column(Integer, ForeignKey("parties.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    status = Column(Enum(PartyMemberStatus), nullable=False, default=PartyMemberStatus.PENDING)
    joined_at = Column(DateTime, server_default=func.now(), nullable=False)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)

    user = relationship("User", back_populates="party_memberships", foreign_keys=[user_id])
    party = relationship("Party", back_populates="members")
    approver = relationship("User", foreign_keys=[approved_by])