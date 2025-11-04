# Triggers & Automation (GHL Cortex/Workflows)

- **Workflow → Webhook (Outbound)** to `POST /api/audits` with `{contactId, locationId, url, types}`
- Re-run weekly or on form submission
- On completion, write a Contact Note and update custom fields
