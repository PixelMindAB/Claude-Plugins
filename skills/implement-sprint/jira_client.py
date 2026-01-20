"""
Self-contained Jira Client for the implement-sprint skill.
Loads configuration from config.json in the skill directory.
"""

import json
import os
import requests
from requests.auth import HTTPBasicAuth
from pathlib import Path

SKILL_DIR = Path(__file__).parent
CONFIG_FILE = SKILL_DIR / "config.json"


def load_config() -> dict:
    """Load configuration from config.json."""
    if not CONFIG_FILE.exists():
        return {}

    with open(CONFIG_FILE) as f:
        return json.load(f)


def save_config(config: dict) -> None:
    """Save configuration to config.json."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def is_configured() -> bool:
    """Check if the skill is properly configured."""
    config = load_config()
    required = ["jira_domain", "project_key", "email", "api_token"]
    return all(config.get(key) for key in required)


def get_config_status() -> str:
    """Get a human-readable config status."""
    config = load_config()
    if not config:
        return "NOT_CONFIGURED"

    required = ["jira_domain", "project_key", "email", "api_token"]
    missing = [key for key in required if not config.get(key)]

    if missing:
        return f"INCOMPLETE (missing: {', '.join(missing)})"
    return "CONFIGURED"


class JiraClient:
    """A simple client for Jira REST API operations."""

    def __init__(self, domain: str = None, project_key: str = None,
                 email: str = None, api_token: str = None):
        """
        Initialize the Jira client.

        If no arguments provided, loads from config.json.

        Args:
            domain: Your Jira domain (e.g., 'your-domain.atlassian.net')
            project_key: The project key (e.g., 'DEMO')
            email: Jira account email
            api_token: Jira API token
        """
        config = load_config()

        self.domain = domain or config.get("jira_domain")
        self.project_key = project_key or config.get("project_key")
        email = email or config.get("email")
        api_token = api_token or config.get("api_token")

        if not all([self.domain, self.project_key, email, api_token]):
            raise ValueError(
                "Jira not configured. Please run setup or provide all parameters."
            )

        self.base_url = f"https://{self.domain}/rest/api/3"
        self.agile_url = f"https://{self.domain}/rest/agile/1.0"
        self.auth = HTTPBasicAuth(email, api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def get_issue(self, issue_key: str) -> dict:
        """Read a single issue by its key."""
        url = f"{self.base_url}/issue/{issue_key}"
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json()

    def update_issue(self, issue_key: str, summary: str = None, description: str = None) -> bool:
        """Update an existing issue."""
        url = f"{self.base_url}/issue/{issue_key}"
        fields = {}

        if summary:
            fields["summary"] = summary

        if description:
            fields["description"] = {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}]
                    }
                ]
            }

        if not fields:
            return True

        response = requests.put(url, headers=self.headers, auth=self.auth, json={"fields": fields})
        response.raise_for_status()
        return True

    def get_transitions(self, issue_key: str) -> list:
        """Get available transitions for an issue."""
        url = f"{self.base_url}/issue/{issue_key}/transitions"
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json().get("transitions", [])

    def transition_issue(self, issue_key: str, status_name: str) -> bool:
        """Transition an issue to a new status."""
        transitions = self.get_transitions(issue_key)

        transition_id = None
        for t in transitions:
            if t["to"]["name"].lower() == status_name.lower():
                transition_id = t["id"]
                break

        if not transition_id:
            available = [t["to"]["name"] for t in transitions]
            raise ValueError(
                f"Cannot transition to '{status_name}'. Available: {available}"
            )

        url = f"{self.base_url}/issue/{issue_key}/transitions"
        response = requests.post(
            url, headers=self.headers, auth=self.auth,
            json={"transition": {"id": transition_id}}
        )
        response.raise_for_status()
        return True

    def get_boards(self, project_key: str = None) -> list:
        """Get all boards, optionally filtered by project."""
        url = f"{self.agile_url}/board"
        params = {"projectKeyOrId": project_key} if project_key else {}
        response = requests.get(url, headers=self.headers, auth=self.auth, params=params)
        response.raise_for_status()
        return response.json().get("values", [])

    def get_board_for_project(self) -> dict:
        """Get the board for the current project."""
        boards = self.get_boards(self.project_key)
        return boards[0] if boards else None

    def get_sprints(self, board_id: int, state: str = None) -> list:
        """Get sprints for a board."""
        url = f"{self.agile_url}/board/{board_id}/sprint"
        params = {"state": state} if state else {}
        response = requests.get(url, headers=self.headers, auth=self.auth, params=params)
        response.raise_for_status()
        return response.json().get("values", [])

    def get_active_sprint(self, board_id: int) -> dict:
        """Get the active sprint for a board."""
        sprints = self.get_sprints(board_id, state="active")
        return sprints[0] if sprints else None

    def get_sprint_issues(self, sprint_id: int) -> list:
        """Get all issues in a sprint."""
        url = f"{self.agile_url}/sprint/{sprint_id}/issue"
        params = {"fields": "summary,status,issuetype,assignee,description"}
        response = requests.get(url, headers=self.headers, auth=self.auth, params=params)
        response.raise_for_status()
        return response.json().get("issues", [])

    def get_active_sprint_issues(self) -> dict:
        """Get issues from the active sprint of the project's board."""
        board = self.get_board_for_project()
        if not board:
            return None

        sprint = self.get_active_sprint(board["id"])
        if not sprint:
            return None

        issues = self.get_sprint_issues(sprint["id"])
        return {"sprint": sprint, "issues": issues}
