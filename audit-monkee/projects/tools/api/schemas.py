from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any, Dict

AuditType = Literal["seo","design","stack"]
AuditStatus = Literal["queued","running","done","failed"]

class AuditCreate(BaseModel):
    contactId: str
    locationId: Optional[str] = None
    url: str
    types: List[AuditType] = Field(default_factory=lambda: ["seo","design","stack"])

class AuditOut(BaseModel):
    id: str
    status: AuditStatus

class AuditDetail(BaseModel):
    id: str
    url: str
    types: List[str]
    status: AuditStatus
    scores: Dict[str, Optional[int]] = {}
    summary: Optional[str] = None
    report_url: Optional[str] = None

class HeadcoreConfigOut(BaseModel):
    site: str
    generated_at: str
    version: str
    seo: Dict[str, Any] = {}
    social: Dict[str, Any] = {}
    structured_data: list = []
    performance: Dict[str, Any] = {}
    security: Dict[str, Any] = {}
    signature: str
