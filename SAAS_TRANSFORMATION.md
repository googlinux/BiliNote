# 🚀 BiliNote SaaS Transformation Plan & Progress

## 📊 Project Overview

**Goal**: Transform BiliNote from a self-hosted tool into a global SaaS platform

**Target Audience**: Global users (English-first)
**Pricing Model**: Subscription-based (USD)
**Payment Gateway**: Stripe (International focus)

---

## ✅ Phase 5: Landing Page - **COMPLETED**

### What's Been Built

#### 1. **Modern Landing Page** (`/saas-web`)
A conversion-optimized, fully responsive landing page with:

**Sections:**
- ✅ **Hero Section**: Clear value proposition with CTA buttons
- ✅ **Features Section**: 6 key features with icons
- ✅ **Pricing Section**: 4-tier pricing with monthly/yearly toggle
- ✅ **FAQ Section**: 8 common questions with accordion UI
- ✅ **CTA Section**: Strong call-to-action for conversion
- ✅ **Navigation**: Sticky navbar with mobile menu
- ✅ **Footer**: Links, social media, branding

**Pages:**
- ✅ Landing page: `/` (http://localhost:3000)
- ✅ Login page: `/auth/login`
- ✅ Register page: `/auth/register`

#### 2. **Pricing Tiers (USD)**

| Plan | Price | Features |
|------|-------|----------|
| **Free** | $0/mo | 5 videos/mo, 10min limit, Basic AI |
| **Basic** | $9/mo | 100 videos, 30min, GPT-4, Screenshots |
| **Pro** | $29/mo | 500 videos, 2hr, Multi-modal, Mind maps, API |
| **Enterprise** | $99/mo | Unlimited, Custom AI, Team features, SSO |

*Yearly plans: 20% discount ($86, $278, $950/year)*

#### 3. **Tech Stack**

```
Frontend: Next.js 16 + React 19 + TypeScript
Styling: Tailwind CSS v4
Components: Shadcn UI + Radix UI
Icons: Lucide React
Fonts: Geist Sans + Geist Mono
Features: Dark mode, Responsive, SEO-ready
```

#### 4. **Design Features**

- ✅ Mobile-first responsive design
- ✅ Automatic dark mode (system preference)
- ✅ Smooth animations and transitions
- ✅ Accessible UI (ARIA, keyboard navigation)
- ✅ Fast loading (Next.js optimization)

---

## 🎯 Next Phases (Pending)

### Phase 1: Database & Auth Backend (3-4 weeks)

**Database Migration:**
- [ ] SQLite → PostgreSQL
- [ ] Multi-tenant schema design
- [ ] User table with authentication
- [ ] Subscription & usage tracking tables

**Authentication System:**
- [ ] JWT token generation & validation
- [ ] User registration API
- [ ] Login/logout endpoints
- [ ] Password reset flow
- [ ] Email verification
- [ ] OAuth integration (Google/GitHub)

**API Endpoints:**
```
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
POST /api/auth/refresh-token
POST /api/auth/verify-email
POST /api/auth/reset-password
GET  /api/user/profile
PUT  /api/user/profile
```

---

### Phase 2: Subscription & Quota System (2-3 weeks)

**Subscription Management:**
- [ ] Pricing plan configuration
- [ ] Subscription creation/renewal
- [ ] Cancellation handling
- [ ] Upgrade/downgrade logic

**Quota System:**
- [ ] Pre-task quota validation
- [ ] Real-time usage tracking
- [ ] Quota exceeded handling
- [ ] Usage statistics

**API Endpoints:**
```
GET  /api/subscription/plans
POST /api/subscription/subscribe
POST /api/subscription/cancel
GET  /api/subscription/current
GET  /api/subscription/usage
GET  /api/subscription/invoices
```

---

### Phase 3: Stripe Payment Integration (2 weeks)

**Payment Flow:**
- [ ] Stripe SDK integration
- [ ] Checkout session creation
- [ ] Webhook handling (payment success/failure)
- [ ] Invoice generation
- [ ] Refund processing

**Payment Methods:**
- [ ] Credit/Debit cards (via Stripe)
- [ ] Apple Pay / Google Pay
- [ ] International cards support

**API Endpoints:**
```
POST /api/payment/create-checkout
POST /api/payment/webhook
GET  /api/payment/status/{order_id}
POST /api/payment/cancel-subscription
```

---

### Phase 4: Dashboard UI (4-5 weeks)

**Dashboard Layout:**
- [ ] Sidebar navigation
- [ ] Top bar (search, notifications, user menu)
- [ ] Responsive mobile drawer

**Pages:**
```
/dashboard              - Overview & quick stats
/dashboard/notes        - Notes list (grid/list view)
/dashboard/notes/new    - Create new note (existing HomePage)
/dashboard/notes/{id}   - Note detail view
/dashboard/settings     - User settings
  ├─ /profile          - Profile & avatar
  ├─ /subscription     - Plan & billing
  ├─ /billing          - Invoice history
  ├─ /models           - AI model config (Pro+)
  └─ /api-keys         - API keys (Pro+)
/dashboard/usage        - Usage statistics
```

**Components:**
- [ ] QuotaCard (usage indicator)
- [ ] NotesGrid (card/list modes)
- [ ] UsageChart (daily/monthly stats)
- [ ] SubscriptionPanel (upgrade prompts)

---

### Phase 5: Backend API Refactoring (2-3 weeks)

**Core Changes:**
- [ ] Add JWT authentication middleware
- [ ] Implement quota checking before processing
- [ ] Multi-tenant data isolation
- [ ] Platform-managed API keys (user-level override for Enterprise)

**Modified Services:**
```python
# backend/app/services/note.py
class NoteGenerator:
    async def generate(request, user_id):
        1. Check user authentication
        2. Validate subscription & quota
        3. Check feature access (screenshots, multi-modal, etc.)
        4. Execute generation
        5. Deduct quota
        6. Save to user's space
```

**Database Models:**
- [ ] Add `user_id` foreign key to all relevant tables
- [ ] Row-level security for data isolation

---

### Phase 6: Deployment & Infrastructure (2 weeks)

**Backend:**
- [ ] PostgreSQL (AWS RDS / Supabase)
- [ ] Redis (ElastiCache / Upstash)
- [ ] Celery workers (ECS / Railway)
- [ ] Object storage (S3 / Cloudflare R2)

**Frontend:**
- [ ] Vercel deployment (Next.js)
- [ ] Custom domain setup
- [ ] CDN configuration

**Monitoring:**
- [ ] Sentry (error tracking)
- [ ] Prometheus + Grafana (metrics)
- [ ] Logs (CloudWatch / Datadog)

---

## 📈 Project Timeline

```
Week 1-4   ██████████ Phase 1: Database & Auth
Week 5-7   ██████████ Phase 2: Subscription & Quota
Week 8-10  ██████████ Phase 3: Stripe Integration
Week 11-15 ██████████ Phase 4: Dashboard UI
Week 16-18 ██████████ Phase 5: Backend Refactoring
Week 19-20 ██████████ Phase 6: Deployment

Total: 20 weeks (~5 months)
```

---

## 🎨 Landing Page Preview

**Live URL (Development)**: http://localhost:3000

**Screenshots Available At:**
- Hero: Professional, clear value prop
- Features: 6 key features with icons
- Pricing: 4 tiers with toggle
- FAQ: Accordion-style Q&A
- CTA: Strong conversion sections

**Design Highlights:**
- Clean, modern aesthetics
- Consistent branding
- Mobile-optimized
- Fast loading
- SEO-ready structure

---

## 💰 Revenue Projections

**Assumptions:**
- 1,000 users in Month 3
- 5% conversion to paid (50 users)
- Average plan: $19/mo

**Monthly Recurring Revenue (MRR):**
- Month 3: $950 (50 users × $19)
- Month 6: $3,800 (200 users × $19)
- Month 12: $11,400 (600 users × $19)

**Annual Run Rate (ARR) at Month 12:**
$136,800/year

---

## 🔐 Security Considerations

**Implemented:**
- ✅ HTTPS ready
- ✅ TypeScript for type safety
- ✅ Secure form handling

**To Implement:**
- [ ] JWT token encryption
- [ ] Password hashing (bcrypt)
- [ ] Rate limiting
- [ ] CORS configuration
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF tokens
- [ ] Webhook signature verification (Stripe)

---

## 📝 Documentation Status

**Completed:**
- ✅ Landing page code
- ✅ Component documentation (inline)
- ✅ README for saas-web

**Pending:**
- [ ] API documentation (Swagger/OpenAPI)
- [ ] User guide
- [ ] Developer docs
- [ ] Deployment guide

---

## 🚀 How to Run Locally

### Landing Page (Already Running)

```bash
cd saas-web
pnpm install
pnpm dev
# Open http://localhost:3000
```

### Original Backend (For Reference)

```bash
cd backend
pip install -r requirements.txt
python main.py
# Runs on http://localhost:8483
```

---

## 🔄 Git Workflow

**Branch**: `claude/saas-website-redesign-011CUXz7Jyrjvkvb1Ut8E9P6`

**Latest Commit**:
```
feat: Add SaaS Landing Page with Next.js

✨ Features:
- Modern Landing Page with all sections
- Auth pages (Login/Register UI)
- Fully responsive + dark mode
- USD pricing ($9/$29/$99)
```

**Remote**: https://github.com/googlinux/BiliNote

---

## 📞 Next Steps & Decisions Needed

1. **Approval on Landing Page Design**
   - Review at http://localhost:3000
   - Provide feedback on design/copy
   - Confirm pricing tiers

2. **Backend Technology Choices**
   - Database: PostgreSQL (AWS RDS vs Supabase)?
   - Cache: Redis (ElastiCache vs Upstash)?
   - Queue: Celery (self-hosted vs Railway)?

3. **Hosting Platform**
   - Frontend: Vercel (recommended)
   - Backend: AWS ECS / Railway / Fly.io?
   - Storage: S3 / Cloudflare R2?

4. **Start Phase 1?**
   - Once landing page is approved
   - Begin database schema design
   - Set up PostgreSQL instance

---

## 📊 Success Metrics (KPIs)

**User Acquisition:**
- [ ] 1,000 signups in Month 1
- [ ] 5% free-to-paid conversion
- [ ] 40% 30-day retention

**Technical:**
- [ ] API response time < 500ms (P99)
- [ ] 99.9% uptime
- [ ] Task success rate > 95%

**Business:**
- [ ] MRR growth: 20% month-over-month
- [ ] Customer Acquisition Cost (CAC) < $50
- [ ] Lifetime Value (LTV) > $300

---

## 🎉 Current Status

✅ **Phase 5 COMPLETE**: Landing Page Ready for Review

**What You Can Do Now:**
1. Visit http://localhost:3000 to preview the landing page
2. Test navigation, pricing toggles, and responsive design
3. Review copy and CTAs
4. Provide feedback for any adjustments

**What's Next:**
Once you approve the landing page, I'll immediately start:
- Phase 1: Database schema design
- Phase 2: User authentication backend
- Phase 3: Stripe integration

**Estimated Time to MVP**: 12-16 weeks

---

**Questions? Let's discuss the next phase!** 🚀
