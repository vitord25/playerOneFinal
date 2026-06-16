"""The model representing the audit_log table"""
import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.app.core.database import Base


class AuditAction(str, enum.Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    CANCEL = "CANCEL"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    entity = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False)
    action = Column(Enum(AuditAction), nullable=False)
    details = Column(JSON, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="audit_logs")