#!/usr/bin/env python3
"""Get active sprint status."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from jira_client import JiraClient, is_configured, get_config_status


def main():
    status = get_config_status()
    if not status.startswith("CONFIGURED"):
        print(f"CONFIG_STATUS: {status}")
        return

    try:
        client = JiraClient()
        result = client.get_active_sprint_issues()

        if not result:
            print("No active sprint found.")
            return

        sprint = result["sprint"]
        issues = result["issues"]

        print(f"Sprint: {sprint['name']}")
        for issue in issues:
            f = issue["fields"]
            status = f["status"]["name"]
            print(f"{issue['key']} [{status}]: {f['summary']}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
