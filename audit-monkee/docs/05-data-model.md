# Data Model (Postgres)

```sql
CREATE TABLE audits (
  id UUID PRIMARY KEY,
  client_id VARCHAR(50),
  contact_id VARCHAR(64) NOT NULL,
  url TEXT NOT NULL,
  audit_types TEXT[],
  overall_score INT,
  lighthouse_perf INT,
  lighthouse_accessibility INT,
  lighthouse_best_practices INT,
  lighthouse_seo INT,
  cwv_json JSONB,
  tech_stack_json JSONB,
  summary TEXT,
  report_url TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  status TEXT CHECK (status IN ('queued','running','done','failed')) NOT NULL
);

CREATE TABLE audit_findings (
  id BIGSERIAL PRIMARY KEY,
  audit_id UUID REFERENCES audits(id) ON DELETE CASCADE,
  category TEXT,
  severity TEXT,
  code TEXT,
  message TEXT,
  target TEXT,
  extra JSONB
);
```
