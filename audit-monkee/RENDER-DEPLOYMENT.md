# Render Deployment Guide

## Overview

Audit Monkee uses a multi-service Render architecture:
- **Web Service**: FastAPI application (free tier)
- **Background Worker**: Celery worker for audit processing (free tier)
- **PostgreSQL Database**: Data storage (free tier - 1GB)
- **Redis Cache**: Task queue and caching (free tier - 256MB)

## Step 1: Create Render Account

1. Go to [render.com](https://render.com) and sign up for a free account
2. Verify your email address

## Step 2: Connect GitLab Repository

1. In Render dashboard, click "New +" → "Blueprint"
2. Connect your GitLab repository (the one you just created)
3. Select the `audit-monkee` repository

## Step 3: Deploy Services

Render will automatically detect the `render.yaml` file and create all services.

### Service Configuration

**Environment Variables** (set these in Render dashboard for each service):

#### Web Service (`audit-monkee-api`)
```bash
JWT_SECRET=<generate-random-string>
PSI_API_KEY=<your-pagespeed-insights-key>
HEADCORE_PRIVATE_KEY=<base64url-ed25519-private-key>
GHL_CLIENT_ID=<your-ghl-oauth-client-id>
GHL_CLIENT_SECRET=<your-ghl-oauth-client-secret>
```

#### Worker Service (`audit-monkee-worker`)
```bash
GHL_ACCESS_TOKEN=<your-ghl-access-token>
PSI_API_KEY=<your-pagespeed-insights-key>
```

## Step 4: Get API Keys

### Google PageSpeed Insights API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "PageSpeed Insights API"
4. Create credentials (API Key)
5. Copy the API key for `PSI_API_KEY`

### GoHighLevel OAuth Setup
1. Go to [GoHighLevel Marketplace Developer Portal](https://marketplace.gohighlevel.com/)
2. Create a new app
3. Set OAuth redirect URI to: `https://your-render-app.onrender.com/oauth/callback`
4. Copy Client ID and Client Secret

### Generate Headcore Keys
```bash
# Generate Ed25519 keypair (run locally)
openssl genpkey -algorithm ed25519 -out private.pem
openssl pkey -in private.pem -pubout -out public.pem

# Convert to base64url for environment variable
base64url -i private.pem | tr -d '=' > headcore_private_key.txt
```

## Step 5: Database Setup

1. After deployment, connect to your PostgreSQL service
2. Run the Alembic migrations:
```bash
cd projects/tools
alembic upgrade head
```

## Step 6: Domain Setup (Optional)

For production, add a custom domain:
1. In Render dashboard, go to your web service settings
2. Add custom domain (e.g., `api.auditmonkee.com`)
3. Update DNS records as instructed

## Step 7: Testing

1. Once deployed, test the API:
```bash
curl https://your-app.onrender.com/api/audits \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{"contactId":"test","url":"https://example.com","types":["seo"]}'
```

2. Check worker logs in Render dashboard
3. Verify database connectivity

## Monitoring & Logs

- **Web Service Logs**: Application errors and API access
- **Worker Logs**: Audit processing status
- **Database Logs**: Query performance and errors
- **Redis Logs**: Queue processing

## Scaling Considerations

**Current Free Tier Limits:**
- Web Service: 512MB RAM, 0.1 CPU
- Worker: 512MB RAM, 0.1 CPU
- PostgreSQL: 1GB storage
- Redis: 256MB storage

**For Production Scaling:**
- Upgrade to paid tiers for more resources
- Add multiple worker instances
- Implement rate limiting
- Add monitoring and alerting

## Troubleshooting

### Common Issues

**Database Connection Errors:**
- Verify PostgreSQL service is running
- Check DATABASE_URL format
- Ensure migrations are applied

**Worker Not Processing:**
- Check Redis connectivity
- Verify Celery configuration
- Monitor worker logs

**GHL Integration Issues:**
- Verify access tokens are valid
- Check rate limits (100 req/10s burst, 200k/day)
- Test with GHL API playground

## Security Checklist

- [ ] JWT_SECRET is randomly generated (not "change-me")
- [ ] GHL credentials are properly configured
- [ ] Database has strong password
- [ ] API keys are not logged
- [ ] HTTPS is enforced (automatic on Render)
- [ ] Database backups enabled (automatic on Render)

## Costs (Free Tier)

- **Web Service**: $0/month (always free)
- **Background Worker**: $0/month (always free)
- **PostgreSQL**: $0/month (1GB free tier)
- **Redis**: $0/month (256MB free tier)

**Total**: $0/month for basic usage

## Next Steps After Deployment

1. ✅ **Deploy to Render** (this guide)
2. ⏳ **Test all endpoints**
3. ⏳ **Configure monitoring**
4. ⏳ **Set up domain (optional)**
5. ⏳ **Prepare marketplace submission**

---

**Note**: Keep detailed deployment logs and configuration for troubleshooting and scaling.
