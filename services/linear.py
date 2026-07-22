# Wraps Linear's GraphQL API for issue creation.

import asyncio
import requests

from config import LINEAR_API_KEY, LINEAR_TEAM_ID

LINEAR_API_URL = "https://api.linear.app/graphql"

_CREATE_ISSUE_MUTATION = """
mutation IssueCreate($teamId: String!, $title: String!, $description: String!) {
  issueCreate(input: { teamId: $teamId, title: $title, description: $description }) {
    success
    issue {
      url
    }
  }
}
"""


def _create_issue_sync(title: str, description: str) -> tuple[bool, str]:
    if not LINEAR_API_KEY or not LINEAR_TEAM_ID:
        return False, "Linear integration is not configured (missing LINEAR_API_KEY or LINEAR_TEAM_ID)."

    headers = {
        "Authorization": LINEAR_API_KEY,
        "Content-Type": "application/json",
    }
    variables = {"teamId": LINEAR_TEAM_ID, "title": title, "description": description}

    response = requests.post(
        LINEAR_API_URL,
        headers=headers,
        json={"query": _CREATE_ISSUE_MUTATION, "variables": variables},
        timeout=10,
    )

    if response.status_code != 200:
        return False, f"Linear API returned {response.status_code}: {response.text[:200]}"

    data = response.json()
    result = data.get("data", {}).get("issueCreate", {})
    if result.get("success"):
        return True, result.get("issue", {}).get("url", "")
    else:
        errors = data.get("errors", [])
        return False, f"Linear rejected the request: {errors}"


async def create_issue(title: str, description: str) -> tuple[bool, str]:
    return await asyncio.to_thread(_create_issue_sync, title, description)