"""GitHub tool stubs."""


def get_issues(repo: str, state: str = "open") -> str:
    """Fetch issues from a GitHub repository."""
    return f"Fetching {state} issues from {repo} (stub — connect GitHub)."


def get_pull_requests(repo: str, state: str = "open") -> str:
    """Fetch pull requests from a GitHub repository."""
    return f"Fetching {state} PRs from {repo} (stub — connect GitHub)."


def read_file(repo: str, path: str) -> str:
    """Read a file from a GitHub repository."""
    return f"Reading {path} from {repo} (stub — connect GitHub)."


def create_issue(repo: str, title: str, body: str) -> str:
    """Create a new issue in a GitHub repository."""
    return f"Created issue '{title}' in {repo} (stub — connect GitHub)."
