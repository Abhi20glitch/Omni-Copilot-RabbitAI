"""
Integrations router — manage OAuth connections for third-party tools.
"""

import os
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

OAUTH_REDIRECT_BASE = os.getenv("OAUTH_REDIRECT_BASE_URL", "http://localhost:3000")

INTEGRATIONS = [
    {"id": "gmail", "name": "Gmail", "icon": "📧", "category": "google", "connected": False},
    {"id": "gcal", "name": "Google Calendar", "icon": "📅", "category": "google", "connected": False},
    {"id": "gmeet", "name": "Google Meet", "icon": "📹", "category": "google", "connected": False},
    {"id": "gforms", "name": "Google Forms", "icon": "📋", "category": "google", "connected": False},
    {"id": "gsheets", "name": "Google Sheets", "icon": "📊", "category": "google", "connected": False},
    {"id": "drive", "name": "Google Drive", "icon": "💾", "category": "google", "connected": False},
    {"id": "slack", "name": "Slack", "icon": "💬", "category": "messaging", "connected": False},
    {"id": "discord", "name": "Discord", "icon": "🎮", "category": "messaging", "connected": False},
    {"id": "notion", "name": "Notion", "icon": "📝", "category": "productivity", "connected": False},
    {"id": "github", "name": "GitHub", "icon": "🐙", "category": "developer", "connected": False},
    {"id": "whatsapp", "name": "WhatsApp", "icon": "📱", "category": "messaging", "connected": False},
]

# In-memory connection state (replace with DB in production)
_connected: dict[str, bool] = {}

GOOGLE_SCOPES = {
    "gmail": ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send"],
    "gcal": ["https://www.googleapis.com/auth/calendar"],
    "gmeet": ["https://www.googleapis.com/auth/meetings.space.created"],
    "gforms": ["https://www.googleapis.com/auth/forms.responses.readonly", "https://www.googleapis.com/auth/forms.body"],
    "gsheets": ["https://www.googleapis.com/auth/spreadsheets"],
    "drive": ["https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive.readonly"],
}


@router.get("/")
async def list_integrations():
    """List all integrations with their connection status."""
    result = []
    for integration in INTEGRATIONS:
        item = dict(integration)
        item["connected"] = _connected.get(item["id"], False)
        result.append(item)
    return {"status": "ok", "integrations": result}


class ConnectRequest(BaseModel):
    redirect_uri: str = ""


@router.post("/{tool_id}/connect")
async def connect_integration(tool_id: str, req: ConnectRequest):
    """Initiate OAuth connection for a tool. Returns the OAuth URL."""
    if tool_id in GOOGLE_SCOPES:
        client_id = os.getenv("GOOGLE_CLIENT_ID", "")
        if not client_id:
            return {"status": "error", "message": "GOOGLE_CLIENT_ID not configured"}
        scopes = "+".join(GOOGLE_SCOPES[tool_id])
        redirect = f"{OAUTH_REDIRECT_BASE}/api/integrations/{tool_id}/callback"
        oauth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={client_id}&redirect_uri={redirect}"
            f"&response_type=code&scope={scopes}&access_type=offline"
        )
        return {"status": "ok", "oauth_url": oauth_url}

    # Non-Google integrations
    client_id_key = f"{tool_id.upper()}_CLIENT_ID"
    client_id = os.getenv(client_id_key, "")
    if not client_id:
        _connected[tool_id] = True  # Simulated for demo
        return {"status": "ok", "message": f"{tool_id} connected (demo mode)"}
    return {"status": "ok", "message": f"OAuth flow for {tool_id} initiated"}


@router.post("/{tool_id}/disconnect")
async def disconnect_integration(tool_id: str):
    """Disconnect an integration."""
    _connected[tool_id] = False
    return {"status": "ok", "message": f"{tool_id} disconnected"}


# ── OAuth callback stubs ──────────────────────────────────────────────
def _make_callback(tool_id: str):
    async def callback(code: str = ""):
        if code:
            _connected[tool_id] = True
            return {"status": "ok", "message": f"{tool_id} connected successfully"}
        return {"status": "error", "message": "No authorization code received"}
    return callback


for _tool in ["gmail", "gcal", "gmeet", "gforms", "gsheets", "drive", "slack", "discord", "notion", "github"]:
    router.add_api_route(f"/{_tool}/callback", _make_callback(_tool), methods=["GET"])
