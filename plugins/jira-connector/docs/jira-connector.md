# jira-connector Plugin

Connect Claude Code to Jira for automated sprint implementation.

---

## What It Does

The `/implement-sprint` skill automates your sprint workflow:

1. Fetches issues from your active Jira sprint
2. For each "To Do" issue:
   - Reads the issue details
   - Transitions to "In Progress"
   - Implements the required changes
   - Tests the implementation
   - Documents results as a comment
   - Transitions to "Done"

**You focus on the code. Claude handles the Jira choreography.**

---

## Quick Start

### 1. Install

```bash
/plugin marketplace add PixelMindAB/Claude-Plugins
/plugin install jira-connector
```

### 2. Run

```bash
/implement-sprint
```

On first run, you'll be prompted to configure your Jira credentials.

That's it. Claude will fetch your sprint and start implementing.

---

## Configuration

### First-Time Setup

The skill prompts for configuration automatically. You'll need:

| Item | Example | Where to Get It |
|------|---------|-----------------|
| Jira Domain | `yourcompany.atlassian.net` | Your Jira URL |
| Email | `you@company.com` | Your Atlassian account |
| API Token | `ATATT3x...` | [Create one here](https://id.atlassian.com/manage-profile/security/api-tokens) |
| Project Key | `DEMO` | From your Jira project |

### How Configuration Works

Configuration is split into two levels:

```
Plugin credentials (shared across all projects)
└── config.json in plugin directory
    ├── jira_domain
    ├── email
    └── api_token

Project key (per-project)
└── .jira_config.json in project root
    └── project_key
```

**Why two files?**
- Credentials are personal — stored once, used everywhere
- Project key varies — each codebase may connect to a different Jira project
- Teams can commit `.jira_config.json` to share the project key

### Manual Configuration

If you prefer to configure manually:

**Plugin credentials** (one-time):
```bash
cat > ${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/config.json << 'EOF'
{
  "jira_domain": "yourcompany.atlassian.net",
  "email": "you@company.com",
  "api_token": "your-api-token"
}
EOF
```

**Project key** (per-project):
```bash
cat > .jira_config.json << 'EOF'
{
  "project_key": "DEMO"
}
EOF
```

---

## Usage

### Basic Workflow

```bash
/implement-sprint
```

The skill will:
1. Check configuration
2. Fetch active sprint issues
3. Implement each "To Do" issue
4. Document results and transition to "Done"

### What Gets Documented

For each issue, a comment is added with:

- **Implementation** — Files created/modified, what was changed
- **Issues Encountered** — Problems and how they were resolved
- **Test Procedure** — Runnable commands to verify the implementation
- **Test Result** — PASSED or FAILED with details

### Important Behaviors

| Rule | Reason |
|------|--------|
| Never overwrites issue descriptions | Descriptions are requirements; results go in comments |
| Never closes sprints | Sprint lifecycle is a team decision |
| Never creates issues or sprints | Issues come from backlog; sprints from planning |
| Stops if no active sprint | You must start the sprint in Jira first |

---

## CLI Reference

The skill uses a single CLI with subcommands:

```bash
python jira_client.py <command> [arguments]
```

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `status` | Check config and list sprint issues | `python jira_client.py status` |
| `get-issue` | Get issue details | `python jira_client.py get-issue DEMO-1` |
| `transition` | Change issue status | `python jira_client.py transition DEMO-1 "In Progress"` |
| `add-comment` | Add comment to issue | `python jira_client.py add-comment DEMO-1 "Done"` |

### Status Output

```
$ python jira_client.py status

# If not configured:
CONFIG_STATUS: CREDENTIALS_MISSING (missing: jira_domain, email, api_token)

# If configured:
Sprint: Sprint 5
DEMO-11 [To Do]: Implement user login
DEMO-12 [In Progress]: Add password reset
DEMO-13 [Done]: Fix header alignment
```

---

## Architecture

### Design Decisions

We made specific choices to keep the plugin simple and maintainable:

#### Single CLI File

**Before:** Three separate scripts
```
├── jira_client.py      # API client
├── get_issue.py        # CLI wrapper
└── sprint_status.py    # CLI wrapper
```

**After:** One file with subcommands
```
└── jira_client.py      # API client + CLI
```

**Why:**
- Eliminates `sys.path` hacks for imports
- Single file to maintain
- Consistent invocation pattern
- Self-documenting with `--help`

#### Two-Level Configuration

**Why not one config file?**
- Credentials are sensitive and personal
- Project key can be shared with team
- Allows one credential setup for multiple projects

#### Comments Over Description Updates

**Why comments instead of updating the issue description?**
- Descriptions contain requirements (input)
- Comments contain implementation details (output)
- Preserves the original issue specification
- Creates an audit trail of implementation attempts

#### No Sprint Management

**Why doesn't the skill create/close sprints?**
- Sprint planning is a team activity
- Sprint closure requires team decision
- Separates implementation from project management
- Reduces risk of accidental sprint changes

### File Structure

```
plugins/jira-connector/
├── .claude-plugin/
│   └── plugin.json           # Plugin metadata
├── docs/
│   └── jira-connector.md     # This document
└── skills/
    └── implement-sprint/
        ├── SKILL.md          # Skill definition (main logic)
        ├── jira_client.py    # Jira API client + CLI (~560 lines)
        ├── requirements.txt  # Python dependencies
        └── .gitignore        # Protects config.json, venv/ during dev
```

### Dependencies

- **Python 3** — Standard installation
- **requests** — HTTP client for Jira API

Installed automatically via virtual environment on first run.

---

## Development

### Testing Locally

```bash
claude --plugin-dir ./plugins/jira-connector
```

This runs the plugin from your local directory, not from cache.

### Testing the CLI

```bash
cd plugins/jira-connector/skills/implement-sprint

# Create venv and install deps
python3 -m venv venv
venv/bin/pip install requests

# Test commands
venv/bin/python jira_client.py --help
venv/bin/python jira_client.py status
```

### Test Mode

For testing the full skill workflow (only when explicitly requested):

1. Creates a test issue
2. Creates a test sprint
3. Moves issue to sprint
4. Starts sprint
5. Implements issue
6. Transitions to Done
7. Closes sprint

**Never used during normal operation.**

---

## Troubleshooting

### "CREDENTIALS_MISSING"

Credentials not configured. Create `config.json`:

```bash
cat > ${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/config.json << 'EOF'
{
  "jira_domain": "yourcompany.atlassian.net",
  "email": "you@company.com",
  "api_token": "your-token"
}
EOF
```

### "PROJECT_NOT_CONFIGURED"

Project key not set. Create `.jira_config.json` in your project root:

```bash
echo '{"project_key": "DEMO"}' > .jira_config.json
```

### "No active sprint found"

No sprint is currently active in Jira. Start a sprint in Jira first, then run the skill again.

### "Cannot transition to 'X'"

The issue's current status doesn't allow that transition. Check:
- Issue's current status in Jira
- Your project's workflow configuration
- Available transitions for that status

### API Token Issues

- Tokens expire — regenerate at [Atlassian API tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
- Use the token value, not the token name
- Ensure no extra whitespace in config.json

---

## Version History

See [CHANGELOG.md](../../../CHANGELOG.md) for full version history.

### Current: 1.2.0

- Consolidated CLI into single file with subcommands
- Restructured repository for marketplace format
- Added comprehensive documentation
- Improved comment template format
- Two-level configuration (credentials + project key)
