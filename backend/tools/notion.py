"""Notion tools — uses access token or OAuth token."""

import os
import json

TOKENS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tokens")


def _get_token() -> str:
    # Prefer env var (internal integration)
    token = os.getenv("NOTION_ACCESS_TOKEN", "")
    if token:
        return token
    # Fall back to OAuth token file
    path = os.path.join(TOKENS_DIR, "notion_token.json")
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
            return data.get("access_token", "")
    return ""


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {_get_token()}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }


def search_pages(query: str) -> str:
    token = _get_token()
    if not token:
        return "Notion not connected. Add NOTION_ACCESS_TOKEN to backend .env."
    try:
        import httpx
        resp = httpx.post(
            "https://api.notion.com/v1/search",
            headers=_headers(),
            json={"query": query, "filter": {"value": "page", "property": "object"}},
        )
        data = resp.json()
        results = data.get("results", [])
        if not results:
            return f"No Notion pages found for '{query}'."
        lines = [f"**Notion pages matching '{query}':**"]
        for page in results[:8]:
            title = ""
            props = page.get("properties", {})
            for prop in props.values():
                if prop.get("type") == "title":
                    title_arr = prop.get("title", [])
                    if title_arr:
                        title = title_arr[0].get("plain_text", "Untitled")
                        break
            url = page.get("url", "")
            lines.append(f"• {title or 'Untitled'} — {url}")
        return "\n".join(lines)
    except Exception as e:
        return f"Notion error: {str(e)}"


def read_page(page_id: str) -> str:
    token = _get_token()
    if not token:
        return "Notion not connected."
    try:
        import httpx
        resp = httpx.get(f"https://api.notion.com/v1/blocks/{page_id}/children", headers=_headers())
        data = resp.json()
        blocks = data.get("results", [])
        lines = []
        for block in blocks[:20]:
            btype = block.get("type", "")
            content = block.get(btype, {})
            rich = content.get("rich_text", [])
            text = "".join(r.get("plain_text", "") for r in rich)
            if text:
                lines.append(text)
        return "\n".join(lines) if lines else "Page is empty."
    except Exception as e:
        return f"Notion error: {str(e)}"


def create_page(title: str, content: str = "", parent_id: str = "") -> str:
    token = _get_token()
    if not token:
        return "Notion not connected."
    try:
        import httpx
        parent = {"type": "page_id", "page_id": parent_id} if parent_id else {"type": "workspace", "workspace": True}
        body = {
            "parent": parent,
            "properties": {"title": {"title": [{"text": {"content": title}}]}},
            "children": [{"object": "block", "type": "paragraph",
                          "paragraph": {"rich_text": [{"text": {"content": content}}]}}] if content else [],
        }
        resp = httpx.post("https://api.notion.com/v1/pages", headers=_headers(), json=body)
        data = resp.json()
        url = data.get("url", "")
        return f"✅ Created Notion page: **{title}**\n{url}"
    except Exception as e:
        return f"Notion error: {str(e)}"
