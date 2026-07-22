# Wraps the GitHub REST API's issue-creation endpoint.

import asyncio
import requests

from config import GITHUB_TOKEN, GITHUB_REPO


def _create_issue_sync(title: str, body: str) -> tuple[bool, str]:
    if not GITHUB_TOKEN:
        return False, "GitHub integration is not configured (missing GITHUB_TOKEN)."

    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    payload = {"title": title, "body": body, "labels": ["automatic"]}

    response = requests.post(url, headers=headers, json=payload, timeout=10)

    if response.status_code == 201:
        return True, response.json().get("html_url", "")
    else:
        return False, f"GitHub API returned {response.status_code}: {response.text[:200]}"


async def create_issue(title: str, body: str) -> tuple[bool, str]:
    return await asyncio.to_thread(_create_issue_sync, title, body)