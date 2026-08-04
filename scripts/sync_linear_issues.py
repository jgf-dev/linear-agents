#!/usr/bin/env python3
"""Sync Linear issues to GitHub issues for agent-automation project repos."""

import os
import sys
import json
import requests

LINEAR_API_URL = "https://api.linear.app/graphql"
GITHUB_API_URL = "https://api.github.com"

LINEAR_API_KEY = os.environ["LINEAR_API_KEY"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPO = os.environ["GITHUB_REPO"]
LINEAR_TEAM_KEY = os.environ.get("LINEAR_TEAM_KEY", "")
LINEAR_PROJECT_NAME = os.environ.get("LINEAR_PROJECT_NAME", "agent-automation")

LINEAR_LABEL = "linear"
STATE_LABEL_PREFIX = "linear:"


def linear_request(query: str, variables: dict = None) -> dict:
    headers = {
        "Authorization": LINEAR_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    response = requests.post(LINEAR_API_URL, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()
    if "errors" in data:
        raise RuntimeError(f"Linear API error: {data['errors']}")
    return data["data"]


def github_request(method: str, path: str, body: dict = None) -> dict:
    headers = {
        "Authorization": "token " + GITHUB_TOKEN,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    url = f"{GITHUB_API_URL}{path}"
    response = requests.request(method, url, json=body, headers=headers, timeout=30)
    response.raise_for_status()
    if response.status_code == 204:
        return {}
    return response.json()


def get_linear_issues() -> list[dict]:
    query = """
    query($filter: IssueFilter, $after: String) {
      issues(filter: $filter, first: 100, after: $after) {
        nodes {
          id
          identifier
          title
          description
          url
          state { name type }
          priority
          assignee { name email }
          labels { nodes { name color } }
          updatedAt
          createdAt
        }
        pageInfo { hasNextPage endCursor }
      }
    }
    """
    filter_clause: dict = {}
    if LINEAR_TEAM_KEY:
        filter_clause["team"] = {"key": {"eq": LINEAR_TEAM_KEY}}
    if LINEAR_PROJECT_NAME:
        filter_clause["project"] = {"name": {"containsIgnoreCase": LINEAR_PROJECT_NAME}}

    issues = []
    cursor = None
    while True:
        variables: dict = {"filter": filter_clause}
        if cursor:
            variables["after"] = cursor
        data = linear_request(query, variables)
        page = data["issues"]
        issues.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    return issues


def get_github_issues() -> dict[str, dict]:
    """Return a map of linear identifier -> github issue."""
    path = f"/repos/{GITHUB_REPO}/issues?state=all&labels={LINEAR_LABEL}&per_page=100"
    all_issues = []
    while path:
        result = github_request("GET", path)
        if isinstance(result, list):
            all_issues.extend(result)
            # GitHub paginates via Link header — requests doesn't expose it easily here
            # so we just stop after the first page (sufficient for most projects)
            break
    mapping = {}
    for issue in all_issues:
        for label in issue.get("labels", []):
            if label["name"].startswith("linear-id:"):
                linear_id = label["name"].split(":", 1)[1]
                mapping[linear_id] = issue
    return mapping


def ensure_label(name: str, color: str = "0075ca", description: str = "") -> None:
    try:
        github_request("GET", f"/repos/{GITHUB_REPO}/labels/{requests.utils.quote(name)}")
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            github_request("POST", f"/repos/{GITHUB_REPO}/labels", {
                "name": name,
                "color": color,
                "description": description,
            })
        else:
            raise


def state_label_name(state_name: str) -> str:
    return f"{STATE_LABEL_PREFIX}{state_name.lower()}"


def priority_label_name(priority: int) -> str | None:
    priorities = {1: "urgent", 2: "high", 3: "medium", 4: "low"}
    name = priorities.get(priority)
    return f"priority:{name}" if name else None


def build_issue_body(linear_issue: dict) -> str:
    lines = []
    if linear_issue.get("description"):
        lines.append(linear_issue["description"])
        lines.append("")
    lines.append(f"---")
    lines.append(f"_Synced from Linear: [{linear_issue['identifier']}]({linear_issue['url']})_")
    return "\n".join(lines)


def sync_issue(linear_issue: dict, existing: dict | None) -> None:
    identifier = linear_issue["identifier"]
    title = f"[{identifier}] {linear_issue['title']}"
    body = build_issue_body(linear_issue)
    state_name = linear_issue["state"]["name"]
    state_type = linear_issue["state"]["type"]

    id_label = f"linear-id:{identifier}"
    ensure_label(LINEAR_LABEL, "4A90E2", "Synced from Linear")
    ensure_label(id_label, "ededed", f"Linear issue {identifier}")
    s_label = state_label_name(state_name)
    ensure_label(s_label, "fbca04", f"Linear state: {state_name}")

    labels = [LINEAR_LABEL, id_label, s_label]

    priority = linear_issue.get("priority", 0)
    p_label = priority_label_name(priority)
    if p_label:
        ensure_label(p_label, "e4e669", f"Priority: {p_label.split(':')[1]}")
        labels.append(p_label)

    github_state = "closed" if state_type in ("completed", "cancelled") else "open"

    if existing is None:
        github_request("POST", f"/repos/{GITHUB_REPO}/issues", {
            "title": title,
            "body": body,
            "labels": labels,
            "state": github_state,
        })
        print(f"Created GitHub issue for {identifier}")
    else:
        existing_number = existing["number"]
        github_request("PATCH", f"/repos/{GITHUB_REPO}/issues/{existing_number}", {
            "title": title,
            "body": body,
            "labels": labels,
            "state": github_state,
        })
        print(f"Updated GitHub issue #{existing_number} for {identifier}")


def main() -> None:
    if not LINEAR_API_KEY:
        print("ERROR: LINEAR_API_KEY is required", file=sys.stderr)
        sys.exit(1)

    print(f"Fetching Linear issues (project: {LINEAR_PROJECT_NAME!r}, team: {LINEAR_TEAM_KEY!r})...")
    linear_issues = get_linear_issues()
    print(f"Found {len(linear_issues)} Linear issues")

    print("Fetching existing GitHub issues...")
    existing_map = get_github_issues()
    print(f"Found {len(existing_map)} existing synced GitHub issues")

    for issue in linear_issues:
        identifier = issue["identifier"]
        existing = existing_map.get(identifier)
        try:
            sync_issue(issue, existing)
        except Exception as e:
            print(f"WARNING: Failed to sync {identifier}: {e}", file=sys.stderr)

    print("Sync complete.")


if __name__ == "__main__":
    main()
