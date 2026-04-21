"""Google Calendar tool stubs."""


def get_upcoming_events(max_results: int = 5) -> str:
    """Fetch upcoming Google Calendar events. Requires OAuth credentials."""
    return f"Fetched {max_results} upcoming events (stub — connect Google Calendar to enable)."


def create_calendar_event(summary: str, start: str, end: str, description: str = "") -> str:
    """Create a new Google Calendar event."""
    return f"Created event '{summary}' from {start} to {end} (stub — connect Google Calendar)."


def check_availability(date: str) -> str:
    """Check calendar availability for a given date."""
    return f"Checking availability for {date} (stub — connect Google Calendar)."
