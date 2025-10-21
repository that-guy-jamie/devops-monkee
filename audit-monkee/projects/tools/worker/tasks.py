import uuid, json, logging
from celery import Celery
from datetime import datetime
from .util import SessionLocal
from ..api.models import Audit, AuditFinding
from ..audit.lighthouse import run_lighthouse
from ..audit.seo import run_seo_checks
from ..audit.tech import detect_stack
from ..api.pdf import generate_pdf
from ..api.ghclient import GHLClient

logger = logging.getLogger(__name__)

celery_app: Celery = None

def init_celery(celery: Celery):
    global celery_app
    celery_app = celery

@celery_app.task(name="audit.run")
def run_audit_task(audit_id: str):
    db = SessionLocal()
    try:
        audit = db.query(Audit).filter(Audit.id == audit_id).one()
        audit.status = "running"
        db.commit()

        lh = run_lighthouse(audit.url)
        seo = run_seo_checks(audit.url)
        tech = detect_stack(audit.url)

        audit.lighthouse_perf = lh.get("performance")
        audit.lighthouse_accessibility = lh.get("accessibility")
        audit.lighthouse_best_practices = lh.get("best_practices")
        audit.lighthouse_seo = lh.get("seo")
        audit.cwv_json = lh.get("cwv")
        audit.tech_stack_json = tech
        audit.overall_score = int(round(sum([audit.lighthouse_perf, audit.lighthouse_accessibility, audit.lighthouse_best_practices, audit.lighthouse_seo]) / 4))
        audit.summary = f"Overall score {audit.overall_score}. Perf {audit.lighthouse_perf}, Acc {audit.lighthouse_accessibility}, BP {audit.lighthouse_best_practices}, SEO {audit.lighthouse_seo}."
        db.commit()

        # Compile complete audit data for PDF generation
        audit_data = {
            "overall_score": audit.overall_score,
            "lighthouse_perf": audit.lighthouse_perf,
            "lighthouse_accessibility": audit.lighthouse_accessibility,
            "lighthouse_best_practices": audit.lighthouse_best_practices,
            "lighthouse_seo": audit.lighthouse_seo,
            "cwv": audit.cwv_json or {},
            "seo": seo or {},
            "tech": tech or {},
            "summary": audit.summary
        }

        # Write PDF with complete audit data
        pdf_path = generate_pdf(audit.id, audit_data)

        # GHL write-back
        gh = GHLClient()
        gh.create_contact_note(audit.contact_id, audit.summary or "")
        gh.upsert_contact_custom_fields(audit.client_id or '', audit.contact_id, {
            "audit_monkee_score": audit.overall_score,
            "audit_monkee_perf": audit.lighthouse_perf,
            "audit_monkee_accessibility": audit.lighthouse_accessibility,
            "audit_monkee_best_practices": audit.lighthouse_best_practices,
            "audit_monkee_seo": audit.lighthouse_seo,
            "audit_monkee_schema_found": seo.get('schema_detected', False) if seo else False,
            "audit_monkee_stack": ", ".join(tech.get('cms', [])) if tech else "Unknown",
            "audit_monkee_last_run": datetime.utcnow().isoformat()
        })

        # Upload PDF and store URL
        try:
            media_result = gh.upload_media(pdf_path)
            pdf_url = media_result.get('url', pdf_path)
        except Exception as e:
            logger.error(f"Failed to upload PDF: {e}")
            pdf_url = pdf_path

        audit.report_url = pdf_url
        audit.status = "done"
        db.commit()
    except Exception as e:
        audit = db.query(Audit).filter(Audit.id == audit_id).one_or_none()
        if audit:
            audit.status = "failed"
            audit.summary = f"Error: {e}"
            db.commit()
        raise
    finally:
        db.close()
