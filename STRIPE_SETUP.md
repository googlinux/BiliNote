# Stripe Integration Setup Guide

Complete guide for setting up Stripe payment integration for BiliNote SaaS.

## Table of Contents

1. [Stripe Account Setup](#stripe-account-setup)
2. [Product and Pricing Configuration](#product-and-pricing-configuration)
3. [API Keys Configuration](#api-keys-configuration)
4. [Webhook Setup](#webhook-setup)
5. [Testing](#testing)
6. [Going Live](#going-live)

---

## Stripe Account Setup

### 1. Create Stripe Account

1. Visit https://stripe.com
2. Click "Start now" or "Sign up"
3. Fill in your business details
4. Verify your email address
5. Complete identity verification (required for live payments)

### 2. Business Information

Complete your business profile:
- Business name: BiliNote
- Business type: SaaS/Software
- Business description: AI-powered video note generation platform
- Business website: https://your-domain.com

### 3. Banking Information

To receive payouts, add your bank account:
1. Go to Settings → Bank accounts and scheduling
2. Click "Add bank account"
3. Enter your banking details
4. Verify with micro-deposits (if required)

---

## Product and Pricing Configuration

### Create Products in Stripe Dashboard

Go to **Products** → **Add product**

### 1. Basic Plan

**Product Details:**
- Name: `Basic`
- Description: `Perfect for individuals getting started with AI note-taking`
- Statement descriptor: `BILINOTE BASIC`

**Monthly Price:**
1. Click "Add pricing"
2. Pricing model: Standard pricing
3. Price: `$9.00 USD`
4. Billing period: Monthly
5. Save and copy the **Price ID** (e.g., `price_xxx123`)
6. Set as `STRIPE_PRICE_BASIC_MONTHLY` in your `.env`

**Yearly Price:**
1. Click "Add another price"
2. Price: `$99.00 USD`
3. Billing period: Yearly
4. Save and copy the **Price ID**
5. Set as `STRIPE_PRICE_BASIC_YEARLY` in your `.env`

### 2. Pro Plan

**Product Details:**
- Name: `Pro`
- Description: `Advanced features for power users and content creators`
- Statement descriptor: `BILINOTE PRO`

**Monthly Price:**
- Price: `$29.00 USD`
- Billing period: Monthly
- Copy Price ID → `STRIPE_PRICE_PRO_MONTHLY`

**Yearly Price:**
- Price: `$319.00 USD` (save $29)
- Billing period: Yearly
- Copy Price ID → `STRIPE_PRICE_PRO_YEARLY`

### 3. Enterprise Plan

**Product Details:**
- Name: `Enterprise`
- Description: `Unlimited access for teams and businesses`
- Statement descriptor: `BILINOTE ENTER`

**Monthly Price:**
- Price: `$99.00 USD`
- Billing period: Monthly
- Copy Price ID → `STRIPE_PRICE_ENTERPRISE_MONTHLY`

**Yearly Price:**
- Price: `$1089.00 USD` (save $99)
- Billing period: Yearly
- Copy Price ID → `STRIPE_PRICE_ENTERPRISE_YEARLY`

### Summary of Price IDs

After creating all products, you should have 6 Price IDs:

```env
STRIPE_PRICE_BASIC_MONTHLY=price_xxx123
STRIPE_PRICE_BASIC_YEARLY=price_xxx456
STRIPE_PRICE_PRO_MONTHLY=price_xxx789
STRIPE_PRICE_PRO_YEARLY=price_xxxabc
STRIPE_PRICE_ENTERPRISE_MONTHLY=price_xxxdef
STRIPE_PRICE_ENTERPRISE_YEARLY=price_xxxghi
```

Add these to your backend `.env` file.

---

## API Keys Configuration

### 1. Get API Keys

1. Go to **Developers** → **API keys**
2. You'll see two types of keys:

**Test Mode Keys** (for development):
- Publishable key: `pk_test_xxx`
- Secret key: `sk_test_xxx`

**Live Mode Keys** (for production):
- Publishable key: `pk_live_xxx`
- Secret key: `sk_live_xxx`

### 2. Configure Environment Variables

**Development (.env.development):**
```env
STRIPE_API_KEY=sk_test_your_test_secret_key
```

**Production (.env.production):**
```env
STRIPE_API_KEY=sk_live_your_live_secret_key
```

**Important Security Notes:**
- ✅ Secret keys should ONLY be used on the backend
- ✅ Never commit secret keys to Git
- ✅ Use environment variables
- ✅ Rotate keys if compromised
- ❌ Never expose secret keys in frontend code
- ❌ Never hardcode keys in your source code

---

## Webhook Setup

Webhooks notify your backend when payment events occur (e.g., successful payment, subscription cancelled).

### 1. Create Webhook Endpoint

1. Go to **Developers** → **Webhooks**
2. Click **Add endpoint**

### 2. Configure Endpoint

**Endpoint URL:**
- Development: `https://your-ngrok-url.ngrok.io/api/payment/webhook`
- Production: `https://api.your-domain.com/api/payment/webhook`

**Events to listen to:**
Select the following events:

- ✅ `checkout.session.completed` - Payment successful
- ✅ `customer.subscription.updated` - Subscription changed
- ✅ `customer.subscription.deleted` - Subscription cancelled
- ✅ `invoice.payment_succeeded` - Recurring payment successful
- ✅ `invoice.payment_failed` - Payment failed

**API Version:**
- Use latest version (2024-11-20 or newer)

### 3. Get Webhook Secret

After creating the endpoint:
1. Click on your webhook endpoint
2. Click "Reveal" next to "Signing secret"
3. Copy the secret (starts with `whsec_`)
4. Add to your `.env`:

```env
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

### 4. Webhook Security

The webhook endpoint in `backend/app/routers/payment.py` automatically:
- Verifies the webhook signature
- Prevents replay attacks
- Validates the event source

**Never skip webhook verification in production!**

---

## Testing

### 1. Use Stripe Test Mode

Ensure you're in **Test Mode** (toggle in top-right of Stripe Dashboard).

### 2. Test Cards

Use these test card numbers:

**Successful Payments:**
- Card: `4242 4242 4242 4242`
- Any future expiry date (e.g., 12/34)
- Any 3-digit CVC
- Any postal code

**Declined Payments:**
- Card: `4000 0000 0000 0002` (Generic decline)
- Card: `4000 0000 0000 9995` (Insufficient funds)

**3D Secure Required:**
- Card: `4000 0025 0000 3155`

### 3. Test Checkout Flow

1. **Start Local Backend:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Start Local Frontend:**
   ```bash
   cd saas-web
   pnpm dev
   ```

3. **Test Subscription:**
   - Login to your app
   - Navigate to billing settings
   - Click "Subscribe Monthly" on Basic plan
   - Use test card `4242 4242 4242 4242`
   - Complete checkout
   - Verify redirect to success page
   - Check Stripe Dashboard → Customers

4. **Verify Database:**
   ```sql
   SELECT * FROM subscriptions WHERE stripe_customer_id IS NOT NULL;
   SELECT * FROM invoices ORDER BY created_at DESC;
   ```

### 4. Test Webhooks Locally

**Option 1: Stripe CLI (Recommended)**

1. Install Stripe CLI:
   ```bash
   brew install stripe/stripe-cli/stripe
   # or
   scoop install stripe
   ```

2. Login:
   ```bash
   stripe login
   ```

3. Forward webhooks to local backend:
   ```bash
   stripe listen --forward-to localhost:8483/api/payment/webhook
   ```

4. Copy the webhook signing secret and add to `.env`:
   ```env
   STRIPE_WEBHOOK_SECRET=whsec_xxx
   ```

5. Trigger test events:
   ```bash
   stripe trigger checkout.session.completed
   stripe trigger invoice.payment_succeeded
   ```

**Option 2: ngrok**

1. Install ngrok: https://ngrok.com/download

2. Expose local backend:
   ```bash
   ngrok http 8483
   ```

3. Copy the ngrok URL (e.g., `https://abc123.ngrok.io`)

4. Create webhook in Stripe Dashboard:
   - Endpoint URL: `https://abc123.ngrok.io/api/payment/webhook`
   - Select events
   - Copy webhook secret

5. Test by making real purchases with test cards

### 5. Test Customer Portal

1. Create a subscription (using test card)
2. Navigate to billing settings
3. Click "Manage Billing"
4. Verify you can:
   - Update payment method
   - View invoices
   - Cancel subscription
   - Reactivate subscription

---

## Going Live

### 1. Pre-Launch Checklist

- [ ] Complete Stripe account verification
- [ ] Add bank account for payouts
- [ ] Create live products and prices
- [ ] Copy live Price IDs to production `.env`
- [ ] Switch to live API keys
- [ ] Create live webhook endpoint
- [ ] Test with real card (small amount)
- [ ] Set up monitoring (Stripe Dashboard)

### 2. Switch to Live Mode

1. **In Stripe Dashboard:**
   - Toggle from "Test Mode" to "Live Mode" (top right)

2. **Update Backend `.env`:**
   ```env
   STRIPE_API_KEY=sk_live_your_live_secret_key
   STRIPE_WEBHOOK_SECRET=whsec_your_live_webhook_secret
   STRIPE_PRICE_BASIC_MONTHLY=price_live_xxx
   STRIPE_PRICE_BASIC_YEARLY=price_live_xxx
   STRIPE_PRICE_PRO_MONTHLY=price_live_xxx
   STRIPE_PRICE_PRO_YEARLY=price_live_xxx
   STRIPE_PRICE_ENTERPRISE_MONTHLY=price_live_xxx
   STRIPE_PRICE_ENTERPRISE_YEARLY=price_live_xxx
   ```

3. **Deploy Backend:**
   - Push changes to production
   - Verify environment variables are set
   - Test /health endpoint

4. **Create Live Webhook:**
   - Go to Developers → Webhooks (in Live Mode)
   - Add endpoint: `https://api.your-domain.com/api/payment/webhook`
   - Select the same events as test mode
   - Copy webhook secret to production `.env`

### 3. Final Verification

1. **Make a Real Purchase:**
   - Use your own credit card
   - Subscribe to Basic plan ($9)
   - Complete checkout
   - Verify webhook received
   - Check subscription in database
   - Check invoice created
   - Cancel immediately if needed

2. **Monitor Stripe Dashboard:**
   - View Customers
   - View Subscriptions
   - View Payments
   - Check webhook logs

3. **Test Full Flow:**
   - New user signup
   - Subscribe to paid plan
   - Generate notes (verify quota)
   - Access customer portal
   - Cancel subscription
   - Verify downgrade to free plan

### 4. Enable Radar (Fraud Prevention)

1. Go to **Radar** in Stripe Dashboard
2. Review default rules
3. Enable recommended fraud rules
4. Set up email alerts for suspicious activity

### 5. Set Up Billing Alerts

1. Go to **Settings** → **Billing**
2. Enable email notifications for:
   - Failed payments
   - Successful payments
   - Subscription cancellations
   - Disputes

---

## Monitoring & Maintenance

### Daily Tasks

- Review Stripe Dashboard for failed payments
- Check webhook delivery status
- Monitor subscription churn rate

### Weekly Tasks

- Review fraud alerts
- Analyze revenue reports
- Check for disputes/chargebacks

### Monthly Tasks

- Reconcile Stripe revenue with database
- Review and optimize pricing
- Analyze subscription metrics
- Test webhook endpoints

---

## Common Issues & Solutions

### Issue: Webhook Not Receiving Events

**Solution:**
1. Check webhook URL is publicly accessible
2. Verify webhook secret matches `.env`
3. Check webhook logs in Stripe Dashboard
4. Test with Stripe CLI: `stripe listen --forward-to localhost:8483/api/payment/webhook`

### Issue: Signature Verification Failed

**Solution:**
1. Ensure you're reading raw request body
2. Don't parse JSON before verification
3. Check webhook secret is correct
4. Verify Stripe-Signature header is present

### Issue: Customer Not Created

**Solution:**
1. Check STRIPE_API_KEY is set
2. Verify API key has correct permissions
3. Review backend logs for errors
4. Test with Stripe API directly

### Issue: Price ID Not Found

**Solution:**
1. Verify Price IDs in `.env` match Stripe Dashboard
2. Ensure you're using correct mode (test vs live)
3. Check product is active in Stripe Dashboard

---

## Support Resources

- **Stripe Documentation**: https://stripe.com/docs
- **Stripe API Reference**: https://stripe.com/docs/api
- **Stripe Support**: https://support.stripe.com
- **Stripe Discord**: https://discord.gg/stripe
- **Testing Guide**: https://stripe.com/docs/testing

---

## Security Best Practices

1. ✅ Always verify webhook signatures
2. ✅ Use HTTPS in production
3. ✅ Store API keys in environment variables
4. ✅ Use separate test and live keys
5. ✅ Rotate keys regularly
6. ✅ Implement rate limiting
7. ✅ Log all payment events
8. ✅ Enable Stripe Radar
9. ✅ Set up fraud alerts
10. ✅ Regularly review access logs

---

**Last Updated**: 2025-11-07

For technical support with BiliNote integration, please refer to the main DEPLOYMENT.md guide.
