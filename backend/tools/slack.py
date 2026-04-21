"""Slack tool stubs."""


def send_message(channel: str, message: str) -> str:
    """Send a message to a Slack channel."""
    return f"Message sent to #{channel}: '{message}' (stub — connect Slack)."


def read_channel(channel: str, limit: int = 10) -> str:
    """Read recent messages from a Slack channel."""
    return f"Read {limit} messages from #{channel} (stub — connect Slack)."


def search_messages(query: str) -> str:
    """Search Slack messages."""
    return f"Searching Slack for '{query}' (stub — connect Slack)."
