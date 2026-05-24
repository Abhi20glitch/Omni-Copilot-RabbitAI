"""CalendarAgent — Actually reads/creates Google Calendar events."""

from __future__ import annotations
import os, re
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


class CalendarAgent:
    def __init__(self):
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            self._llm = _get_llm()
        return self._llm

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        from tools.google_calendar import get_upcoming_events, create_calendar_event, check_availability

        last_msg = state["messages"][-1]["content"] if state["messages"] else ""
        msg_lower = last_msg.lower()
        state["agent_steps"].append({"agent": "calendar", "action": f"Processing: {last_msg[:60]}"})

        if any(k in msg_lower for k in ("create", "schedule", "add event", "book", "new event", "set up")):
            llm = self._get_llm()
            if llm:
                try:
                    from langchain_core.messages import HumanMessage, SystemMessage
                    import json
                    from datetime import datetime
                    today = datetime.now().strftime("%Y-%m-%d")
                    extract = llm.invoke([
                        SystemMessage(content=(
                            f"Today is {today}. Extract calendar event details from the user message. "
                            "Reply ONLY as JSON: {\"summary\": \"title\", \"start\": \"2026-05-24T10:00:00\", \"end\": \"2026-05-24T11:00:00\", \"description\": \"\"}. "
                            "Use ISO 8601 format for dates. If time not specified, use 09:00. If duration not specified, assume 1 hour."
                        )),
                        HumanMessage(content=last_msg)
                    ])
                    raw = extract.content.strip()
                    match = re.search(r'\{.*\}', raw, re.DOTALL)
                    if match:
                        details = json.loads(match.group())
                        summary = details.get("summary", "")
                        start = details.get("start", "")
                        end = details.get("end", "")
                        if summary and start and end:
                            content = create_calendar_event(summary, start, end, details.get("description", ""))
                        else:
                            content = f"📅 To create an event I need a title, date, and time. Please provide the missing details."
                    else:
                        content = "📅 Please specify the event title, date, and time."
                except Exception as e:
                    content = f"📅 Calendar error: {str(e)}"
            else:
                content = "📅 Set GROQ_API_KEY to enable event creation."

        elif any(k in msg_lower for k in ("available", "free", "busy")):
            date_match = re.search(r"\d{4}-\d{2}-\d{2}", last_msg)
            if date_match:
                content = check_availability(date_match.group())
            else:
                from datetime import date
                content = check_availability(date.today().isoformat())

        else:
            content = get_upcoming_events(10)

        state["messages"].append({"role": "assistant", "content": content})
        state["agent_steps"].append({"agent": "calendar", "action": "Calendar operation completed"})
        return state
