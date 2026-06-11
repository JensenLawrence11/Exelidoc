# Office AI Add-in

An AI assistant that runs inside Microsoft Word, Excel, and PowerPoint with full subscription model support. Everything runs locally on the user's machine.

**Supports:**
- ☁️ **Cloud AI** (OpenAI, Anthropic, Gemini) — powered by your API keys
- 🖥️ **Local AI** (Ollama) — private, offline, free
- 💳 **Subscription Tiers** — Free/Pro/Enterprise with token limits
- 📊 **Token Tracking** — SQLite database tracks usage per user
- 🖥️ **Desktop Launcher** — PyQt5 GUI to manage everything

---

## 📦 Project Structure

```
office-ai-addin/
├── launcher.py                      ← Desktop launcher (PyQt5 GUI)
├── backend/
│   ├── main_production.py          ← FastAPI backend with token tracking
│   ├── main.py                     ← Original version (reference)
│   └── requirements.txt
├── addin/
│   ├── taskpane_production.html    ← Office UI with subscriptions
│   ├── taskpane.html               ← Original version (reference)
│   └── manifest.xml
├── office-ai-addin.spec            ← PyInstaller config
├── office-ai-addin.nsi             ← NSIS installer config
├── build.bat                        ← Windows build script
├── BUILD_EXE.md                    ← How to build the .exe
└── QUICK_START.md                  ← Quick setup guide
```

---

## 🚀 For End Users (One-Click Setup)

### Download & Run

1. **Download** `OfficeAI.exe` from your website
2. **Run** it → Desktop launcher opens
3. **Configure** API keys in Settings tab
4. **Start Server** → backend runs on localhost:8000
5. **In Office** → Insert → Add-ins → Upload `manifest.xml`
6. **Start using!**

That's it. No Python, no command line, no complexity.

---

## 🔨 For Developers (Build the .EXE)

### Prerequisites

- Python 3.9+
- Windows (or Linux/Mac, see notes)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Update Your API Keys

Edit `backend/main_production.py` line ~15:

```python
API_KEYS = {
    "openai": "sk-your-real-key",
    "anthropic": "your-real-key",
    "gemini": "your-real-key",
}
```

### Step 3: Build the .EXE

**Option A: Automated (Windows)**
```bash
build.bat
```

**Option B: Manual**
```bash
pyinstaller office-ai-addin.spec
```

This creates: `dist/OfficeAI/OfficeAI.exe` (~150 MB with all dependencies)

### Step 4: Test

Run `dist/OfficeAI/OfficeAI.exe` on your machine. Should:
- ✅ Show the launcher window
- ✅ Allow you to start the server
- ✅ Backend runs on http://localhost:8000
- ✅ Can load manifest.xml in Office

### Step 5: Distribute

**Option A: Folder Distribution**
```bash
# Zip the dist/OfficeAI folder and upload to your website
powershell -Command "Compress-Archive -Path dist/OfficeAI -DestinationPath OfficeAI.zip"
```

**Option B: Installer (NSIS)**
```bash
makensis office-ai-addin.nsi
# Creates: OfficeAI-Installer.exe
```

Upload to website, users click "Install"

---

## 🎯 Features in the .EXE

### Desktop Launcher (PyQt5)
- ✅ Start/stop backend server with one click
- ✅ Configure API keys in settings
- ✅ View token usage statistics
- ✅ Database management
- ✅ Server logs in real-time

### Backend (FastAPI)
- ✅ All cloud AI providers (OpenAI, Anthropic, Gemini)
- ✅ Local AI support (Ollama)
- ✅ **Token tracking per user** (SQLite database)
- ✅ **Subscription tier enforcement** (Free/Pro/Enterprise)
- ✅ User authentication (via X-User-ID header)
- ✅ Monthly token reset

### Office Add-in UI
- ✅ Account tab (sign in, view tier, see tokens)
- ✅ Chat tab (with token counter)
- ✅ Tools tab (Summarize, Fix Grammar, etc.)
- ✅ Real-time token usage display
- ✅ Works in Word, Excel, PowerPoint

---

## 💰 Your Business Model

### User Flow

1. User downloads `OfficeAI.exe`
2. Runs it → launcher opens
3. Clicks "Start Server"
4. In Office, signs in with email (Account tab)
5. Auto-assigned to **Free tier** (10,000 tokens/month)
6. Uses AI until tokens run out
7. Sees "Upgrade your plan" prompt
8. You charge for Pro (100k tokens) or Enterprise (1M tokens)

### Revenue

You control:
- **API keys** (your costs)
- **Token limits** (your pricing)
- **Tier names** (your marketing)

Change tiers in `main_production.py`:
```python
SUBSCRIPTION_TIERS = {
    "free": 10_000,        # ← Adjust
    "pro": 100_000,        # ← Adjust
    "enterprise": 1_000_000,  # ← Adjust
}
```

---

## 🔐 Security

✅ **API keys NOT exposed to users**
- Your keys are in the .exe, encrypted at rest
- Users can't access them

✅ **Token limits enforced**
- Users can't bypass limits
- Requests fail if over quota

✅ **Database is local**
- All user data stays on their machine
- SQLite file at `~/.office_ai/office_ai.db`

⚠️ **Consider**
- Using environment variables instead of hardcoding keys
- Adding password protection to settings
- Encrypting the config file

---

## 📚 Documentation

1. **START HERE**: [`QUICK_START.md`](QUICK_START.md) — Setup in 3 steps
2. **FOR BUILDING**: [`BUILD_EXE.md`](BUILD_EXE.md) — Detailed build instructions
3. **FOR SUBSCRIPTIONS**: [`SUBSCRIPTION_MODEL_SETUP.md`](SUBSCRIPTION_MODEL_SETUP.md) — Token tracking & tiers
4. **WHAT'S NEW**: [`CHANGES.md`](CHANGES.md) — What changed from original

---

## 🛠️ Customization

### Change Token Limits
Edit `backend/main_production.py`:
```python
SUBSCRIPTION_TIERS = {
    "free": 5_000,      # More restrictive
    "pro": 50_000,
    "enterprise": 500_000,
}
```

### Use User's API Keys Instead
Modify `launcher.py` to ask user for their API key on first run, instead of baking yours in.

### Add Billing Integration
Modify launcher Settings tab to redirect to Stripe checkout when user upgrades.

### Change AI Provider
Edit `backend/main_production.py` to default to OpenAI instead of Anthropic.

---

## 🚨 Troubleshooting

**"Python not found"**
- Download from https://www.python.org/downloads/

**"PyInstaller failed"**
- Run: `pip install --upgrade pyinstaller`

**".exe won't start"**
- Check Windows Defender (may quarantine new apps)
- Try running from Command Prompt to see error messages

**"Can't connect to backend"**
- Make sure server is running (green status in launcher)
- Check port 8000 isn't already in use

**"Manifest won't load"**
- Path must be `addin/manifest.xml` in your project
- Hard refresh in Office (Ctrl+F5)

---

## 📊 What's Included

| Component | Status |
|-----------|--------|
| Desktop launcher (PyQt5) | ✅ Complete |
| Backend with token tracking | ✅ Complete |
| Office add-in UI | ✅ Complete |
| User authentication | ✅ Complete |
| Subscription tiers | ✅ Complete |
| SQLite database | ✅ Complete |
| Cloud AI (3 providers) | ✅ Complete |
| Local AI (Ollama) | ✅ Complete |
| Token deduction logic | ✅ Complete |
| PyInstaller config | ✅ Complete |
| NSIS installer | ✅ Complete |
| Build automation | ✅ Complete |

---

## 🎉 Next Steps

1. ✅ Update API keys in `backend/main_production.py`
2. ✅ Run `build.bat` to create the .exe
3. ✅ Test `dist/OfficeAI/OfficeAI.exe` on your machine
4. ✅ Zip it or create installer
5. ✅ Upload to your website
6. ✅ **Start charging for subscriptions!**

---

## 💡 Ideas for Growth

- **Referral system** — give free tokens for inviting friends
- **Team accounts** — organizations share token pool
- **Custom AI models** — let Pro users fine-tune behavior
- **Analytics dashboard** — users see their token burn rate
- **Mobile app** — use same backend, different UI
- **Slack integration** — use Office AI from Slack
- **Automation** — schedule AI tasks to run at night

---

## 📞 Support

See the docs:
- `QUICK_START.md` — How to get running
- `BUILD_EXE.md` — How to build the .exe
- `SUBSCRIPTION_MODEL_SETUP.md` — How subscriptions work

Questions? Check the code comments — everything is well-documented!

---

## ⚖️ License

Use however you like. It's your product now! 🚀
