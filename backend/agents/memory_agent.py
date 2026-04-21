"""
MemoryAgent — Reads/writes to in-memory store (Qdrant optional).
"""

from __future__ import annotations
import os
from typing import Any

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama-3.3-70b-versatile")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MEM0_ENABLED = os.getenv("MEM0_ENABLED", "false").lower() == "true"

# Shared in-process memory store (same as memory router)
_memory_store: dict[str, str] = {}


def _get_llm():
    if not GROQ_API_KEY:
        return None
    try:
        from langchain_groq import ChatGroq
        return ChatGroq(model=DEFAULT_MODEL, api_key=GROQ_API_KEY, temperature=0.3)
    except Exception:
        return None


class MemoryAgent:
    """Specialist agent for managing conversational memory."""

    def __init__(self) -> None:
        self.tools = ["store_memory", "recall_memory", "search_memory", "delete_memory"]
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            self._llm = _get_llm()
        return self._llm

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        last_msg = state["messages"][-1]["content"] if state["messages"] else ""
        msg_lower = last_msg.lower()

        state["agent_steps"].append({
            "agent": "memory",
            "action": f"Processing memory request: {last_msg[:60]}",
        })

        # Determine operation
        is_store = any(k in msg_lower for k in ("remember", "store", "save", "note that"))
        is_recall = any(k in msg_lower for k in ("recall", "what do you know", "what do you remember"))
        is_forget = "forget" in msg_lower

        if is_store:
            # Extract and store the memory
            _memory_store[f"user_note_{len(_memory_store)}"] = last_msg
            content = f"🧠 [Memory] Got it! I've stored that in memory: \"{last_msg[:80]}\""
            state["agent_steps"].append({"agent": "memory", "action": "Memory stored"})
        elif is_recall:
            if _memory_store:
                items = "\n".join(f"• {v}" for v in list(_memory_store.values())[-5:])
                content = f"🧠 [Memory] Here's what I remember:\n{items}"
            else:
                content = "🧠 [Memory] I don't have any stored memories yet. Tell me something to remember!"
            state["agent_steps"].append({"agent": "memory", "action": "Memory recalled"})
        elif is_forget:
            _memory_store.clear()
            content = "🧠 [Memory] Done — I've cleared all stored memories."
            state["agent_steps"].append({"agent": "memory", "action": "Memory cleared"})
        else:
            llm = self._get_llm()
            if llm:
                try:
                    from langchain_core.messages import HumanMessage, SystemMessage
                    memory_context = "\n".join(f"{k}: {v}" for k, v in list(_memory_store.items())[-10:])
                    system = SystemMessage(content=(
                        "You are a Memory assistant for Omni Copilot. "
                        f"Current stored memories:\n{memory_context or 'None'}\n\n"
                        "Help the user manage their memory. Be concise."
                    ))
                    response = llm.invoke([system, HumanMessage(content=last_msg)])
                    content = f"🧠 [Memory] {response.content}"
                except Exception:
                    content = f"🧠 [Memory] Processing: \"{last_msg[:60]}\". Use 'remember', 'recall', or 'forget' to manage memory."
            else:
                content = f"🧠 [Memory] Processing: \"{last_msg[:60]}\". Use 'remember', 'recall', or 'forget' to manage memory."
            state["agent_steps"].append({"agent": "memory", "action": "Memory operation completed"})

        state["messages"].append({"role": "assistant", "content": content})
        return state
