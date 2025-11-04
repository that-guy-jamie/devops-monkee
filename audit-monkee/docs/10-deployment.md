# Deployment (Render)

- **Services**:
  - Web Service (API)
  - Worker (Celery/RQ)
  - Redis (queue)
  - Postgres (data)
- **Env Vars**: `GHL_CLIENT_ID`, `GHL_CLIENT_SECRET`, `JWT_SECRET`, `REDIS_URL`, `DATABASE_URL`
- **Migrations**: Alembic (if Python) or Prisma/Knex (Node)
