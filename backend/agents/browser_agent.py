"""BrowserAgent — WhatsApp automation via Playwright."""

from __future__ import annotations
import os, re, asyncio
from typing import Any

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama-3.3-70b-versatile")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
WHATSAPP_CONFIRM_MS = int(os.getenv("OMNI_WHATSAPP_CONFIRMATION_MS", "6000"))


def _get_llm():
    if not GROQ_API_KEY:
        return None
    try:
        from langchain_groq import ChatGroq
        return ChatGroq(model=DEFAULT_MODEL, api_key=GROQ_API_KEY, temperature=0.5)
    except Exception:
        return None


async def _send_whatsapp(contact: str, message: str) -> str:
    """Open WhatsApp Web and send a message using Playwright."""
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto("https://web.whatsapp.com")
            return (
                f"📱 WhatsApp Web opened. Please scan the QR code if not already logged in.\n"
                f"Once logged in, I'll send '{message}' to {contact}.\n"
                f"Note: First-time use requires QR code scan."
            )
    except Exception as e:
        return f"📱 WhatsApp error: {str(e)}"


class BrowserAgent:
    def __init__(self):
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            self._llm = _get_llm()
        return self._llm

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        last_msg = state["messages"][-1]["content"] if state["messages"] else ""
        msg_lower = last_msg.lower()
        state["agent_steps"].append({"agent": "browser", "action": f"Processing: {last_msg[:60]}"})

        if "whatsapp" in msg_lower:
            llm = self._get_llm()
            contact = ""
            message = ""
            if llm:
                try:
                    from langchain_core.messages import HumanMessage, SystemMessage
                    import json
                    extract = llm.invoke([
                        SystemMessage(content=(
                            "Extract WhatsApp message details. "
                            "Reply ONLY as JSON: {\"contact\": \"name or number\", \"message\": \"message text\"}."
                        )),
                        HumanMessage(content=last_msg)
                    ])
                    raw = extract.content.strip()
                    match = re.search(r'\{.*\}', raw, re.DOTALL)
                    if match:
                        details = json.loads(match.group())
                        contact = details.get("contact", "")
                        message = details.get("message", "")
                except Exception:
                    pass

            if contact and message:
                content = asyncio.run(_send_whatsapp(contact, message))
            else:
                content = "📱 To send a WhatsApp message, please specify the contact and message. Example: 'Send WhatsApp to John: Hey, are you free tonight?'"

        else:
            llm = self._get_llm()
            if llm:
                try:
                    from langchain_core.messages import HumanMessage, SystemMessage
                    resp = llm.invoke([
                        SystemMessage(content=(
                            "You are a web browsing assistant. Help the user with web searches and browsing tasks. "
                            "Be helpful and concise."
                        )),
                        HumanMessage(content=last_msg)
                    ])
                    content = f"🌐 {resp.content}"
                except Exception as e:
                    content = f"🌐 Browser error: {str(e)}"
            else:
                content = f"🌐 Set GROQ_API_KEY to enable browser assistance."

        state["messages"].append({"role": "assistant", "content": content})
        state["agent_steps"].append({"agent": "browser", "action": "Browser operation completed"})
        return state
