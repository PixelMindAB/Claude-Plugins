# Claude-Plugins

A collection of Claude Code plugins by PixelMind AB.

## Available Plugins

### jira-connector

Connect Claude Code to Jira for sprint automation and issue management.

**Included skills:**

- `/implement-sprint` - Automate sprint implementation

## Installation

### Step 1: Add Marketplace

```bash
/plugin marketplace add PixelMindAB/Claude-Plugins
```

### Step 2: Install Plugin

```bash
/plugin install jira-connector
```

### Installation Scopes

Choose where to install the plugin using the `--scope` flag:

```bash
# Global (default) - available in all your projects
/plugin install jira-connector

# Project - shared with team (committed to git)
/plugin install jira-connector --scope project

# Local - personal, this project only (not committed)
/plugin install jira-connector --scope local
```

| Scope | Settings File | In Git | Use Case |
|-------|---------------|--------|----------|
| `user` | `~/.claude/settings.json` | N/A | Personal, all projects |
| `project` | `.claude/settings.json` | Yes | Shared with team |
| `local` | `.claude/settings.local.json` | No | Personal, this project only |

**Recommendation:** Use `--scope project` for team projects. Each person's Jira credentials are stored separately in the skill's `config.json` (gitignored).

### Manual Installation

Alternatively, clone and copy:

```bash
git clone https://github.com/PixelMindAB/Claude-Plugins.git
cp -r Claude-Plugins/skills/implement-sprint .claude/skills/
```

## Plugin: jira-connector

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
   - **API Token** - From <https://id.atlassian.com/manage-profile/security/api-tokens>

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

```text
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
