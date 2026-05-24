"""Gmail tools — uses stored OAuth token."""

import os
import json
import base64
from email.mime.text import MIMEText

TOKENS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tokens")


def _is_connected() -> bool:
    return os.path.exists(os.path.join(TOKENS_DIR, "gmail_token.json"))


def _get_service():
    path = os.path.join(TOKENS_DIR, "gmail_token.json")
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
        return build("gmail", "v1", credentials=creds), None
    except Exception as e:
        return None, str(e)


def read_inbox(max_results: int = 10) -> str:
    service, err = _get_service()
    if not service:
        if err == "not_connected":
            return "📧 Gmail is not connected yet. Go to the Integrations Hub and click Connect on Gmail."
        return f"📧 Gmail connection error: {err}"
    try:
        result = service.users().messages().list(
            userId="me", labelIds=["INBOX"], maxResults=max_results
        ).execute()
        messages = result.get("messages", [])
        if not messages:
            return "📧 Your inbox is empty."
        lines = ["**Recent inbox emails:**"]
        for msg in messages[:10]:
            m = service.users().messages().get(
                userId="me", id=msg["id"], format="metadata",
                metadataHeaders=["Subject", "From"]
            ).execute()
            headers = {h["name"]: h["value"] for h in m.get("payload", {}).get("headers", [])}
            subject = headers.get("Subject", "(no subject)")
            sender = headers.get("From", "unknown")
            lines.append(f"• **{subject}** — from {sender}")
        return "\n".join(lines)
    except Exception as e:
        err_str = str(e)
        if "accessNotConfigured" in err_str or "has not been used" in err_str:
            return "📧 Gmail API is not enabled in Google Cloud. Please enable it at: https://console.developers.google.com/apis/api/gmail.googleapis.com/overview"
        if "invalid_grant" in err_str or "Token has been expired" in err_str:
            return "📧 Gmail token expired. Please reconnect Gmail from the Integrations Hub."
        return f"📧 Gmail error: {err_str[:200]}"


def send_email(to: str, subject: str, body: str) -> str:
    service, err = _get_service()
    if not service:
        if err == "not_connected":
            return "📧 Gmail is not connected. Go to the Integrations Hub and connect Gmail first."
        return f"📧 Gmail connection error: {err}"
    try:
        msg = MIMEText(body)
        msg["to"] = to
        msg["subject"] = subject
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return f"✅ Email sent to **{to}**\nSubject: {subject}"
    except Exception as e:
        err_str = str(e)
        if "accessNotConfigured" in err_str or "has not been used" in err_str:
            return "📧 Gmail API is not enabled in Google Cloud. Please enable it at: https://console.developers.google.com/apis/api/gmail.googleapis.com/overview"
        if "invalid_grant" in err_str:
            return "📧 Gmail token expired. Please reconnect Gmail from the Integrations Hub."
        return f"📧 Gmail error: {err_str[:200]}"


def search_emails(query: str, max_results: int = 10) -> str:
    service, err = _get_service()
    if not service:
        if err == "not_connected":
            return "📧 Gmail is not connected. Go to the Integrations Hub and connect Gmail first."
        return f"📧 Gmail connection error: {err}"
    try:
        result = service.users().messages().list(
            userId="me", q=query, maxResults=max_results
        ).execute()
        messages = result.get("messages", [])
        if not messages:
            return f"📧 No emails found for '{query}'."
        lines = [f"**Emails matching '{query}':**"]
        for msg in messages[:10]:
            m = service.users().messages().get(
                userId="me", id=msg["id"], format="metadata",
                metadataHeaders=["Subject", "From"]
            ).execute()
            headers = {h["name"]: h["value"] for h in m.get("payload", {}).get("headers", [])}
            subject = headers.get("Subject", "(no subject)")
            sender = headers.get("From", "unknown")
            lines.append(f"• **{subject}** — from {sender}")
        return "\n".join(lines)
    except Exception as e:
        err_str = str(e)
        if "accessNotConfigured" in err_str:
            return "📧 Gmail API not enabled. Enable it in Google Cloud Console."
        return f"📧 Gmail error: {err_str[:200]}"
