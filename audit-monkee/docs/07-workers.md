# Workers & Queue

- **Backend**: FastAPI (or Node) + Celery/RQ workers
- **Jobs**: Lighthouse run (headless), PSI fetch, tech fingerprint, SEO checks
- **Concurrency**: tuned per Render plan; job timeout & retries
- **Idempotency**: dedupe based on (url, contact, types, day)
