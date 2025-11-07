# BiliNote SaaS Deployment Guide

This guide covers the deployment process for the BiliNote SaaS platform, including both frontend and backend components.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Configuration](#database-configuration)
4. [Stripe Integration](#stripe-integration)
5. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
6. [Backend Deployment (Railway/AWS)](#backend-deployment)
7. [Post-Deployment Verification](#post-deployment-verification)

---

## Prerequisites

- **Node.js**: v18.0.0 or higher (for frontend)
- **Python**: v3.9 or higher (for backend)
- **PostgreSQL**: v14 or higher (production database)
- **Stripe Account**: For payment processing
- **Git**: For version control

## Environment Setup

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Application
DEBUG=False
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8483

# Database
DATABASE_URL=postgresql://username:password@host:port/database_name

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
REFRESH_TOKEN_EXPIRE_MINUTES=43200

# CORS
FRONTEND_URL=https://your-domain.com

# Stripe
STRIPE_API_KEY=sk_live_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Stripe Price IDs (from Stripe Dashboard)
STRIPE_PRICE_BASIC_MONTHLY=price_xxx
STRIPE_PRICE_BASIC_YEARLY=price_xxx
STRIPE_PRICE_PRO_MONTHLY=price_xxx
STRIPE_PRICE_PRO_YEARLY=price_xxx
STRIPE_PRICE_ENTERPRISE_MONTHLY=price_xxx
STRIPE_PRICE_ENTERPRISE_YEARLY=price_xxx

# Email (Optional - for verification)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=noreply@your-domain.com

# OAuth (Optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### Frontend Environment Variables

Create a `.env.local` file in the `saas-web/` directory:

```env
# API URL
NEXT_PUBLIC_API_URL=https://api.your-domain.com

# Site URL
NEXT_PUBLIC_SITE_URL=https://your-domain.com
```

---

## Database Configuration

### 1. Create PostgreSQL Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE bilinote_saas;

# Create user (optional)
CREATE USER bilinote WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE bilinote_saas TO bilinote;
```

### 2. Run Database Migrations

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Initialize database (creates all tables)
python -m app.db.init_db

# Or use Alembic for migrations (if configured)
alembic upgrade head
```

### 3. Verify Database Schema

The following tables should be created:
- `users` - User accounts
- `subscriptions` - Subscription plans and quotas
- `invoices` - Payment history
- `video_tasks` - Note generation tasks
- `user_videos` - User video library

---

## Stripe Integration

### 1. Create Stripe Account

1. Sign up at https://stripe.com
2. Complete account verification
3. Switch to Live mode (for production)

### 2. Create Products and Prices

Go to Stripe Dashboard → Products → Create product:

**Basic Plan:**
- Name: Basic
- Price: $9.00 USD / month
- Recurring: Monthly
- Copy Price ID → Set as `STRIPE_PRICE_BASIC_MONTHLY`

Repeat for:
- Basic Yearly ($99/year)
- Pro Monthly ($29/month)
- Pro Yearly ($319/year)
- Enterprise Monthly ($99/month)
- Enterprise Yearly ($1089/year)

### 3. Configure Webhook

1. Go to Stripe Dashboard → Developers → Webhooks
2. Click "Add endpoint"
3. Endpoint URL: `https://api.your-domain.com/api/payment/webhook`
4. Select events to listen for:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy webhook secret → Set as `STRIPE_WEBHOOK_SECRET`

### 4. Get API Keys

1. Go to Stripe Dashboard → Developers → API keys
2. Copy "Secret key" → Set as `STRIPE_API_KEY`
3. **Never commit API keys to git!**

---

## Frontend Deployment (Vercel)

### 1. Install Vercel CLI (optional)

```bash
npm i -g vercel
```

### 2. Deploy via Vercel Dashboard

1. Go to https://vercel.com
2. Click "New Project"
3. Import your Git repository
4. Configure:
   - Framework: Next.js
   - Root Directory: `saas-web`
   - Build Command: `pnpm build`
   - Output Directory: `.next`
5. Add environment variables:
   - `NEXT_PUBLIC_API_URL`
   - `NEXT_PUBLIC_SITE_URL`
6. Click "Deploy"

### 3. Configure Custom Domain (optional)

1. Go to Project Settings → Domains
2. Add your custom domain
3. Configure DNS records as instructed

### 4. Verify Deployment

Visit your deployed URL and verify:
- Homepage loads correctly
- Login/Register works
- Dashboard is accessible

---

## Backend Deployment

### Option 1: Railway (Recommended)

1. **Sign up at https://railway.app**

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Select `backend` directory

3. **Add PostgreSQL Database**
   - Click "New" → "Database" → "PostgreSQL"
   - Copy `DATABASE_URL` to environment variables

4. **Configure Environment Variables**
   - Go to Variables tab
   - Add all backend environment variables (from `.env`)

5. **Configure Build**
   - Root Directory: `backend`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

6. **Deploy**
   - Railway will auto-deploy on push to main

### Option 2: AWS Elastic Beanstalk

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB Application**
   ```bash
   cd backend
   eb init -p python-3.9 bilinote-backend
   ```

3. **Create Environment**
   ```bash
   eb create bilinote-prod
   ```

4. **Set Environment Variables**
   ```bash
   eb setenv DEBUG=False DATABASE_URL=postgresql://... STRIPE_API_KEY=sk_live_...
   ```

5. **Deploy**
   ```bash
   eb deploy
   ```

### Option 3: Docker + DigitalOcean/EC2

1. **Create Dockerfile** (if not exists)
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY . .

   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8483"]
   ```

2. **Build Docker Image**
   ```bash
   docker build -t bilinote-backend .
   ```

3. **Push to Registry**
   ```bash
   docker tag bilinote-backend registry.digitalocean.com/your-registry/bilinote-backend
   docker push registry.digitalocean.com/your-registry/bilinote-backend
   ```

4. **Deploy to Server**
   - Use Docker Compose or Kubernetes
   - Configure reverse proxy (Nginx/Caddy)
   - Set up SSL with Let's Encrypt

---

## Post-Deployment Verification

### 1. Health Check

```bash
# Backend health check
curl https://api.your-domain.com/health

# Expected response
{"status": "healthy"}
```

### 2. API Endpoints Test

```bash
# Test registration
curl -X POST https://api.your-domain.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234","full_name":"Test User"}'

# Test login
curl -X POST https://api.your-domain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234"}'
```

### 3. Stripe Webhook Test

1. Go to Stripe Dashboard → Webhooks
2. Select your webhook endpoint
3. Click "Send test webhook"
4. Verify events are received

### 4. Frontend Integration Test

1. Create account on frontend
2. Login to dashboard
3. View subscription details
4. Test checkout flow (use Stripe test cards)
5. Verify customer portal access

### 5. Database Verification

```sql
-- Check users were created
SELECT COUNT(*) FROM users;

-- Check subscriptions were created
SELECT COUNT(*) FROM subscriptions;

-- Check invoices after payment
SELECT * FROM invoices ORDER BY created_at DESC LIMIT 10;
```

---

## Monitoring & Maintenance

### Logging

- **Backend**: Use structured logging with Winston/Loguru
- **Frontend**: Use Vercel Analytics
- **Database**: Enable PostgreSQL query logging

### Error Tracking

Recommended tools:
- Sentry for error tracking
- LogRocket for user session replay
- DataDog for infrastructure monitoring

### Backup Strategy

1. **Database Backups**
   - Daily automated backups
   - Retain for 30 days
   - Test restore procedure monthly

2. **File Backups**
   - Backup uploaded files to S3
   - Backup generated notes

### Security

1. **SSL/TLS**: Ensure HTTPS everywhere
2. **CORS**: Restrict to your domain only
3. **Rate Limiting**: Implement on API endpoints
4. **SQL Injection**: Use parameterized queries (already done with SQLAlchemy)
5. **XSS Protection**: Sanitize user inputs
6. **Secrets**: Never commit to git, use environment variables

---

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check `DATABASE_URL` format
   - Verify database is running
   - Check firewall rules

2. **Stripe Webhook Not Receiving Events**
   - Verify webhook URL is accessible
   - Check webhook secret matches
   - Review Stripe logs

3. **CORS Errors**
   - Verify `FRONTEND_URL` in backend `.env`
   - Check CORS middleware configuration
   - Ensure headers are properly set

4. **Authentication Fails**
   - Check `SECRET_KEY` is set
   - Verify token expiration settings
   - Review JWT token format

---

## Support

For deployment assistance:
- Check GitHub issues
- Review FastAPI documentation: https://fastapi.tiangolo.com
- Review Next.js documentation: https://nextjs.org/docs
- Review Stripe documentation: https://stripe.com/docs

---

**Last Updated**: 2025-11-07
