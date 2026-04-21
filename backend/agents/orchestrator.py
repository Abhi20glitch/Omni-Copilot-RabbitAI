"""
OrchestratorAgent — Routes user intent to the correct specialist agent.

Uses LangGraph to build a multi-agent state graph.  The orchestrator
inspects the latest user message, classifies intent via LLM, and delegates
to one of: DocsAgent, CommsAgent, CalendarAgent, CodeAgent, BrowserAgent,
or MemoryAgent.
"""

from __future__ import annotations

import os
from typing import TypedDict, Optional

from langgraph.graph import StateGraph, END


# ── Shared state schema used by every node ────────────────────────────
class AgentState(TypedDict):
    user_id: str
    messages: list[dict]           # Full conversation history
    current_agent: str
    tool_calls: list[dict]
    memory_context: str
    plan: Optional[dict]           # Structured plan for user approval
    plan_accepted: Optional[bool]
    agent_steps: list[dict]        # Timeline steps for frontend


# ── Specialist imports (lazy to avoid circular deps) ──────────────────
from agents.docs_agent import DocsAgent        # noqa: E402
from agents.comms_agent import CommsAgent      # noqa: E402
from agents.calendar_agent import CalendarAgent  # noqa: E402
from agents.code_agent import CodeAgent        # noqa: E402
from agents.browser_agent import BrowserAgent  # noqa: E402
from agents.memory_agent import MemoryAgent    # noqa: E402


DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama-3.3-70b-versatile")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


def _get_llm():
    """Lazily initialise the Groq LLM."""
    if not GROQ_API_KEY:
        return None
    try:
        from langchain_groq import ChatGroq
        return ChatGroq(model=DEFAULT_MODEL, api_key=GROQ_API_KEY, temperature=0.7)
    except Exception:
        return None


class OrchestratorAgent:
    """
    Central router that analyses user intent and dispatches work to the
    appropriate specialist agent.  Returns an updated AgentState with
    agent_steps populated for the frontend timeline.
    """

    def __init__(self) -> None:
        self.docs = DocsAgent()
        self.comms = CommsAgent()
        self.calendar = CalendarAgent()
        self.code = CodeAgent()
        self.browser = BrowserAgent()
        self.memory = MemoryAgent()
        self._llm = None
        self.graph = self._build_graph()

    def _get_llm(self):
        if self._llm is None:
            self._llm = _get_llm()
        return self._llm

    # ── Intent classification ─────────────────────────────────────────
    @staticmethod
    def _classify_intent(message: str) -> str:
        """Classify the user's intent to route to the correct agent."""
        msg = message.lower()
        if any(k in msg for k in ("calendar", "schedule", "event", "meeting", "remind", "appointment")):
            return "calendar"
        if any(k in msg for k in ("email", "gmail", "mail", "slack", "message", "send", "inbox")):
            return "comms"
        if any(k in msg for k in ("doc", "notion", "drive", "document", "page", "wiki", "note")):
            return "docs"
        if any(k in msg for k in ("github", "code", "pr", "issue", "repo", "commit", "pull request")):
            return "code"
        if any(k in msg for k in ("browse", "search web", "whatsapp", "scrape", "website", "google")):
            return "browser"
        if any(k in msg for k in ("remember", "memory", "recall", "forget", "store this")):
            return "memory"
        return "general"

    # ── LangGraph nodes ───────────────────────────────────────────────
    def _route_node(self, state: AgentState) -> AgentState:
        """Classify intent and set current_agent."""
        last_msg = state["messages"][-1]["content"] if state["messages"] else ""
        intent = self._classify_intent(last_msg)
        state["current_agent"] = intent
        state["agent_steps"].append({
            "agent": "orchestrator",
            "action": f"Classified intent → {intent}",
        })
        return state

    def _calendar_node(self, state: AgentState) -> AgentState:
        return self.calendar.run(state)

    def _comms_node(self, state: AgentState) -> AgentState:
        return self.comms.run(state)

    def _docs_node(self, state: AgentState) -> AgentState:
        return self.docs.run(state)

    def _code_node(self, state: AgentState) -> AgentState:
        return self.code.run(state)

    def _browser_node(self, state: AgentState) -> AgentState:
        return self.browser.run(state)

    def _memory_node(self, state: AgentState) -> AgentState:
        return self.memory.run(state)

    def _general_node(self, state: AgentState) -> AgentState:
        """General conversation — uses Groq LLM if available, otherwise fallback."""
        state["agent_steps"].append({
            "agent": "general",
            "action": "Generating response with LLM",
        })

        llm = self._get_llm()
        if llm:
            try:
                from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
                lc_messages = [
                    SystemMessage(content=(
                        "You are Omni Copilot, a helpful universal AI workspace assistant. "
                        "You help users manage their productivity tools including Gmail, Google Calendar, "
                        "GitHub, Notion, Slack, Google Drive, Discord, and WhatsApp. "
                        "Be concise, helpful, and friendly. When users ask about connecting tools, "
                        "direct them to the Integrations Hub."
                    ))
                ]
                for m in state["messages"]:
                    if m["role"] == "user":
                        lc_messages.append(HumanMessage(content=m["content"]))
                    elif m["role"] == "assistant":
                        lc_messages.append(AIMessage(content=m["content"]))

                response = llm.invoke(lc_messages)
                content = response.content
            except Exception as e:
                content = (
                    f"I'm having trouble connecting to the AI model right now. "
                    f"Please ensure GROQ_API_KEY is set in your backend .env file. "
                    f"Error: {str(e)[:100]}"
                )
        else:
            last_msg = state["messages"][-1]["content"] if state["messages"] else ""
            content = (
                f"I received your message: \"{last_msg[:80]}\". "
                "To enable full AI responses, please set GROQ_API_KEY in your backend .env file. "
                "I can help you with Calendar, Email/Slack, Docs/Notion, GitHub, Web Browsing, and Memory. "
                "Connect your tools from the Integrations Hub to get started."
            )

        state["messages"].append({"role": "assistant", "content": content})
        state["agent_steps"].append({
            "agent": "general",
            "action": "Response generated",
        })
        return state

    # ── Conditional edge ──────────────────────────────────────────────
    @staticmethod
    def _pick_agent(state: AgentState) -> str:
        return state.get("current_agent", "general")

    # ── Build the graph ───────────────────────────────────────────────
    def _build_graph(self) -> StateGraph:
        g = StateGraph(AgentState)

        g.add_node("route", self._route_node)
        g.add_node("calendar", self._calendar_node)
        g.add_node("comms", self._comms_node)
        g.add_node("docs", self._docs_node)
        g.add_node("code", self._code_node)
        g.add_node("browser", self._browser_node)
        g.add_node("memory", self._memory_node)
        g.add_node("general", self._general_node)

        g.set_entry_point("route")
        g.add_conditional_edges("route", self._pick_agent, {
            "calendar": "calendar",
            "comms": "comms",
            "docs": "docs",
            "code": "code",
            "browser": "browser",
            "memory": "memory",
            "general": "general",
        })

        for node in ("calendar", "comms", "docs", "code", "browser", "memory", "general"):
            g.add_edge(node, END)

        return g.compile()

    # ── Public API ────────────────────────────────────────────────────
    def run(self, user_id: str, messages: list[dict]) -> AgentState:
        """Execute the full orchestration graph and return final state."""
        initial: AgentState = {
            "user_id": user_id,
            "messages": list(messages),
            "current_agent": "",
            "tool_calls": [],
            "memory_context": "",
            "plan": None,
            "plan_accepted": None,
            "agent_steps": [],
        }
        return self.graph.invoke(initial)
