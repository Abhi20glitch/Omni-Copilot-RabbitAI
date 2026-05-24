"""Google Calendar tools — uses stored OAuth token."""

import os
import json
from datetime import datetime, timezone

TOKENS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tokens")


def _is_connected() -> bool:
    return os.path.exists(os.path.join(TOKENS_DIR, "gcal_token.json"))


def _get_service():
    path = os.path.join(TOKENS_DIR, "gcal_token.json")
    if not os.path.exists(path):
        return None, "not_connected"
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        with open(path) as f:
            data = json.load(f)
        creds = Credentials(
            token=data.get("access_token") or data.get("token"),
            refresh_token=data.get("refresh_token"),
            token_uri=data.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=data.get("client_id", os.getenv("GOOGLE_CLIENT_ID", "")),
            client_secret=data.get("client_secret", os.getenv("GOOGLE_CLIENT_SECRET", "")),
        )
        return build("calendar", "v3", credentials=creds), None
    except Exception as e:
        return None, str(e)


def _handle_error(err_str: str, tool: str = "Calendar") -> str:
    if "accessNotConfigured" in err_str or "has not been used" in err_str:
        return f"📅 Google {tool} API is not enabled. Enable it at: https://console.developers.google.com/apis/api/calendar-json.googleapis.com/overview"
    if "invalid_grant" in err_str or "Token has been expired" in err_str:
        return f"📅 Google {tool} token expired. Please reconnect from the Integrations Hub."
    return f"📅 {tool} error: {err_str[:200]}"


def get_upcoming_events(max_results: int = 10) -> str:
    service, err = _get_service()
    if not service:
        if err == "not_connected":
            return "📅 Google Calendar is not connected. Go to the Integrations Hub and connect Google Calendar."
        return f"📅 Calendar connection error: {err}"
    try:
        now = datetime.now(timezone.utc).isoformat()
        result = service.events().list(
            calendarId="primary", timeMin=now,
            maxResults=max_results, singleEvents=True, orderBy="startTime"
        ).execute()
        events = result.get("items", [])
        if not events:
            return "📅 No upcoming events found on your calendar."
        lines = ["**Upcoming Calendar Events:**"]
        for e in events:
            start = e["start"].get("dateTime", e["start"].get("date", ""))
            lines.append(f"• **{e['summary']}** — {start}")
        return "\n".join(lines)
    except Exception as e:
        return _handle_error(str(e))


def create_calendar_event(summary: str, start: str, end: str, description: str = "") -> str:
    service, err = _get_service()
    if not service:
        if err == "not_connected":
            return "📅 Google Calendar is not connected. Connect it from the Integrations Hub."
        return f"📅 Calendar connection error: {err}"
    try:
        event = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start, "timeZone": "UTC"},
            "end": {"dateTime": end, "timeZone": "UTC"},
        }
        created = service.events().insert(calendarId="primary", body=event).execute()
        return f"✅ Event created: **{summary}**\n{created.get('htmlLink', '')}"
    except Exception as e:
        return _handle_error(str(e))


def check_availability(date: str) -> str:
    service, err = _get_service()
    if not service:
        if err == "not_connected":
            return "📅 Google Calendar is not connected. Connect it from the Integrations Hub."
        return f"📅 Calendar connection error: {err}"
    try:
        start = f"{date}T00:00:00Z"
        end = f"{date}T23:59:59Z"
        result = service.events().list(
            calendarId="primary", timeMin=start, timeMax=end,
            singleEvents=True, orderBy="startTime"
        ).execute()
        events = result.get("items", [])
        if not events:
            return f"✅ You're free all day on {date}!"
        lines = [f"**Your schedule for {date}:**"]
        for e in events:
            s = e["start"].get("dateTime", e["start"].get("date", ""))
            en = e["end"].get("dateTime", e["end"].get("date", ""))
            lines.append(f"• **{e['summary']}** ({s} → {en})")
        return "\n".join(lines)
    except Exception as e:
        return _handle_error(str(e))
