"""
DocsAgent — Reads/writes Google Drive docs and Notion pages.
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


class DocsAgent:
    """Specialist agent for document operations across Drive & Notion."""

    def __init__(self) -> None:
        self.tools = ["search_drive_files", "read_drive_document", "search_notion_pages", "read_notion_page", "create_notion_page"]
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            self._llm = _get_llm()
        return self._llm

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        last_msg = state["messages"][-1]["content"] if state["messages"] else ""

        state["agent_steps"].append({
            "agent": "docs",
            "action": f"Searching documents for: {last_msg[:60]}",
        })

        msg_lower = last_msg.lower()
        is_notion = "notion" in msg_lower
        platform = "Notion" if is_notion else "Google Drive"
        icon = "📝" if is_notion else "📄"

        llm = self._get_llm()
        if llm:
            try:
                from langchain_core.messages import HumanMessage, SystemMessage
                system = SystemMessage(content=(
                    f"You are a {platform} assistant for Omni Copilot. "
                    f"{platform} is not yet connected (OAuth required). "
                    "Help the user understand what document operation you would perform once connected, "
                    f"and guide them to connect {platform} from the Integrations Hub. "
                    "Be specific and concise."
                ))
                response = llm.invoke([system, HumanMessage(content=last_msg)])
                content = f"{icon} [{platform}] {response.content}"
            except Exception:
                content = self._fallback(last_msg, platform, icon)
        else:
            content = self._fallback(last_msg, platform, icon)

        state["messages"].append({"role": "assistant", "content": content})
        state["agent_steps"].append({"agent": "docs", "action": "Document operation completed"})
        return state

    def _fallback(self, query: str, platform: str, icon: str) -> str:
        return (
            f"{icon} [{platform}] I'd search for: \"{query[:60]}\" — "
            f"connect {platform} from the Integrations Hub to enable this."
        )
