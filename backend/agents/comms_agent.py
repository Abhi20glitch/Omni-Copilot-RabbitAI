"""
CommsAgent — Sends/reads Gmail and Slack messages.
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


class CommsAgent:
    """Specialist agent for Gmail and Slack communications."""

    def __init__(self) -> None:
        self.tools = ["read_gmail_inbox", "send_gmail", "read_slack_channel", "send_slack_message", "search_slack"]
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            self._llm = _get_llm()
        return self._llm

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        last_msg = state["messages"][-1]["content"] if state["messages"] else ""

        state["agent_steps"].append({
            "agent": "comms",
            "action": f"Processing communication request: {last_msg[:60]}",
        })

        msg_lower = last_msg.lower()
        is_slack = any(k in msg_lower for k in ("slack", "channel"))
        platform = "Slack" if is_slack else "Gmail"
        icon = "💬" if is_slack else "📧"

        llm = self._get_llm()
        if llm:
            try:
                from langchain_core.messages import HumanMessage, SystemMessage
                system = SystemMessage(content=(
                    f"You are a {platform} assistant for Omni Copilot. "
                    f"{platform} is not yet connected (OAuth required). "
                    "Help the user understand what you would do once connected, "
                    f"and guide them to connect {platform} from the Integrations Hub. "
                    "Be specific about what communication action you'd perform. "
                    "Keep responses concise."
                ))
                response = llm.invoke([system, HumanMessage(content=last_msg)])
                content = f"{icon} [{platform}] {response.content}"
            except Exception:
                content = self._fallback(last_msg, platform, icon)
        else:
            content = self._fallback(last_msg, platform, icon)

        state["messages"].append({"role": "assistant", "content": content})
        state["agent_steps"].append({"agent": "comms", "action": "Communication task completed"})
        return state

    def _fallback(self, query: str, platform: str, icon: str) -> str:
        return (
            f"{icon} [{platform}] I'd process: \"{query[:60]}\" — "
            f"connect {platform} from the Integrations Hub to enable this."
        )
