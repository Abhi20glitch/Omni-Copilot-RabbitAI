"""CommsAgent — Actually sends/reads Gmail using stored OAuth token."""

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
        return ChatGroq(model=DEFAULT_MODEL, api_key=GROQ_API_KEY, temperature=0.3)
    except Exception:
        return None


class CommsAgent:
    def __init__(self):
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            self._llm = _get_llm()
        return self._llm

    def run(self, state: dict[str, Any]) -> dict[str, Any]:
        from tools.gmail import read_inbox, send_email, search_emails

        last_msg = state["messages"][-1]["content"] if state["messages"] else ""
        msg_lower = last_msg.lower()
        state["agent_steps"].append({"agent": "comms", "action": f"Processing: {last_msg[:60]}"})

        # Send email — extract details with LLM
        if any(k in msg_lower for k in ("send", "compose", "write an email", "email to")):
            llm = self._get_llm()
            if llm:
                try:
                    from langchain_core.messages import HumanMessage, SystemMessage
                    extract = llm.invoke([
                        SystemMessage(content=(
                            "Extract email details from the user message. "
                            "Reply ONLY as JSON with no extra text: {\"to\": \"email address\", \"subject\": \"subject line\", \"body\": \"full email body\"}. "
                            "For the body, write a proper short email based on what the user wants to say. "
                            "Fix any obvious typos in the email address (e.g. gmailcom -> gmail.com)."
                        )),
                        HumanMessage(content=last_msg)
                    ])
                    import json
                    raw = extract.content.strip()
                    match = re.search(r'\{.*\}', raw, re.DOTALL)
                    if match:
                        details = json.loads(match.group())
                        to = details.get("to", "").strip()
                        subject = details.get("subject", "").strip()
                        body = details.get("body", "").strip()
                        if to and subject and body:
                            result = send_email(to, subject, body)
                            content = f"{result}\n\n**Details:**\n- To: {to}\n- Subject: {subject}\n- Body: {body}"
                        else:
                            content = f"📧 I need more details to send the email.\n- To: {to or '❌ missing'}\n- Subject: {subject or '❌ missing'}\n- Body: {body or '❌ missing'}"
                    else:
                        content = "📧 Couldn't parse email details. Please say: 'Send email to [address], subject: [subject], body: [message]'"
                except Exception as e:
                    content = f"📧 Error: {str(e)}"
            else:
                content = "📧 Set GROQ_API_KEY to enable email composition."

        # Search emails
        elif any(k in msg_lower for k in ("search", "find email", "look for email")):
            query = re.sub(r"(search|find|look for|emails? (about|from|with))", "", last_msg, flags=re.IGNORECASE).strip()
            content = search_emails(query or last_msg)

        # Default: read inbox
        else:
            content = read_inbox(10)

        state["messages"].append({"role": "assistant", "content": content})
        state["agent_steps"].append({"agent": "comms", "action": "Email task completed"})
        return state
