import uuid
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .settings import settings
from .deps import get_db
from . import models
from .schemas import AuditCreate, AuditOut, AuditDetail, HeadcoreConfigOut
from ..worker.worker import celery_app
from .auth import require_jwt
from fastapi import Depends
from ..audit.headcore import build_config, sign_config

app = FastAPI(title=settings.app_name, version="0.1.0")

origins = [o.strip() for o in settings.allow_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    # Create tables if not present (dev convenience)
    from sqlalchemy import create_engine
    from .models import Base
    from .settings import settings as s
    engine = create_engine(s.database_url, connect_args={"check_same_thread": False} if s.database_url.startswith("sqlite") else {})
    Base.metadata.create_all(engine)

@app.post("/api/audits", response_model=AuditOut, dependencies=[Depends(require_jwt)])
def create_audit(payload: AuditCreate, db: Session = Depends(get_db)):
    aid = str(uuid.uuid4())
    a = models.Audit(
        id=aid,
        client_id=payload.locationId,
        contact_id=payload.contactId,
        url=payload.url,
        audit_types=payload.types,
        status="queued"
    )
    db.add(a)
    db.commit()
    # enqueue celery
    celery_app.send_task("audit.run", args=[aid])
    return {"id": aid, "status": "queued"}

@app.get("/api/audits/{audit_id}", response_model=AuditDetail, dependencies=[Depends(require_jwt)])
def get_audit(audit_id: str, db: Session = Depends(get_db)):
    a = db.query(models.Audit).filter(models.Audit.id == audit_id).one_or_none()
    if not a:
        raise HTTPException(404, "Not found")
    return {
        "id": a.id,
        "url": a.url,
        "types": a.audit_types or [],
        "status": a.status,
        "scores": {
            "overall": a.overall_score,
            "performance": a.lighthouse_perf,
            "accessibility": a.lighthouse_accessibility,
            "best_practices": a.lighthouse_best_practices,
            "seo": a.lighthouse_seo
        },
        "summary": a.summary,
        "report_url": a.report_url
    }

@app.post("/api/audits/{audit_id}/headcore", response_model=HeadcoreConfigOut, dependencies=[Depends(require_jwt)])
def generate_headcore_config(audit_id: str, db: Session = Depends(get_db)):
    a = db.query(models.Audit).filter(models.Audit.id == audit_id).one_or_none()
    if not a:
        raise HTTPException(404, "Not found")
    cfg = build_config(a.url, {
        "performance": a.lighthouse_perf,
        "accessibility": a.lighthouse_accessibility,
        "best_practices": a.lighthouse_best_practices,
        "seo": a.lighthouse_seo
    })
    if not settings.headcore_private_key:
        raise HTTPException(400, "HEADCORE_PRIVATE_KEY not configured")
    cfg = sign_config(cfg, settings.headcore_private_key)
    return cfg
