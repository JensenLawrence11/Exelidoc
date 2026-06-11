# Building Office AI Add-in as a Single .EXE

This guide shows how to package everything into `OfficeAI.exe` that users can download and run.

---

## 📋 Prerequisites

### On Your Build Machine

1. **Python 3.9+** — Download from python.org
2. **NSIS** (for installer) — Download from nsis.sourceforge.io (optional, for .exe installer)

### Install Build Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- PyInstaller (creates .exe)
- PyQt5 (GUI for the launcher)
- FastAPI, Uvicorn, etc. (backend)

---

## 🔨 Step 1: Update Your API Keys

**BEFORE building**, update `backend/main_production.py` with your API keys:

```python
API_KEYS = {
    "openai": "sk-your-real-key",
    "anthropic": "your-real-key",
    "gemini": "your-real-key",
}
```

⚠️ **Security Note**: Your API keys will be baked into the .exe. This is OK for a desktop app (users can't easily extract them), but consider:
- Using environment variables instead
- Asking users to enter their own keys on first run
- Encrypting sensitive config

---

## 🏗️ Step 2: Create the .EXE

### On Windows

```bash
pyinstaller office-ai-addin.spec
```

This creates:
- `dist/OfficeAI/OfficeAI.exe` — the main app
- Plus all dependencies bundled

**Build time**: 2-5 minutes

### Result

```
dist/
└── OfficeAI/
    ├── OfficeAI.exe          ← Run this
    ├── backend/              ← All backend files
    ├── addin/                ← All Office add-in files
    └── [dependencies]        ← All Python libraries
```

---

## 📦 Step 3: (Optional) Create an Installer

If you want users to click "Install" instead of downloading a folder:

### Install NSIS

Download from: https://nsis.sourceforge.io/Download

### Build Installer

```bash
makensis office-ai-addin.nsi
```

This creates: `OfficeAI-Installer.exe`

Users run this → it installs to `C:\Program Files\Office AI` → shortcuts on desktop

---

## 🚀 Step 4: Distribute

### Option A: Folder Distribution
Zip the `dist/OfficeAI/` folder:
```bash
cd dist
powershell -Command "Compress-Archive -Path OfficeAI -DestinationPath OfficeAI.zip"
```

Users download `OfficeAI.zip`, extract, run `OfficeAI.exe`

### Option B: Installer
Upload `OfficeAI-Installer.exe` to your website
Users download and install with one click

### Option C: Auto-Update (Advanced)
Use Electron Updater or similar to push updates automatically

---

## 📋 What's Included in the .EXE

✅ **Desktop Launcher** (PyQt5 GUI)
- Start/stop server
- Configure API keys
- View token usage stats
- One-click server management

✅ **FastAPI Backend**
- All token tracking
- User management (SQLite)
- Cloud AI (OpenAI, Anthropic, Gemini)
- Local AI (Ollama support)
- Subscription tier enforcement

✅ **Office Add-in**
- taskpane_production.html
- manifest.xml
- All client-side code

✅ **Configuration**
- API keys (encrypted in user's home dir, not in .exe)
- Subscription tiers
- Database (created on first run)

---

## 🔧 First Run Experience for Users

1. **Download `OfficeAI.exe`**
2. **Run it** → Desktop launcher opens
3. **Go to Settings tab** → Enter their Anthropic API key (they provide their own, or you provide)
4. **Click Start Server**
5. **Server is running** at http://localhost:8000
6. **In Word/Excel → Insert → Add-ins → Upload My Add-in**
7. **Select manifest.xml** (included)
8. **Office AI panel appears** → Ready to use!

---

## 🔒 Security Considerations

### ✅ Good
- API keys NOT exposed in .exe (they're loaded at runtime)
- User config stored in `~/.office_ai/` (user's home dir)
- Database is local (not cloud)
- Token limits enforced (users can't bypass)

### ⚠️ Could Improve
- API keys in `main_production.py` source code → extract to config file
- Add encryption for stored keys
- Consider asking users to enter their own API key on first run

### Example: User-Provided Key

In `launcher.py`, you could change:

```python
# Instead of baking in API_KEY
API_KEYS = {
    "openai": config.get("openai_key", ""),  # User enters on first run
    ...
}
```

Then in Settings tab, user pastes their own key.

---

## 📊 File Sizes

Expected sizes:

| Item | Size |
|------|------|
| OfficeAI.exe | ~150 MB |
| OfficeAI-Installer.exe | ~80 MB |
| All dependencies | Included in above |

Large because PyQt5 + all Python standard library are bundled.

**To reduce size**:
- Use `UPX` compression (configured in .spec)
- Strip unnecessary modules
- Use PyInstaller `--onefile` (creates single huge .exe instead)

---

## 🚨 Troubleshooting Build Issues

### "PyQt5 not found"
```bash
pip install PyQt5==5.15.9
```

### "module 'pydantic' not found"
```bash
pip install pydantic
```

### "pyinstaller command not found"
```bash
pip install pyinstaller==6.10.0
```

### Build takes forever
- Don't worry, first build is slow (collecting dependencies)
- Subsequent builds are faster

### Antivirus blocks the .exe
- Windows Defender may flag newly-built .exes as suspicious
- Build on a clean machine or disable real-time scanning during build
- You can sign the .exe with a code-signing certificate (advanced)

---

## 🎯 Next Steps

1. ✅ **Add your API keys** to `main_production.py`
2. ✅ **Run `pyinstaller office-ai-addin.spec`**
3. ✅ **Test `dist/OfficeAI/OfficeAI.exe`** on your machine
4. ✅ **Zip the `dist/OfficeAI` folder** or **build installer with NSIS**
5. ✅ **Upload to your website** for download

---

## 🔐 Protecting Your Keys

If you don't want to bake keys into the .exe, modify the code:

**In `launcher.py` Settings tab:**
```python
# User enters their own key
self.anthropic_key = QLineEdit()
self.anthropic_key.setEchoMode(QLineEdit.Password)
```

**In `main_production.py`:**
```python
# Load from user's config file instead of hardcoded
API_KEYS = {
    "openai": load_key("openai"),      # From config
    "anthropic": load_key("anthropic"),
    "gemini": load_key("gemini"),
}
```

This way, **you don't store API keys in code**, and **users provide their own** (and you charge for tokens used on their API account).

---

## 💡 Distribution Strategies

### Free Download (SaaS Model)
- User downloads `OfficeAI.exe`
- Runs locally
- Signs up with email
- You charge based on token usage (your API account)

### Premium Download (Freemium)
- Free tier: Limited tokens (Ollama only, local)
- Paid tier: Cloud AI access (your API keys)

### White-Label (Enterprise)
- Customer provides their own API keys
- You charge for software/support

---

## 🎉 You're Ready!

Once `dist/OfficeAI/OfficeAI.exe` exists, you have:

✅ One file to distribute
✅ Everything bundled (backend, frontend, launcher)
✅ Users just download and run
✅ Server starts with one click
✅ Token tracking included
✅ Ready to charge for subscriptions

Good luck! 🚀
