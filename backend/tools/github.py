"""GitHub tools — uses PyGithub via stored OAuth token."""

import os
import json

TOKENS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tokens")


def _get_token() -> str:
    path = os.path.join(TOKENS_DIR, "github_token.json")
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
            return data.get("access_token", "")
    return ""


def _github_client():
    token = _get_token()
    if not token:
        return None
    try:
        from github import Github
        return Github(token)
    except ImportError:
        return None


def get_issues(repo: str = "", state: str = "open") -> str:
    g = _github_client()
    if not g:
        return "GitHub not connected. Connect GitHub from the Integrations Hub."
    try:
        if repo:
            r = g.get_repo(repo)
        else:
            user = g.get_user()
            repos = list(user.get_repos())
            if not repos:
                return "No repositories found."
            r = repos[0]
        issues = list(r.get_issues(state=state))[:10]
        if not issues:
            return f"No {state} issues found in {r.full_name}."
        lines = [f"**{r.full_name}** — {state} issues:"]
        for issue in issues:
            lines.append(f"• #{issue.number} {issue.title} (@{issue.user.login})")
        return "\n".join(lines)
    except Exception as e:
        return f"GitHub error: {str(e)}"


def get_pull_requests(repo: str = "", state: str = "open") -> str:
    g = _github_client()
    if not g:
        return "GitHub not connected. Connect GitHub from the Integrations Hub."
    try:
        if repo:
            r = g.get_repo(repo)
        else:
            user = g.get_user()
            repos = list(user.get_repos())
            if not repos:
                return "No repositories found."
            r = repos[0]
        prs = list(r.get_pulls(state=state))[:10]
        if not prs:
            return f"No {state} PRs found in {r.full_name}."
        lines = [f"**{r.full_name}** — {state} PRs:"]
        for pr in prs:
            lines.append(f"• #{pr.number} {pr.title} (@{pr.user.login})")
        return "\n".join(lines)
    except Exception as e:
        return f"GitHub error: {str(e)}"


def get_user_repos() -> str:
    g = _github_client()
    if not g:
        return "GitHub not connected."
    try:
        user = g.get_user()
        repos = list(user.get_repos())[:15]
        lines = [f"**Repositories for {user.login}:**"]
        for r in repos:
            lines.append(f"• {r.full_name} ({'private' if r.private else 'public'}) — ⭐{r.stargazers_count}")
        return "\n".join(lines)
    except Exception as e:
        return f"GitHub error: {str(e)}"


def create_issue(repo: str, title: str, body: str = "") -> str:
    g = _github_client()
    if not g:
        return "GitHub not connected."
    try:
        r = g.get_repo(repo)
        issue = r.create_issue(title=title, body=body)
        return f"✅ Created issue #{issue.number}: {issue.title}\n{issue.html_url}"
    except Exception as e:
        return f"GitHub error: {str(e)}"
