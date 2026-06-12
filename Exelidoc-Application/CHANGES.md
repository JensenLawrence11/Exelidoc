# Changes Summary: Original → Subscription Model

## Files

| File | Old | New |
|------|-----|-----|
| Backend | `backend/main.py` | `backend/main_production.py` |
| Frontend | `addin/taskpane.html` | `addin/taskpane_production.html` |

---

## Key Changes

### Backend (`main_production.py`)

#### Removed ❌
- User-provided API keys (Settings tab input)
- No authentication/user tracking
- No token limits

#### Added ✅
- **Hard-coded API keys** — only your keys, users can't override
- **SQLite database** — tracks users, token usage, and call logs
- **User signup** — automatic account creation on first login
- **Token tracking** — deducts tokens from users' monthly allowance
- **Rate limiting** — rejects requests when user exceeds limit
- **Subscription tiers** — free (10k), pro (100k), enterprise (1M) tokens/month
- **X-User-ID header** — required authentication on all requests
- **Usage endpoint** — `/usage/{user_id}` shows remaining tokens

#### Database
New `office_ai.db` created automatically with tables:
- `users` — user accounts & subscription tier
- `usage` — monthly token count per user
- `logs` — detailed call records for analytics

---

### Frontend (`taskpane_production.html`)

#### Removed ❌
- Settings tab (no user API key input)
- Provider selection UI (always uses Anthropic Claude in demo)
- Local/Cloud mode toggle (simplified for demo)

#### Added ✅
- **Account tab** — sign in, view usage, upgrade plan
- **Token usage bar** — real-time progress bar showing consumption
- **User info display** — tier, tokens used, limit, remaining
- **Login/logout** — required before making requests
- **Upgrade link** — directs to billing (you customize)
- **localStorage** — remembers user ID across sessions

---

## Business Model

### Before
- Users provide their own API keys
- No usage tracking
- No way to monetize

### After
- **You own the API keys** and the token budget
- **Users sign up for free** (10k tokens/month)
- **You charge for upgrades** (Pro = $5/mo, Enterprise = $20/mo, etc.)
- **Monthly token limit enforcement** — prevents unexpected costs
- **Token usage tracking** — see who's using what, for analytics

---

## Setup Checklist

Before you launch:

- [ ] **Add your API keys** to `API_KEYS` dict in `main_production.py`
- [ ] **Change JWT_SECRET** to a random string
- [ ] **Update subscription tier limits** if needed (currently 10k/100k/1M)
- [ ] **Test locally** with the Account tab sign-in flow
- [ ] **Check database** — run `sqlite3 office_ai.db` to inspect
- [ ] **Update manifest.xml** to point to `taskpane_production.html`
- [ ] **Plan monetization** — when will users upgrade?

---

## API Key Protection

Your keys are **never exposed to users**:

```
User Request → Frontend (add-in) → Backend (your server, has API key) → OpenAI/Anthropic/Gemini
```

Frontend doesn't know or have access to API keys. Safe! ✓

---

## Token Counting

Tokens are estimated per request:

- **Input tokens** — characters in user's prompt
- **Output tokens** — characters in AI response
- **Rough formula** — ~4 characters per token (varies by provider)

Anthropic API returns exact token counts; others are estimated. You can adjust in code.

---

## Data in SQLite

Example query to see all usage:

```bash
sqlite3 office_ai.db
```

```sql
-- Top users by token consumption
SELECT user_id, SUM(tokens_used) as total 
FROM logs 
GROUP BY user_id 
ORDER BY total DESC;

-- Usage by month
SELECT user_id, month_year, tokens_used 
FROM usage 
ORDER BY month_year DESC;

-- API call history
SELECT timestamp, user_id, provider, tokens_used 
FROM logs 
ORDER BY timestamp DESC;
```

---

## What's the Same

✓ All AI providers work (OpenAI, Anthropic, Gemini)  
✓ Local Ollama support (if Ollama is running)  
✓ Office.js integration (Word, Excel, PowerPoint)  
✓ Copy/Insert/Clear buttons  
✓ Quick action tools (Summarize, Fix Grammar, etc.)  
✓ Same UI design & polish  

---

## Next Steps

1. **Immediately**: Add your API keys and test locally
2. **Soon**: Build a pricing page on your website
3. **Later**: Add Stripe integration for actual billing
4. **Eventually**: Submit to Microsoft AppSource for distribution

Good to go! 🚀
