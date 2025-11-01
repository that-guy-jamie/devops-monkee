"""
Audit Log Model
===============

Tracks all system mutations per SBEP v2.0 requirements.
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship

from backend.models.base import BaseModel


class AuditLog(BaseModel):
    """
    Audit Log Model
    
    Records all mutations for compliance and debugging.
    Required by SBEP v2.0 protocol.
    """
    
    __tablename__ = "audit_log"
    
    # Who performed the action
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # What was done
    action = Column(String(100), nullable=False, index=True)
    # Examples: "approve_modification", "execute_campaign_change", "create_client"
    
    # What resource was affected
    resource_type = Column(String(100), nullable=False, index=True)
    # Examples: "campaign_modification", "client", "user"
    
    resource_id = Column(String(100), nullable=False, index=True)
    
    # Details (before/after state)
    changes_json = Column(JSON, nullable=True)
    # Structure: {"before": {...}, "after": {...}, "fields_changed": [...]}
    
    # Additional context
    notes = Column(Text, nullable=True)
    
    # Request metadata
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self) -> str:
        return (
            f"<AuditLog(id={self.id}, action='{self.action}', "
            f"resource={self.resource_type}:{self.resource_id})>"
        )
    
    @classmethod
    def log_action(
        cls,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: str | int,
        changes: dict = None,
        notes: str = None,
        ip_address: str = None,
        user_agent: str = None,
    ) -> "AuditLog":
        """
        Create an audit log entry.
        
        Args:
            user_id: ID of user performing action
            action: Action name (e.g., "approve_modification")
            resource_type: Type of resource (e.g., "campaign_modification")
            resource_id: ID of resource
            changes: Optional dict with before/after state
            notes: Optional notes
            ip_address: Optional IP address
            user_agent: Optional user agent
            
        Returns:
            AuditLog instance (not yet saved to DB)
        """
        return cls(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            changes_json=changes,
            notes=notes,
            ip_address=ip_address,
            user_agent=user_agent,
        )

