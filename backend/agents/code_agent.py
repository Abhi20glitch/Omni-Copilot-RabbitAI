"""CodeAgent — Handles GitHub issues, PRs, and code generation."""

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
    def __init__(self) -> None:
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            self._llm = _get_llm()
        return self._llm

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        from tools.github import get_issues, get_pull_requests, get_user_repos, create_issue

        last_msg = state["messages"][-1]["content"] if state["messages"] else ""
        msg_lower = last_msg.lower()

        state["agent_steps"].append({"agent": "code", "action": f"Processing: {last_msg[:60]}"})

        if any(k in msg_lower for k in ("my repos", "repositories", "list repos")):
            content = get_user_repos()

        elif any(k in msg_lower for k in ("pull request", " pr ", "prs")):
            content = get_pull_requests()

        elif "issue" in msg_lower and any(k in msg_lower for k in ("create", "open", "new")):
            # Use LLM to extract issue details
            llm = self._get_llm()
            if llm:
                try:
                    from langchain_core.messages import HumanMessage, SystemMessage
                    system = SystemMessage(content=(
                        "You are a GitHub assistant. Help the user create a GitHub issue. "
                        "Ask for repo name, title, and description if not provided. Be concise."
                    ))
                    resp = llm.invoke([system, HumanMessage(content=last_msg)])
                    content = f"🐙 [GitHub] {resp.content}"
                except Exception:
                    content = get_issues()
            else:
                content = get_issues()

        elif "issue" in msg_lower:
            content = get_issues()

        else:
            # General code question — use LLM
            llm = self._get_llm()
            if llm:
                try:
                    from langchain_core.messages import HumanMessage, SystemMessage
                    system = SystemMessage(content=(
                        "You are an expert software engineer and code assistant. "
                        "Help with code questions, debugging, architecture, and best practices. "
                        "Use code blocks for code snippets. Be concise and accurate."
                    ))
                    # Include conversation history
                    from langchain_core.messages import AIMessage
                    lc_msgs = [system]
                    for m in state["messages"]:
                        if m["role"] == "user":
                            lc_msgs.append(HumanMessage(content=m["content"]))
                        elif m["role"] == "assistant":
                            lc_msgs.append(AIMessage(content=m["content"]))
                    resp = llm.invoke(lc_msgs)
                    content = f"💻 {resp.content}"
                except Exception as e:
                    content = f"💻 [Code] Error: {str(e)}"
            else:
                content = f"💻 [Code] Set GROQ_API_KEY to enable AI code assistance."

        state["messages"].append({"role": "assistant", "content": content})
        state["agent_steps"].append({"agent": "code", "action": "Code operation completed"})
        return state
