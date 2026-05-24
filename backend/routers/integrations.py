"""
Integrations router — manage OAuth connections for third-party tools.
"""

import os
import json
import secrets
import urllib.parse
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

router = APIRouter()

OAUTH_REDIRECT_BASE = os.getenv("OAUTH_REDIRECT_BASE_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_APP_URL", "http://localhost:3000")
TOKENS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tokens")

if not os.path.exists(TOKENS_DIR):
    os.makedirs(TOKENS_DIR)

INTEGRATIONS = [
    {"id": "gmail",    "name": "Gmail",            "icon": "📧", "category": "google",       "connected": False},
    {"id": "gcal",     "name": "Google Calendar",  "icon": "📅", "category": "google",       "connected": False},
    {"id": "gmeet",    "name": "Google Meet",       "icon": "📹", "category": "google",       "connected": False},
    {"id": "gforms",   "name": "Google Forms",      "icon": "📋", "category": "google",       "connected": False},
    {"id": "gsheets",  "name": "Google Sheets",     "icon": "📊", "category": "google",       "connected": False},
    {"id": "drive",    "name": "Google Drive",      "icon": "💾", "category": "google",       "connected": False},
    {"id": "discord",  "name": "Discord",           "icon": "🎮", "category": "messaging",    "connected": False},
    {"id": "notion",   "name": "Notion",            "icon": "📝", "category": "productivity", "connected": False},
    {"id": "github",   "name": "GitHub",            "icon": "🐙", "category": "developer",    "connected": False},
    {"id": "whatsapp", "name": "WhatsApp",          "icon": "📱", "category": "messaging",    "connected": False},
]

GOOGLE_SCOPES = {
    "gmail":   "https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.send",
    "gcal":    "https://www.googleapis.com/auth/calendar",
    "gmeet":   "https://www.googleapis.com/auth/meetings.space.created",
    "gforms":  "https://www.googleapis.com/auth/forms.responses.readonly https://www.googleapis.com/auth/forms.body",
    "gsheets": "https://www.googleapis.com/auth/spreadsheets",
    "drive":   "https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/drive.readonly",
}

# In-memory state store for OAuth flows
_oauth_states: dict[str, str] = {}


def _token_path(tool_id: str) -> str:
    return os.path.join(TOKENS_DIR, f"{tool_id}_token.json")


def _is_connected(tool_id: str) -> bool:
    if tool_id == "notion" and os.getenv("NOTION_ACCESS_TOKEN", ""):
        return True
    return os.path.exists(_token_path(tool_id))


def _save_token(tool_id: str, data: dict) -> None:
    with open(_token_path(tool_id), "w") as f:
        json.dump(data, f)


def _load_token(tool_id: str) -> dict:
    path = _token_path(tool_id)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


# ── List ──────────────────────────────────────────────────────────────

@router.get("/")
async def list_integrations():
    result = []
    for integration in INTEGRATIONS:
        item = dict(integration)
        item["connected"] = _is_connected(item["id"])
        result.append(item)
    return {"status": "ok", "integrations": result}


# ── Connect ───────────────────────────────────────────────────────────

class ConnectRequest(BaseModel):
    redirect_uri: str = ""


@router.post("/{tool_id}/connect")
async def connect_integration(tool_id: str, req: ConnectRequest):
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")

    # ── Google tools ──────────────────────────────────────────────────
    if tool_id in GOOGLE_SCOPES:
        if not client_id or not client_secret:
            return {"status": "error", "message": "GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET not configured"}
        redirect = f"{OAUTH_REDIRECT_BASE}/api/integrations/{tool_id}/callback"
        state = secrets.token_urlsafe(16)
        _oauth_states[state] = tool_id
        params = urllib.parse.urlencode({
            "client_id": client_id,
            "redirect_uri": redirect,
            "response_type": "code",
            "scope": GOOGLE_SCOPES[tool_id],
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        })
        return {"status": "ok", "oauth_url": f"https://accounts.google.com/o/oauth2/v2/auth?{params}"}

    # ── Notion ────────────────────────────────────────────────────────
    if tool_id == "notion":
        token = os.getenv("NOTION_ACCESS_TOKEN", "")
        if token:
            return {"status": "ok", "message": "Notion connected via access token"}
        notion_client_id = os.getenv("NOTION_CLIENT_ID", "")
        if notion_client_id:
            redirect = f"{OAUTH_REDIRECT_BASE}/api/integrations/notion/callback"
            params = urllib.parse.urlencode({
                "client_id": notion_client_id,
                "redirect_uri": redirect,
                "response_type": "code",
                "owner": "user",
            })
            return {"status": "ok", "oauth_url": f"https://api.notion.com/v1/oauth/authorize?{params}"}
        return {"status": "error", "message": "Add NOTION_ACCESS_TOKEN to backend .env"}

    # ── GitHub ────────────────────────────────────────────────────────
    if tool_id == "github":
        gh_client_id = os.getenv("GITHUB_CLIENT_ID", "")
        if gh_client_id:
            redirect = f"{OAUTH_REDIRECT_BASE}/api/integrations/github/callback"
            params = urllib.parse.urlencode({
                "client_id": gh_client_id,
                "redirect_uri": redirect,
                "scope": "repo read:user",
            })
            return {"status": "ok", "oauth_url": f"https://github.com/login/oauth/authorize?{params}"}
        return {"status": "error", "message": "Add GITHUB_CLIENT_ID to backend .env"}

    # ── Discord ───────────────────────────────────────────────────────
    if tool_id == "discord":
        dc_client_id = os.getenv("DISCORD_CLIENT_ID", "")
        if dc_client_id:
            redirect = f"{OAUTH_REDIRECT_BASE}/api/integrations/discord/callback"
            params = urllib.parse.urlencode({
                "client_id": dc_client_id,
                "redirect_uri": redirect,
                "response_type": "code",
                "scope": "identify guilds",
            })
            return {"status": "ok", "oauth_url": f"https://discord.com/api/oauth2/authorize?{params}"}
        return {"status": "error", "message": "Add DISCORD_CLIENT_ID to backend .env"}

    # ── WhatsApp ──────────────────────────────────────────────────────
    if tool_id == "whatsapp":
        _save_token("whatsapp", {"connected": True})
        return {"status": "ok", "message": "WhatsApp ready — uses browser automation"}

    # ── Fallback ──────────────────────────────────────────────────────
    _save_token(tool_id, {"connected": True})
    return {"status": "ok", "message": f"{tool_id} connected (demo mode)"}


# ── Disconnect ────────────────────────────────────────────────────────

@router.post("/{tool_id}/disconnect")
async def disconnect_integration(tool_id: str):
    path = _token_path(tool_id)
    if os.path.exists(path):
        os.remove(path)
    return {"status": "ok", "message": f"{tool_id} disconnected"}


# ── OAuth Callbacks ───────────────────────────────────────────────────

@router.get("/{tool_id}/callback")
async def oauth_callback(tool_id: str, code: str = "", state: str = "", error: str = ""):
    import httpx
    frontend = os.getenv("FRONTEND_APP_URL", "http://localhost:3000")

    if error:
        return RedirectResponse(url=f"{frontend}/integrations?error={urllib.parse.quote(error)}")
    if not code:
        return RedirectResponse(url=f"{frontend}/integrations?error=no_code")

    # ── Google ────────────────────────────────────────────────────────
    if tool_id in GOOGLE_SCOPES:
        client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
        redirect = f"{OAUTH_REDIRECT_BASE}/api/integrations/{tool_id}/callback"
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "code": code,
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "redirect_uri": redirect,
                        "grant_type": "authorization_code",
                    },
                )
            data = resp.json()
            if "error" in data:
                return RedirectResponse(url=f"{frontend}/integrations?error={urllib.parse.quote(str(data['error']))}")
            # Enrich token with client credentials for refresh
            data["client_id"] = client_id
            data["client_secret"] = client_secret
            data["token_uri"] = "https://oauth2.googleapis.com/token"
            _save_token(tool_id, data)
            return RedirectResponse(url=f"{frontend}/integrations?connected={tool_id}")
        except Exception as e:
            return RedirectResponse(url=f"{frontend}/integrations?error={urllib.parse.quote(str(e)[:80])}")

    # ── GitHub ────────────────────────────────────────────────────────
    if tool_id == "github":
        client_id = os.getenv("GITHUB_CLIENT_ID", "")
        client_secret = os.getenv("GITHUB_CLIENT_SECRET", "")
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://github.com/login/oauth/access_token",
                    data={"client_id": client_id, "client_secret": client_secret, "code": code},
                    headers={"Accept": "application/json"},
                )
            data = resp.json()
            _save_token("github", data)
            return RedirectResponse(url=f"{frontend}/integrations?connected=github")
        except Exception as e:
            return RedirectResponse(url=f"{frontend}/integrations?error={urllib.parse.quote(str(e)[:80])}")

    # ── Discord ───────────────────────────────────────────────────────
    if tool_id == "discord":
        client_id = os.getenv("DISCORD_CLIENT_ID", "")
        client_secret = os.getenv("DISCORD_CLIENT_SECRET", "")
        redirect = f"{OAUTH_REDIRECT_BASE}/api/integrations/discord/callback"
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://discord.com/api/oauth2/token",
                    data={
                        "client_id": client_id,
                        "client_secret": client_secret,
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": redirect,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
            data = resp.json()
            _save_token("discord", data)
            return RedirectResponse(url=f"{frontend}/integrations?connected=discord")
        except Exception as e:
            return RedirectResponse(url=f"{frontend}/integrations?error={urllib.parse.quote(str(e)[:80])}")

    # ── Notion ────────────────────────────────────────────────────────
    if tool_id == "notion":
        import base64
        client_id = os.getenv("NOTION_CLIENT_ID", "")
        client_secret = os.getenv("NOTION_CLIENT_SECRET", "")
        redirect = f"{OAUTH_REDIRECT_BASE}/api/integrations/notion/callback"
        credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://api.notion.com/v1/oauth/token",
                    json={"grant_type": "authorization_code", "code": code, "redirect_uri": redirect},
                    headers={"Authorization": f"Basic {credentials}", "Notion-Version": "2022-06-28"},
                )
            data = resp.json()
            _save_token("notion", data)
            return RedirectResponse(url=f"{frontend}/integrations?connected=notion")
        except Exception as e:
            return RedirectResponse(url=f"{frontend}/integrations?error={urllib.parse.quote(str(e)[:80])}")

    return RedirectResponse(url=f"{frontend}/integrations?error=unknown_tool")
