from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, Integer, Text, JSON, DateTime, Enum, ForeignKey, ARRAY
from sqlalchemy.sql import func
import enum
Base = declarative_base()

class AuditStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    done = "done"
    failed = "failed"

class Audit(Base):
    __tablename__ = "audits"
    id = Column(String, primary_key=True)               # UUID
    client_id = Column(String, nullable=True)           # GHL location or your client id
    contact_id = Column(String, nullable=False)
    url = Column(Text, nullable=False)
    audit_types = Column(JSON, nullable=True)           # list of str
    overall_score = Column(Integer, nullable=True)
    lighthouse_perf = Column(Integer, nullable=True)
    lighthouse_accessibility = Column(Integer, nullable=True)
    lighthouse_best_practices = Column(Integer, nullable=True)
    lighthouse_seo = Column(Integer, nullable=True)
    cwv_json = Column(JSON, nullable=True)
    tech_stack_json = Column(JSON, nullable=True)
    summary = Column(Text, nullable=True)
    report_url = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, nullable=False)

class AuditFinding(Base):
    __tablename__ = "audit_findings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    audit_id = Column(String, ForeignKey("audits.id", ondelete="CASCADE"))
    category = Column(String)
    severity = Column(String)
    code = Column(String)
    message = Column(Text)
    target = Column(Text)
    extra = Column(JSON)
