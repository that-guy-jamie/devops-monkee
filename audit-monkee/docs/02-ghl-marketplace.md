# GHL Marketplace Integration

## Distribution
- App type: **Agency & Sub-account**
- Auth: **OAuth 2.0** (Location token + Agency context)
- On install: store tokens and location/agency IDs

## Embedded App UX
1. Install → OAuth → select location.
2. Open app (iFrame): choose audit type(s) + enter root URL + pick target contact.
3. Run audit: show progress (queued → running → done).
4. Write results back to GHL (note, custom fields, PDF).

## Rate Limits & Safety
- Implement request throttling and exponential backoff.
- Respect daily/burst limits per resource.
