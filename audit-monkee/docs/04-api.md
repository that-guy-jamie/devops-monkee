# API Surface

## Public (app frontend → backend)
- `POST /api/audits`  
  **Body**: `{ contactId, locationId, url, types[] }`  
  **Resp**: `{ auditId }`

- `GET /api/audits/{id}` → status, progress, scores
- `GET /api/audits/{id}/report` → presigned URL (PDF)

## Worker responsibilities
- Execute Lighthouse/PSI + SEO/stack checks
- Persist results
- Write back to GHL (note + custom fields + PDF)
