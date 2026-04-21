"""
CalendarAgent — Creates/lists Google Calendar events.
"""

from __future__ import annotations
import os
from typing import Any

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama-3.3-70b-versatile")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


def _get_llm():
    if not GROQ_API_KEY:
        return None
    try:
        from langchain_groq import ChatGroq
        return ChatGroq(model=DEFAULT_MODEL, api_key=GROQ_API_KEY, temperature=0.3)
    except Exception:
        return None


class CalendarAgent:
    """Specialist agent for Google Calendar operations."""

    def __init__(self) -> None:
        self.tools = ["get_upcoming_events", "create_calendar_event", "check_availability", "delete_event"]
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            self._llm = _get_llm()
        return self._llm

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        last_msg = state["messages"][-1]["content"] if state["messages"] else ""

        state["agent_steps"].append({
            "agent": "calendar",
            "action": f"Processing calendar request: {last_msg[:60]}",
        })

        llm = self._get_llm()
        if llm:
            try:
                from langchain_core.messages import HumanMessage, SystemMessage
                system = SystemMessage(content=(
                    "You are a Calendar assistant for Omni Copilot. "
                    "Google Calendar is not yet connected (OAuth required). "
                    "Help the user understand what you would do once connected, "
                    "and guide them to connect Google Calendar from the Integrations Hub. "
                    "Be specific about what calendar action you'd perform based on their request. "
                    "Keep responses concise and actionable."
                ))
                response = llm.invoke([system, HumanMessage(content=last_msg)])
                content = f"📅 [Calendar] {response.content}"
            except Exception as e:
                content = self._fallback(last_msg)
        else:
            content = self._fallback(last_msg)

        state["messages"].append({"role": "assistant", "content": content})
        state["agent_steps"].append({"agent": "calendar", "action": "Calendar operation completed"})
        return state

    def _fallback(self, query: str) -> str:
        msg = query.lower()
        if any(k in msg for k in ("create", "schedule", "add", "book")):
            return (
                f"📅 [Calendar] I'd create an event for: \"{query[:60]}\" — "
                "connect Google Calendar from the Integrations Hub to enable this."
            )
        return (
            "📅 [Calendar] I'd fetch your upcoming events — "
            "connect Google Calendar from the Integrations Hub to enable this."
        )
