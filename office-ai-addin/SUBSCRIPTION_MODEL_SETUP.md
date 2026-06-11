# Office AI Add-in — Subscription Model Setup

Your backend now operates like **Copilot Pro**: you control the API key, users pay for token access tiers.

---

## 🔧 Configuration (Before Running)

### 1. **Add Your API Keys** to `main_production.py`

Find these lines (~15-18) and replace with your actual keys:

```python
API_KEYS = {
    "openai": "sk-your-openai-key-here",
    "anthropic": "your-anthropic-key-here",
    "gemini": "your-gemini-key-here",
}
```

Get keys from:
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/
- **Google Gemini**: https://aistudio.google.com/app/apikey

### 2. **Set JWT Secret** (for future auth scaling)

Line ~21:
```python
JWT_SECRET = "your-super-secret-key-change-this-in-production"
```

Change this to something random and secure.

---

## 🚀 Running the Backend

```bash
cd backend
pip install -r requirements.txt
python main_production.py
```

Backend runs at `http://localhost:8000`

---

## 📋 How It Works

### User Flow

1. **User opens the add-in** → Account tab appears
2. **User enters ID** (email or username) → signs up automatically
3. **User gets assigned a tier** (defaults to free: 10k tokens/month)
4. **Each AI call deducts tokens** from their monthly allowance
5. **When limit is reached** → requests fail with "upgrade" message

### Token Accounting

Tokens are **tracked in SQLite** (`office_ai.db`):

- **usage table** — monthly token count per user
- **logs table** — detailed call history (for analytics)
- **users table** — user info, subscription tier

Each month (calendar month) resets automatically.

---

## 💳 Subscription Tiers

Define in `main_production.py` (~24-28):

```python
SUBSCRIPTION_TIERS = {
    "free": 10_000,
    "pro": 100_000,
    "enterprise": 1_000_000,
}
```

Adjust limits as needed.

---

## 🔐 Authentication

Currently uses a **simple header-based system**:

```
X-User-ID: user@example.com
```

The add-in sends this in every request. For production, consider:
- OAuth2 / Microsoft Auth
- JWT tokens
- Stripe integration for billing

---

## 📊 API Endpoints (All Requests Need X-User-ID Header)

### Sign Up / Update Tier
```
POST /signup
{
  "user_id": "user@example.com",
  "subscription_tier": "free"  // or "pro" or "enterprise"
}
```

### Check Usage
```
GET /usage/{user_id}
Returns:
{
  "tier": "free",
  "limit": 10000,
  "used": 2500,
  "remaining": 7500
}
```

### Generate AI Response
```
POST /ai/generate
Headers: X-User-ID: user@example.com

{
  "prompt": "summarize this",
  "mode": "cloud",           // "cloud" or "local"
  "provider": "anthropic",   // "openai" | "anthropic" | "gemini"
  "max_tokens": 1024
}

Returns:
{
  "result": "AI response here...",
  "tokens_used": 245,
  "usage": {
    "used": 2745,
    "limit": 10000,
    "remaining": 7255
  }
}
```

---

## 🎨 Frontend (taskpane_production.html)

The HTML file now includes:

- **Account tab** — Sign in, view tier, see token usage
- **Token progress bar** — Visual representation of usage
- **Usage tracking** — Shows remaining tokens after each call
- **Subscription upgrade** — Link to upgrade (you can customize)

The add-in header stays the same, but now requires a user ID to work.

---

## 📦 Manifest.xml Update

Update `addin/manifest.xml` to point to the production HTML:

Change this line:
```xml
<SourceLocation DefaultValue="http://localhost:8000/addin/taskpane.html" />
```

To this:
```xml
<SourceLocation DefaultValue="http://localhost:8000/addin/taskpane_production.html" />
```

---

## 💡 Testing Locally

1. **Start backend**: `python main_production.py`
2. **Load manifest** in Word/Excel
3. **Go to Account tab**
4. **Enter any user ID** (e.g. `test@example.com`)
5. **Sign in** — user is created, defaults to "free" tier
6. **Chat tab** — make AI requests, watch tokens deduct

Check `office_ai.db` to see usage data:

```bash
sqlite3 office_ai.db
SELECT * FROM usage;
SELECT * FROM logs;
```

---

## 🌐 Production Deployment

When you're ready to go live:

1. **Deploy backend** to a server (AWS, Heroku, Azure, etc.)
2. **Update manifest.xml** to point to your server URL
3. **Add HTTPS** (required by Office)
4. **Integrate payment processor** (Stripe, PayPal) for subscriptions
5. **Build a website** with pricing page, sign-up, and billing dashboard
6. **Submit to Microsoft AppSource** (for distribution)

---

## 🔒 Security Checklist

- [ ] Remove `reload=True` from production (`uvicorn.run(...)`)
- [ ] Change `JWT_SECRET` to a real secret
- [ ] Use HTTPS only (add SSL certificate)
- [ ] Lock down CORS to only your domain
- [ ] Hash user IDs if storing emails
- [ ] Validate API keys are set (don't expose them in errors)
- [ ] Rate limit requests to prevent abuse
- [ ] Log all API calls for audit trails
- [ ] Use environment variables for secrets (not hard-coded)

---

## 🎁 What You Could Add

- **Billing integration** (Stripe for recurring subscriptions)
- **Usage analytics dashboard** (see top users, token burn rate, etc.)
- **Referral system** (bonus tokens for inviting friends)
- **API tier per provider** (use cheaper models for free users)
- **Custom system prompts** (user-defined AI behavior)
- **Offline queue** (cache requests, send later if offline)
- **Team accounts** (share token pool across org)

---

## 📞 Support

- Check `office_ai.db` for usage data
- Check logs with: `tail -f server.log`
- Test API directly: `curl -H "X-User-ID: test@example.com" http://localhost:8000/health`

Good luck! This is now a viable SaaS product. 🚀
