"""
BrowserAgent — Web browsing and WhatsApp automation.
"""

from __future__ import annotations
import os
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


class BrowserAgent:
    """Specialist agent for web browsing and WhatsApp automation."""

    def __init__(self) -> None:
        self.tools = ["browse_url", "search_web", "send_whatsapp", "scrape_page"]
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            self._llm = _get_llm()
        return self._llm

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        last_msg = state["messages"][-1]["content"] if state["messages"] else ""
        msg_lower = last_msg.lower()

        state["agent_steps"].append({
            "agent": "browser",
            "action": f"Processing browser request: {last_msg[:60]}",
        })

        is_whatsapp = "whatsapp" in msg_lower

        llm = self._get_llm()
        if llm:
            try:
                from langchain_core.messages import HumanMessage, SystemMessage
                if is_whatsapp:
                    system_text = (
                        "You are a WhatsApp automation assistant for Omni Copilot. "
                        "WhatsApp automation via Playwright is available but requires setup. "
                        f"Note: There is a {WHATSAPP_CONFIRM_MS}ms confirmation window before sending. "
                        "Explain what you would do and ask for confirmation before proceeding."
                    )
                else:
                    system_text = (
                        "You are a web browsing assistant for Omni Copilot. "
                        "You can help users search the web, browse URLs, and scrape pages. "
                        "Playwright browser automation is available. "
                        "Describe what you would do and provide helpful guidance. Be concise."
                    )
                system = SystemMessage(content=system_text)
                response = llm.invoke([system, HumanMessage(content=last_msg)])
                icon = "📱" if is_whatsapp else "🌐"
                label = "WhatsApp" if is_whatsapp else "Browser"
                content = f"{icon} [{label}] {response.content}"
            except Exception:
                content = self._fallback(last_msg, is_whatsapp)
        else:
            content = self._fallback(last_msg, is_whatsapp)

        state["messages"].append({"role": "assistant", "content": content})
        state["agent_steps"].append({"agent": "browser", "action": "Browser operation completed"})
        return state

    def _fallback(self, query: str, is_whatsapp: bool) -> str:
        if is_whatsapp:
            return f"📱 [WhatsApp] Would send message for: \"{query[:60]}\". Confirm wait: {WHATSAPP_CONFIRM_MS}ms."
        return f"🌐 [Browser] Would search/browse for: \"{query[:60]}\". Set GROQ_API_KEY for AI-powered browsing."
