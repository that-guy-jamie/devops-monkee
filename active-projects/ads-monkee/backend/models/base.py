"""
Base Model Classes
==================

Common fields and mixins for all models.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declared_attr

from backend.database import Base


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at timestamps.
    
    Automatically managed by SQLAlchemy events.
    """
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class BaseModel(Base, TimestampMixin):
    """
    Abstract base model with common fields.
    
    All models should inherit from this.
    """
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary (for JSON serialization)."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def __repr__(self) -> str:
        """String representation of model."""
        return f"<{self.__class__.__name__}(id={self.id})>"

