"""
User Model
==========

Represents staff and client users with role-based access.
"""

import enum
from typing import Optional

from sqlalchemy import Column, ForeignKey, Integer, String, Enum as SQLEnum
from sqlalchemy.orm import relationship

from backend.models.base import BaseModel


class UserRole(str, enum.Enum):
    """User role for access control."""
    ADMIN = "admin"          # Full access, can approve & execute
    ANALYST = "analyst"      # Can analyze and report, no approval
    CLIENT = "client"        # Own data only, simplified view


class User(BaseModel):
    """
    User Model
    
    Represents both staff (admin, analyst) and client users.
    Authentication via GoHighLevel OAuth.
    """
    
    __tablename__ = "users"
    
    # Basic Information
    email = Column(String(255), nullable=False, unique=True, index=True)
    full_name = Column(String(255))
    
    # Role & Access
    role = Column(
        SQLEnum(UserRole),
        nullable=False,
        default=UserRole.CLIENT,
        index=True
    )
    
    # Client Association (NULL for staff users)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True, index=True)
    
    # GoHighLevel Integration
    ghl_user_id = Column(String(100), unique=True, index=True)
    ghl_location_id = Column(String(100))  # For client users
    
    # Relationships
    client = relationship("Client", back_populates="users", lazy="selectin")
    auth_sessions = relationship("AuthSession", back_populates="user", lazy="select")
    audit_logs = relationship("AuditLog", back_populates="user", lazy="select")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role={self.role.value})>"
    
    @property
    def is_staff(self) -> bool:
        """Check if user is staff (admin or analyst)."""
        return self.role in (UserRole.ADMIN, UserRole.ANALYST)
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role == UserRole.ADMIN
    
    @property
    def can_approve(self) -> bool:
        """Check if user can approve campaign modifications."""
        return self.role == UserRole.ADMIN
    
    @property
    def can_execute(self) -> bool:
        """Check if user can execute API changes."""
        return self.role == UserRole.ADMIN
    
    @property
    def can_view_all_clients(self) -> bool:
        """Check if user can view all clients."""
        return self.is_staff

