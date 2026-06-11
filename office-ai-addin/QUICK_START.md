# Quick Start — Office AI with Subscription Model

## 📋 Files You Have

```
backend/
├── main_production.py     ← Use THIS (subscription model)
├── main.py                ← Old version (ignore)
└── requirements.txt

addin/
├── taskpane_production.html  ← Use THIS (subscription model)
├── taskpane.html            ← Old version (ignore)
├── manifest.xml             ← Same as before
```

---

## ⚡ 3 Steps to Get Running

### Step 1: Add Your API Keys

Open `backend/main_production.py`, find line ~15:

```python
API_KEYS = {
    "openai": "sk-your-openai-key-here",
    "anthropic": "your-anthropic-key-here",
    "gemini": "your-gemini-key-here",
}
```

Replace with real keys from:
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/
- Gemini: https://aistudio.google.com/app/apikey

### Step 2: Start the Backend

```bash
cd backend
pip install -r requirements.txt
python main_production.py
```

You should see:
```
INFO:     Application startup complete
```

### Step 3: Load the Add-in

In Word/Excel/PowerPoint:
- Go to **Insert → Add-ins → Upload My Add-in**
- Select `addin/manifest.xml`
- The panel opens on the right

---

## 🎮 Using It

1. Click the **Account** tab
2. Enter any user ID (e.g., `test@example.com`)
3. Click **Sign In / Sign Up** — user is created automatically
4. Go to **Chat** tab
5. Type a question and hit **Send**
6. Watch your token count decrease in the token bar

---

## 💰 How Users Pay

In the Account tab, when they hit their limit:

> "Token limit exceeded for free tier (10,000 tokens/month). Upgrade your plan."

The **Upgrade Plan** button (which you'll customize) directs them to your pricing page. You can use:
- **Stripe** for subscriptions
- **Paddle** for simpler setup
- **Gumroad** for one-time purchases

---

## 📊 Check Database

See who's using what:

```bash
sqlite3 office_ai.db
SELECT * FROM users;
SELECT * FROM usage;
```

---

## 🔧 Customize Tiers

Edit `main_production.py` line ~24:

```python
SUBSCRIPTION_TIERS = {
    "free": 10_000,      # ← Change this
    "pro": 100_000,      # ← Or this
    "enterprise": 1_000_000,
}
```

To give Pro users more:
```python
SUBSCRIPTION_TIERS = {
    "free": 5_000,
    "pro": 50_000,
    "enterprise": 500_000,
}
```

---

## 🌐 Upgrade a User's Tier

Manually update the database:

```bash
sqlite3 office_ai.db
UPDATE users SET subscription_tier = 'pro' WHERE user_id = 'test@example.com';
```

Or build an admin panel later.

---

## 🐛 Troubleshooting

**"Token limit exceeded" but user just signed up?**
- Check `office_ai.db`: maybe the month reset
- Run: `DELETE FROM usage WHERE month_year = '2024-12';` to clear month

**Can't find the API key issue?**
- Backend starts but errors on request?
- Check if your API keys are correct and have funds
- Test with: `curl -H "X-User-ID: test" http://localhost:8000/health`

**Add-in won't load?**
- Make sure backend is running on port 8000
- Update manifest.xml to point to taskpane_production.html
- Hard refresh (Ctrl+F5) in Office

**Users can't sign in?**
- Check network — add-in needs to reach localhost:8000
- For production, deploy backend to real server and update URL

---

## 🚀 Next: Go Live

1. **Deploy backend** to AWS/Heroku/Azure
2. **Update manifest.xml** with your server URL
3. **Add HTTPS** (Office requires it)
4. **Build landing page** with pricing tiers
5. **Integrate Stripe** for billing
6. **Submit to AppSource** for Microsoft distribution

---

## 💡 Pro Tips

- **Monitor token burn** — which users consume the most?
- **Set alerts** — get notified if someone burns 80% of their limit
- **Auto-upgrade** — offer power users "upgrade now" mid-month
- **Team plans** — let organizations buy bulk tokens
- **API analytics** — track which features are most-used

---

## 📚 Files to Read

1. `CHANGES.md` — what changed from original
2. `SUBSCRIPTION_MODEL_SETUP.md` — deep dive on config
3. Code comments in `main_production.py` — understand the flow

---

## ✅ Checklist

- [ ] Added API keys
- [ ] Backend starts without errors
- [ ] Can load add-in in Word
- [ ] Can sign in with any user ID
- [ ] Chat works and deducts tokens
- [ ] Token bar shows usage
- [ ] Database file (`office_ai.db`) was created
- [ ] Read the docs

You're ready! 🎉

---

## Questions?

The code is heavily commented. Look for:
- `# ─── Section Title ───────` headers for organization
- Docstrings on every function
- Inline comments explaining logic

Good luck! 🚀
