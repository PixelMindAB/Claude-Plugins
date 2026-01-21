"""
Self-contained Jira Client for the implement-sprint skill.
Loads configuration from config.json in the skill directory.
"""

import argparse
import json
import sys
import requests
from requests.auth import HTTPBasicAuth
from pathlib import Path

SKILL_DIR = Path(__file__).parent
PLUGIN_CONFIG_FILE = SKILL_DIR / "config.json"
PROJECT_CONFIG_NAME = ".jira_config.json"


def get_project_config_path() -> Path:
    """Get the path to the project-level config file in current working directory."""
    return Path.cwd() / PROJECT_CONFIG_NAME


def load_plugin_config() -> dict:
    """Load credentials from plugin-level config.json."""
    if PLUGIN_CONFIG_FILE.exists():
        with open(PLUGIN_CONFIG_FILE) as f:
            return json.load(f)
    return {}


def load_project_config() -> dict:
    """Load project_key from project-level .jira_config.json."""
    project_config = get_project_config_path()
    if project_config.exists():
        with open(project_config) as f:
            return json.load(f)
    return {}


def load_config() -> dict:
    """Load merged configuration.

    - Credentials (jira_domain, email, api_token) from plugin config.json
    - Project key (project_key) from project-level .jira_config.json
    """
    config = load_plugin_config()
    project_config = load_project_config()

    # Project config overrides project_key only
    if project_config.get("project_key"):
        config["project_key"] = project_config["project_key"]

    return config


def save_plugin_config(config: dict) -> Path:
    """Save credentials to plugin config.json."""
    with open(PLUGIN_CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    return PLUGIN_CONFIG_FILE


def save_project_config(project_key: str) -> Path:
    """Save project_key to .jira_config.json in current directory."""
    config_path = get_project_config_path()
    with open(config_path, "w") as f:
        json.dump({"project_key": project_key}, f, indent=2)
    return config_path


def is_configured() -> bool:
    """Check if the skill is properly configured."""
    config = load_config()
    required = ["jira_domain", "project_key", "email", "api_token"]
    return all(config.get(key) for key in required)


def get_config_status() -> str:
    """Get a human-readable config status."""
    plugin_config = load_plugin_config()
    project_config = load_project_config()

    # Check credentials in plugin config
    credentials = ["jira_domain", "email", "api_token"]
    missing_creds = [key for key in credentials if not plugin_config.get(key)]

    # Check project_key in project config
    has_project_key = bool(project_config.get("project_key"))

    if missing_creds:
        return f"CREDENTIALS_MISSING (missing: {', '.join(missing_creds)})"

    if not has_project_key:
        return f"PROJECT_NOT_CONFIGURED (create {PROJECT_CONFIG_NAME} with project_key)"

    return f"CONFIGURED (project: {project_config['project_key']})"


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

    def start_sprint(self, sprint_id: int, duration_days: int = 14) -> bool:
        """Start a sprint by setting its state to active.

        Args:
            sprint_id: The ID of the sprint to start
            duration_days: Sprint duration in days (default: 14)

        Returns:
            True if successful
        """
        from datetime import datetime, timedelta

        start_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')
        end_date = (datetime.now() + timedelta(days=duration_days)).strftime('%Y-%m-%dT%H:%M:%S.000Z')

        url = f"{self.agile_url}/sprint/{sprint_id}"
        response = requests.post(
            url, headers=self.headers, auth=self.auth,
            json={
                'state': 'active',
                'startDate': start_date,
                'endDate': end_date
            }
        )
        response.raise_for_status()
        return True

    def close_sprint(self, sprint_id: int) -> bool:
        """Close a sprint by setting its state to closed.

        Args:
            sprint_id: The ID of the sprint to close

        Returns:
            True if successful
        """
        url = f"{self.agile_url}/sprint/{sprint_id}"
        response = requests.post(
            url, headers=self.headers, auth=self.auth,
            json={'state': 'closed'}
        )
        response.raise_for_status()
        return True

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

    def add_comment(self, issue_key: str, comment: str) -> bool:
        """Add a comment to an issue.

        Args:
            issue_key: The issue key (e.g., 'DEMO-18')
            comment: The comment text to add

        Returns:
            True if successful
        """
        url = f"{self.base_url}/issue/{issue_key}/comment"
        body = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": comment}]
                    }
                ]
            }
        }
        response = requests.post(url, headers=self.headers, auth=self.auth, json=body)
        response.raise_for_status()
        return True

    def get_comments(self, issue_key: str) -> list:
        """Get all comments for an issue.

        Args:
            issue_key: The issue key (e.g., 'DEMO-18')

        Returns:
            List of comments
        """
        url = f"{self.base_url}/issue/{issue_key}/comment"
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        return response.json().get("comments", [])

    def create_issue(self, summary: str, issue_type: str = "Task", description: str = None) -> dict:
        """Create a new issue in the project.

        Args:
            summary: The issue summary/title
            issue_type: The issue type (default: "Task")
            description: Optional description

        Returns:
            The created issue data including key and id
        """
        url = f"{self.base_url}/issue"
        fields = {
            "project": {"key": self.project_key},
            "summary": summary,
            "issuetype": {"name": issue_type}
        }

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

        response = requests.post(url, headers=self.headers, auth=self.auth, json={"fields": fields})
        response.raise_for_status()
        return response.json()

    def create_sprint(self, name: str, board_id: int = None) -> dict:
        """Create a new sprint.

        Args:
            name: The sprint name
            board_id: The board ID (if not provided, uses project's board)

        Returns:
            The created sprint data including id
        """
        if not board_id:
            board = self.get_board_for_project()
            if not board:
                raise ValueError("No board found for project")
            board_id = board["id"]

        url = f"{self.agile_url}/sprint"
        response = requests.post(
            url, headers=self.headers, auth=self.auth,
            json={"name": name, "originBoardId": board_id}
        )
        response.raise_for_status()
        return response.json()

    def move_issues_to_sprint(self, sprint_id: int, issue_keys: list) -> bool:
        """Move issues to a sprint.

        Args:
            sprint_id: The sprint ID
            issue_keys: List of issue keys to move

        Returns:
            True if successful
        """
        url = f"{self.agile_url}/sprint/{sprint_id}/issue"
        response = requests.post(
            url, headers=self.headers, auth=self.auth,
            json={"issues": issue_keys}
        )
        response.raise_for_status()
        return True


def get_description_text(description: dict) -> str:
    """Extract plain text from Atlassian Document Format (ADF) description.

    Args:
        description: The ADF description dict from a Jira issue

    Returns:
        Plain text extracted from the description
    """
    if not description:
        return "No description"

    text_parts = []
    for content in description.get("content", []):
        if content.get("type") == "paragraph":
            for item in content.get("content", []):
                if item.get("type") == "text":
                    text_parts.append(item.get("text", ""))

    return " ".join(text_parts) if text_parts else "No description"


# =============================================================================
# CLI Interface
# =============================================================================

def cmd_status(args):
    """Show configuration status and active sprint issues."""
    status = get_config_status()
    if not status.startswith("CONFIGURED"):
        print(f"CONFIG_STATUS: {status}")
        return 1

    try:
        client = JiraClient()
        result = client.get_active_sprint_issues()

        if not result:
            print("No active sprint found.")
            return 0

        sprint = result["sprint"]
        issues = result["issues"]

        print(f"Sprint: {sprint['name']}")
        for issue in issues:
            f = issue["fields"]
            issue_status = f["status"]["name"]
            print(f"{issue['key']} [{issue_status}]: {f['summary']}")
        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_get_issue(args):
    """Get detailed information for a specific issue."""
    if not is_configured():
        print("ERROR: Jira not configured. Please set up config.json first.")
        return 1

    try:
        client = JiraClient()
        issue = client.get_issue(args.issue_key)
        fields = issue["fields"]

        print(f"Issue: {issue['key']}")
        print(f"Summary: {fields['summary']}")
        print(f"Status: {fields['status']['name']}")
        print(f"Type: {fields['issuetype']['name']}")
        print(f"Description: {get_description_text(fields.get('description'))}")
        print(f"URL: https://{client.domain}/browse/{issue['key']}")
        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_transition(args):
    """Transition an issue to a new status."""
    if not is_configured():
        print("ERROR: Jira not configured.")
        return 1

    try:
        client = JiraClient()
        client.transition_issue(args.issue_key, args.status)
        print(f"Transitioned {args.issue_key} to {args.status}")
        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def cmd_add_comment(args):
    """Add a comment to an issue."""
    if not is_configured():
        print("ERROR: Jira not configured.")
        return 1

    try:
        client = JiraClient()
        client.add_comment(args.issue_key, args.comment)
        print(f"Comment added to {args.issue_key}")
        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Jira client for the implement-sprint skill",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # status command
    status_parser = subparsers.add_parser("status", help="Show config status and sprint issues")
    status_parser.set_defaults(func=cmd_status)

    # get-issue command
    get_issue_parser = subparsers.add_parser("get-issue", help="Get issue details")
    get_issue_parser.add_argument("issue_key", help="Issue key (e.g., DEMO-1)")
    get_issue_parser.set_defaults(func=cmd_get_issue)

    # transition command
    transition_parser = subparsers.add_parser("transition", help="Transition issue to new status")
    transition_parser.add_argument("issue_key", help="Issue key (e.g., DEMO-1)")
    transition_parser.add_argument("status", help="Target status (e.g., 'In Progress', 'Done')")
    transition_parser.set_defaults(func=cmd_transition)

    # add-comment command
    comment_parser = subparsers.add_parser("add-comment", help="Add comment to issue")
    comment_parser.add_argument("issue_key", help="Issue key (e.g., DEMO-1)")
    comment_parser.add_argument("comment", help="Comment text")
    comment_parser.set_defaults(func=cmd_add_comment)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
