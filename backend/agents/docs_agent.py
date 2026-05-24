"""DocsAgent — Reads/writes Notion pages."""

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
    def __init__(self) -> None:
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            self._llm = _get_llm()
        return self._llm

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        from tools.notion import search_pages, create_page

        last_msg = state["messages"][-1]["content"] if state["messages"] else ""
        msg_lower = last_msg.lower()

        state["agent_steps"].append({"agent": "docs", "action": f"Processing docs request: {last_msg[:60]}"})

        if any(k in msg_lower for k in ("create", "new page", "write", "add page")):
            llm = self._get_llm()
            if llm:
                try:
                    from langchain_core.messages import HumanMessage, SystemMessage
                    system = SystemMessage(content=(
                        "You are a Notion assistant. Help the user create a Notion page. "
                        "If they haven't specified a title or content, ask for it. "
                        "If you have enough info, confirm what page you'd create. Be concise."
                    ))
                    resp = llm.invoke([system, HumanMessage(content=last_msg)])
                    content = f"📝 [Notion] {resp.content}"
                except Exception:
                    content = f"📝 [Notion] I'd create a page for: \"{last_msg[:60]}\""
            else:
                content = f"📝 [Notion] I'd create a page for: \"{last_msg[:60]}\""

        else:
            # Search Notion
            import re
            query = re.sub(r"(search|find|look for|in notion|notion)", "", last_msg, flags=re.IGNORECASE).strip()
            content = search_pages(query or last_msg)

        state["messages"].append({"role": "assistant", "content": content})
        state["agent_steps"].append({"agent": "docs", "action": "Docs operation completed"})
        return state
