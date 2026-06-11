"""
Office AI Add-in - Production Backend with Subscription Model
Run with: uvicorn main_production:app --reload --port 8000

BUSINESS MODEL:
- You provide the API key (hard-coded, hidden from users)
- Users pay for subscription tiers based on token usage
- Token usage is tracked and enforced per user
- No user API keys allowed
"""

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import httpx
import json
import sqlite3
import os
from datetime import datetime, timedelta
from contextlib import contextmanager

app = FastAPI(title="Office AI Add-in Backend", version="2.0.0")

# ─── Configuration ─────────────────────────────────────────────────────────────

# !! REPLACE THESE WITH YOUR ACTUAL API KEYS !!
API_KEYS = {
    "openai": "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",
    "anthropic": "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",
    "gemini": "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",
}

# !! REPLACE WITH A SECRET KEY FOR USER AUTH !!
JWT_SECRET = "your-super-secret-key-change-this-in-production"

# Subscription tiers: tokens per month
SUBSCRIPTION_TIERS = {
    "free": 10_000,
    "pro": 100_000,
    "enterprise": 1_000_000,
}

# ─── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Database Setup ───────────────────────────────────────────────────────────

DB_PATH = "office_ai.db"

def get_db():
    """SQLite connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create tables if they don't exist."""
    conn = get_db()
    c = conn.cursor()
    
    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            subscription_tier TEXT DEFAULT 'free',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Token usage tracking (monthly reset)
    c.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            tokens_used INTEGER DEFAULT 0,
            month_year TEXT NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, month_year),
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)
    
    # API call logs (for debugging/analytics)
    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            provider TEXT,
            prompt_length INTEGER,
            response_length INTEGER,
            tokens_used INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# ─── Models ───────────────────────────────────────────────────────────────────

class AIRequest(BaseModel):
    prompt: str
    mode: str = "cloud"
    provider: str = "anthropic"  # openai | anthropic | gemini
    system_prompt: Optional[str] = None
    max_tokens: int = 1024

class UserSignup(BaseModel):
    user_id: str  # unique identifier (email or UUID)
    email: Optional[str] = None
    subscription_tier: str = "free"

# ─── Helper Functions ─────────────────────────────────────────────────────────

def get_current_month() -> str:
    """Return YYYY-MM format for current month."""
    return datetime.utcnow().strftime("%Y-%m")

def estimate_tokens(text: str) -> int:
    """Rough token estimation: ~4 chars per token."""
    return max(1, len(text) // 4)

def get_user_usage(user_id: str) -> dict:
    """Get current month's token usage for user."""
    conn = get_db()
    c = conn.cursor()
    month = get_current_month()
    
    c.execute(
        "SELECT tokens_used FROM usage WHERE user_id = ? AND month_year = ?",
        (user_id, month)
    )
    row = c.fetchone()
    conn.close()
    
    return {"tokens_used": row[0] if row else 0, "month": month}

def add_tokens(user_id: str, tokens: int):
    """Add tokens to user's monthly usage."""
    conn = get_db()
    c = conn.cursor()
    month = get_current_month()
    
    c.execute(
        """
        INSERT INTO usage (user_id, tokens_used, month_year) 
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, month_year) 
        DO UPDATE SET tokens_used = tokens_used + ?
        """,
        (user_id, tokens, month, tokens)
    )
    conn.commit()
    conn.close()

def log_api_call(user_id: str, provider: str, prompt_len: int, response_len: int, tokens: int):
    """Log API call for analytics."""
    conn = get_db()
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO logs (user_id, provider, prompt_length, response_length, tokens_used)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, provider, prompt_len, response_len, tokens)
    )
    conn.commit()
    conn.close()

def check_rate_limit(user_id: str) -> tuple[bool, dict]:
    """Check if user is within their token limit. Returns (allowed, info)."""
    conn = get_db()
    c = conn.cursor()
    
    # Get user's subscription tier
    c.execute("SELECT subscription_tier FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="User not found. Please sign up first.")
    
    tier = row[0]
    limit = SUBSCRIPTION_TIERS.get(tier, SUBSCRIPTION_TIERS["free"])
    usage = get_user_usage(user_id)
    tokens_remaining = limit - usage["tokens_used"]
    
    return tokens_remaining > 0, {
        "tier": tier,
        "limit": limit,
        "used": usage["tokens_used"],
        "remaining": max(0, tokens_remaining)
    }

# ─── Cloud AI Providers ────────────────────────────────────────────────────────

async def call_anthropic(prompt: str, system_prompt: str, model: str, max_tokens: int) -> tuple[str, int]:
    """Call Anthropic Claude API. Returns (response, tokens_used)."""
    model = model or "nvidia/nemotron-3-ultra-550b-a55b"
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system_prompt:
        payload["system"] = system_prompt

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://integrate.api.nvidia.com/v1",
            headers={
                "x-api-key": API_KEYS["anthropic"],
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="API key invalid (backend issue).")
        response.raise_for_status()
        
        data = response.json()
        result_text = data["content"][0]["text"]
        
        # Anthropic returns usage info
        usage = data.get("usage", {})
        tokens = usage.get("output_tokens", 0) + usage.get("input_tokens", 0)
        
        return result_text, tokens

async def call_openai(prompt: str, system_prompt: str, model: str, max_tokens: int) -> tuple[str, int]:
    """Call OpenAI API. Returns (response, tokens_used)."""
    model = model or "nvidia/nemotron-3-ultra-550b-a55b"
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            "https://integrate.api.nvidia.com/v1",
            headers={
                "Authorization": f"Bearer {API_KEYS['openai']}",
                "Content-Type": "application/json"
            },
            json={"model": model, "messages": messages, "max_tokens": max_tokens},
        )
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="API key invalid (backend issue).")
        response.raise_for_status()
        
        data = response.json()
        result_text = data["choices"][0]["message"]["content"]
        tokens = data["usage"]["total_tokens"]
        
        return result_text, tokens

async def call_gemini(prompt: str, system_prompt: str, model: str, max_tokens: int) -> tuple[str, int]:
    """Call Google Gemini API. Returns (response, tokens_used)."""
    model = model or "nvidia/nemotron-3-ultra-550b-a55b"
    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"https://integrate.api.nvidia.com/v1",
            json={
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": {"maxOutputTokens": max_tokens},
            },
        )
        if response.status_code == 400:
            raise HTTPException(status_code=401, detail="API key invalid (backend issue).")
        response.raise_for_status()
        
        data = response.json()
        result_text = data["candidates"][0]["content"]["parts"][0]["text"]
        
        # Estimate tokens since Gemini doesn't always return usage
        tokens = estimate_tokens(full_prompt) + estimate_tokens(result_text)
        
        return result_text, tokens

async def call_local_ai(prompt: str, system_prompt: str, model: str, max_tokens: int) -> tuple[str, int]:
    """Call local Ollama. Returns (response, tokens_used)."""
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434", timeout=2)
    except:
        raise HTTPException(
            status_code=503,
            detail="Local AI (Ollama) is not running. Start it with: ollama serve"
        )

    model = model or "llama3"
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "http://localhost:11434/api/chat",
            json={"model": model, "messages": messages, "stream": False},
        )
        response.raise_for_status()
        data = response.json()
        result_text = data["message"]["content"]
        
        # Estimate tokens
        tokens = estimate_tokens(prompt) + estimate_tokens(result_text)
        
        return result_text, tokens

# ─── API Endpoints ────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0", "model": "subscription-based"}

@app.post("/signup")
def signup(payload: UserSignup):
    """Register a new user or update existing user."""
    if payload.subscription_tier not in SUBSCRIPTION_TIERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tier. Choose from: {list(SUBSCRIPTION_TIERS.keys())}"
        )
    
    conn = get_db()
    c = conn.cursor()
    
    try:
        c.execute(
            """
            INSERT INTO users (user_id, email, subscription_tier)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) 
            DO UPDATE SET subscription_tier = ?, updated_at = CURRENT_TIMESTAMP
            """,
            (payload.user_id, payload.email, payload.subscription_tier, payload.subscription_tier)
        )
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=str(e))
    
    conn.close()
    return {"status": "ok", "user_id": payload.user_id, "tier": payload.subscription_tier}

@app.get("/usage/{user_id}")
def get_usage(user_id: str):
    """Get user's current token usage and limits."""
    allowed, info = check_rate_limit(user_id)
    return info

@app.post("/ai/generate")
async def generate(req: AIRequest, x_user_id: str = Header(None)):
    """
    Generate AI response. User ID required via X-User-ID header.
    
    Example request header:
        X-User-ID: user@example.com
    """
    if not x_user_id:
        raise HTTPException(
            status_code=401,
            detail="Missing X-User-ID header. Set it to your user ID."
        )
    
    # Check rate limit
    allowed, usage_info = check_rate_limit(x_user_id)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Token limit exceeded for {usage_info['tier']} tier ({usage_info['limit']} tokens/month). Upgrade your plan."
        )
    
    system = req.system_prompt or "You are a helpful AI assistant inside Microsoft Office. Be concise and clear."
    
    try:
        if req.mode == "local":
            result, tokens_used = await call_local_ai(req.prompt, system, "", req.max_tokens)
        else:  # cloud
            if req.provider == "anthropic":
                result, tokens_used = await call_anthropic(req.prompt, system, "", req.max_tokens)
            elif req.provider == "openai":
                result, tokens_used = await call_openai(req.prompt, system, "", req.max_tokens)
            elif req.provider == "gemini":
                result, tokens_used = await call_gemini(req.prompt, system, "", req.max_tokens)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown provider: {req.provider}")
        
        # Track usage
        add_tokens(x_user_id, tokens_used)
        log_api_call(x_user_id, req.provider, len(req.prompt), len(result), tokens_used)
        
        # Get updated usage
        new_usage = get_user_usage(x_user_id)
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT subscription_tier FROM users WHERE user_id = ?", (x_user_id,))
        tier_row = c.fetchone()
        conn.close()
        tier = tier_row[0] if tier_row else "free"
        limit = SUBSCRIPTION_TIERS[tier]
        
        return {
            "result": result,
            "mode": req.mode,
            "tokens_used": tokens_used,
            "usage": {
                "used": new_usage["tokens_used"],
                "limit": limit,
                "remaining": limit - new_usage["tokens_used"]
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/local/models")
async def list_local_models():
    """List available Ollama models."""
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434", timeout=2)
    except:
        return {"models": [], "error": "Ollama not running"}
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            data = response.json()
            models = [m["name"] for m in data.get("models", [])]
            return {"models": models}
    except Exception as e:
        return {"models": [], "error": str(e)}

# ─── Serve the add-in HTML ────────────────────────────────────────────────────

addin_path = os.path.join(os.path.dirname(__file__), "..", "addin")
if os.path.isdir(addin_path):
    app.mount("/addin", StaticFiles(directory=addin_path, html=True), name="addin")

# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_production:app", host="127.0.0.1", port=8000, reload=True)
