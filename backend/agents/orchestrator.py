"""
OrchestratorAgent — Routes user intent to the correct specialist agent.
"""

from __future__ import annotations
import os
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    user_id: str
    messages: list[dict]
    current_agent: str
    tool_calls: list[dict]
    memory_context: str
    plan: Optional[dict]
    plan_accepted: Optional[bool]
    agent_steps: list[dict]

from agents.docs_agent import DocsAgent
from agents.comms_agent import CommsAgent
from agents.calendar_agent import CalendarAgent
from agents.code_agent import CodeAgent
from agents.browser_agent import BrowserAgent
from agents.memory_agent import MemoryAgent

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama-3.3-70b-versatile")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


def _get_llm():
    if not GROQ_API_KEY:
        return None
    try:
        from langchain_groq import ChatGroq
        return ChatGroq(model=DEFAULT_MODEL, api_key=GROQ_API_KEY, temperature=0.7)
    except Exception:
        return None


class OrchestratorAgent:
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

    @staticmethod
    def _classify_intent(message: str) -> str:
        msg = message.lower()
        if any(k in msg for k in ("calendar", "schedule", "event", "meeting", "remind", "appointment", "what's on my")):
            return "calendar"
        if any(k in msg for k in ("email", "gmail", "mail", "inbox", "send email", "compose")):
            return "comms"
        if any(k in msg for k in ("notion", "document", "doc ", "page", "wiki", "note", "drive")):
            return "docs"
        if any(k in msg for k in ("github", "repo", "issue", "pull request", " pr ", "commit", "code review")):
            return "code"
        if any(k in msg for k in ("whatsapp", "browse", "search web", "scrape", "website", "open browser")):
            return "browser"
        if any(k in msg for k in ("remember", "memory", "recall", "forget", "store this")):
            return "memory"
        return "general"

    def _route_node(self, state: AgentState) -> AgentState:
        last_msg = state["messages"][-1]["content"] if state["messages"] else ""
        intent = self._classify_intent(last_msg)
        state["current_agent"] = intent
        state["agent_steps"].append({"agent": "orchestrator", "action": f"Routing to {intent} agent"})
        return state

    def _calendar_node(self, state): return self.calendar.run(state)
    def _comms_node(self, state): return self.comms.run(state)
    def _docs_node(self, state): return self.docs.run(state)
    def _code_node(self, state): return self.code.run(state)
    def _browser_node(self, state): return self.browser.run(state)
    def _memory_node(self, state): return self.memory.run(state)

    def _general_node(self, state: AgentState) -> AgentState:
        state["agent_steps"].append({"agent": "general", "action": "Generating response"})
        llm = self._get_llm()
        if llm:
            try:
                from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
                lc_messages = [SystemMessage(content=(
                    "You are Omni Copilot, a powerful AI workspace assistant with real integrations. "
                    "You can actually perform actions — not just describe them. You have access to:\n"
                    "- Gmail: read inbox, send emails, search emails\n"
                    "- Google Calendar: list events, create events, check availability\n"
                    "- GitHub: list repos, show issues, show PRs\n"
                    "- Notion: search pages, create pages\n"
                    "- WhatsApp: send messages via browser automation\n"
                    "- Google Drive, Sheets, Meet, Forms\n\n"
                    "When users ask you to do something with these tools, tell them you're doing it "
                    "and provide the result. Be direct and action-oriented. "
                    "If a tool isn't connected yet, tell them to connect it from the Integrations Hub."
                ))]
                for m in state["messages"]:
                    if m["role"] == "user":
                        lc_messages.append(HumanMessage(content=m["content"]))
                    elif m["role"] == "assistant":
                        lc_messages.append(AIMessage(content=m["content"]))
                response = llm.invoke(lc_messages)
                content = response.content
            except Exception as e:
                content = f"Error connecting to AI: {str(e)[:100]}"
        else:
            content = "Please set GROQ_API_KEY in backend .env to enable AI responses."

        state["messages"].append({"role": "assistant", "content": content})
        state["agent_steps"].append({"agent": "general", "action": "Response generated"})
        return state

    @staticmethod
    def _pick_agent(state: AgentState) -> str:
        return state.get("current_agent", "general")

    def _build_graph(self):
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
            "calendar": "calendar", "comms": "comms", "docs": "docs",
            "code": "code", "browser": "browser", "memory": "memory", "general": "general",
        })
        for node in ("calendar", "comms", "docs", "code", "browser", "memory", "general"):
            g.add_edge(node, END)
        return g.compile()

    def run(self, user_id: str, messages: list[dict]) -> AgentState:
        initial: AgentState = {
            "user_id": user_id, "messages": list(messages), "current_agent": "",
            "tool_calls": [], "memory_context": "", "plan": None,
            "plan_accepted": None, "agent_steps": [],
        }
        return self.graph.invoke(initial)
