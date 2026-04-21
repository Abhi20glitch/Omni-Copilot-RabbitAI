"""Gmail tool stubs."""


def read_inbox(max_results: int = 10) -> str:
    """Read recent Gmail messages."""
    return f"Fetched {max_results} recent emails (stub — connect Gmail to enable)."


def send_email(to: str, subject: str, body: str) -> str:
    """Send an email via Gmail."""
    return f"Sent email to {to}: '{subject}' (stub — connect Gmail to enable)."


def search_emails(query: str) -> str:
    """Search Gmail with a query string."""
    return f"Searching emails for '{query}' (stub — connect Gmail to enable)."
