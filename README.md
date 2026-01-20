# Claude-Plugins

A collection of Claude Code plugins by PixelMind AB.

## Available Plugins

### jira-sprint-automation

Automate Jira sprint implementation with Claude Code. This plugin fetches active sprint issues and implements them one by one, transitioning statuses (To Do → In Progress → Done) and updating issues with implementation details and test results.

## Installation

### Method 1: Add as Marketplace (Recommended)

```bash
/plugin marketplace add PixelMindAB/Claude-Plugins
/plugin install jira-sprint-automation@PixelMindAB/Claude-Plugins
```

### Method 2: Manual Installation

1. Clone this repository
2. Copy the desired skill folder to your project's `.claude/skills/` directory

```bash
git clone https://github.com/PixelMindAB/Claude-Plugins.git
cp -r Claude-Plugins/skills/implement-sprint .claude/skills/
```

## Plugin: jira-sprint-automation

### Features

- Fetches active sprint issues from Jira
- Implements issues one by one
- Automatically transitions issue status (To Do → In Progress → Done)
- Updates issues with implementation details and test results
- Self-contained with its own Jira client

### Setup

1. Install dependencies:
   ```bash
   pip install requests
   ```

2. On first run, the skill will prompt you to configure:
   - **Jira Domain** - e.g., `yourcompany.atlassian.net`
   - **Project Key** - e.g., `DEMO`, `PROJ`
   - **Email** - Your Atlassian account email
   - **API Token** - From https://id.atlassian.com/manage-profile/security/api-tokens

3. Credentials are stored in `config.json` (gitignored)

### Usage

```bash
/implement-sprint
```

The command will:
1. Check configuration (prompt for setup if needed)
2. Fetch active sprint issues
3. For each "To Do" issue:
   - Read issue details
   - Transition to "In Progress"
   - Implement the required changes
   - Test the implementation
   - Update issue with results
   - Transition to "Done"

### File Structure

```
skills/implement-sprint/
├── SKILL.md              # Skill definition
├── jira_client.py        # Self-contained Jira API client
├── get_issue.py          # Get issue details
├── sprint_status.py      # Check sprint status
├── config.json.example   # Configuration template
├── requirements.txt      # Python dependencies
└── .gitignore            # Ignores config.json
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Author

[PixelMind AB](https://github.com/PixelMindAB)
