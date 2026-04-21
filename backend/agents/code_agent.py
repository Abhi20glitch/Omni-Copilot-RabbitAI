"""
CodeAgent — Handles GitHub issues, PRs, and code generation.
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
        return ChatGroq(model=DEFAULT_MODEL, api_key=GROQ_API_KEY, temperature=0.2)
    except Exception:
        return None


class CodeAgent:
    """Specialist agent for GitHub and code-related operations."""

    def __init__(self) -> None:
        self.tools = ["get_github_issues", "get_pull_requests", "read_repo_file", "create_issue", "generate_code_snippet"]
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            self._llm = _get_llm()
        return self._llm

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        last_msg = state["messages"][-1]["content"] if state["messages"] else ""

        state["agent_steps"].append({
            "agent": "code",
            "action": f"Processing code request: {last_msg[:60]}",
        })

        msg_lower = last_msg.lower()
        is_github = any(k in msg_lower for k in ("github", "issue", "pr", "pull request", "repo", "commit"))

        llm = self._get_llm()
        if llm:
            try:
                from langchain_core.messages import HumanMessage, SystemMessage
                if is_github:
                    system_text = (
                        "You are a GitHub assistant for Omni Copilot. "
                        "GitHub is not yet connected (OAuth required). "
                        "Help the user understand what GitHub operation you would perform once connected, "
                        "and guide them to connect GitHub from the Integrations Hub. "
                        "Be specific about the repo operation."
                    )
                else:
                    system_text = (
                        "You are a code assistant for Omni Copilot. "
                        "Help the user with their code question. You can generate code snippets, "
                        "explain concepts, and provide technical guidance. "
                        "Be concise and use code blocks where appropriate."
                    )
                system = SystemMessage(content=system_text)
                response = llm.invoke([system, HumanMessage(content=last_msg)])
                icon = "🐙" if is_github else "💻"
                label = "GitHub" if is_github else "Code"
                content = f"{icon} [{label}] {response.content}"
            except Exception:
                content = self._fallback(last_msg, is_github)
        else:
            content = self._fallback(last_msg, is_github)

        state["messages"].append({"role": "assistant", "content": content})
        state["agent_steps"].append({"agent": "code", "action": "Code operation completed"})
        return state

    def _fallback(self, query: str, is_github: bool) -> str:
        if is_github:
            return (
                f"🐙 [GitHub] I'd handle: \"{query[:60]}\" — "
                "connect GitHub from the Integrations Hub to enable this."
            )
        return f"💻 [Code] I received your code request: \"{query[:60]}\". Set GROQ_API_KEY to enable AI code generation."
