"""Notion tool stubs."""


def search_pages(query: str) -> str:
    """Search Notion workspace for pages matching a query."""
    return f"Searching Notion for '{query}' (stub — connect Notion)."


def read_page(page_id: str) -> str:
    """Read a Notion page by ID."""
    return f"Reading Notion page {page_id} (stub — connect Notion)."


def create_page(title: str, content: str, parent_id: str = "") -> str:
    """Create a new Notion page."""
    return f"Created Notion page '{title}' (stub — connect Notion)."
