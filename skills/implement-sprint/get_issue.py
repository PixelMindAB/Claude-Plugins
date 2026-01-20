#!/usr/bin/env python3
"""Get detailed issue information for implementation."""

import sys
from pathlib import Path

# Import from local jira_client
sys.path.insert(0, str(Path(__file__).parent))
from jira_client import JiraClient, is_configured


def get_description_text(description):
    """Extract plain text from ADF description."""
    if not description:
        return "No description"

    text_parts = []
    for content in description.get("content", []):
        if content.get("type") == "paragraph":
            for item in content.get("content", []):
                if item.get("type") == "text":
                    text_parts.append(item.get("text", ""))

    return " ".join(text_parts) if text_parts else "No description"


def main():
    if not is_configured():
        print("ERROR: Jira not configured. Please set up config.json first.")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python get_issue.py <issue_key>")
        sys.exit(1)

    issue_key = sys.argv[1]

    try:
        client = JiraClient()
        issue = client.get_issue(issue_key)
        fields = issue["fields"]

        print(f"Issue: {issue['key']}")
        print(f"Summary: {fields['summary']}")
        print(f"Status: {fields['status']['name']}")
        print(f"Type: {fields['issuetype']['name']}")
        print(f"Description: {get_description_text(fields.get('description'))}")
        print(f"URL: https://{client.domain}/browse/{issue['key']}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
