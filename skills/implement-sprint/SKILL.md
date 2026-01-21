---
name: implement-sprint
description: Connect to Jira, get active sprint issues, and implement them one by one
disable-model-invocation: true
---

# Implement Active Sprint Issues

You are implementing issues from the active Jira sprint.

## IMPORTANT: Normal Operation Rules

1. **Only work on issues in an ALREADY ACTIVE sprint** - Do not create sprints or start sprints
2. **NEVER close the sprint** - Sprint management is done by the team, not by this skill
3. **If no active sprint exists** - Inform the user and stop. Do not create one.

The skill's job is to implement issues, not manage sprint lifecycle.

## Step 1: Environment Setup

First, check if the plugin environment is set up. Run this command:

```bash
if [ ! -d "${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/venv" ]; then
  echo "Setting up plugin environment..."
  python3 -m venv ${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/venv
  ${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/venv/bin/pip install requests
  echo "Environment ready!"
else
  echo "Environment already set up."
fi
```

## Step 2: Check Configuration

Check if Jira is configured:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/venv/bin/python ${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/sprint_status.py
```

### If "CREDENTIALS_MISSING"

Ask the user for credentials (one-time setup, stored globally):
1. **Jira Domain** - e.g., `yourcompany.atlassian.net`
2. **Email** - Their Atlassian account email
3. **API Token** - From https://id.atlassian.com/manage-profile/security/api-tokens

Save credentials to plugin config:
```bash
cat > ${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/config.json << 'EOF'
{
  "jira_domain": "DOMAIN_HERE",
  "email": "EMAIL_HERE",
  "api_token": "TOKEN_HERE"
}
EOF
```

### If "PROJECT_NOT_CONFIGURED"

Ask the user for the Jira project key for this codebase (e.g., `DEMO`, `PROJ`).

Save project key to `.jira_config.json` in the project root:
```bash
cat > .jira_config.json << 'EOF'
{
  "project_key": "PROJECT_KEY_HERE"
}
EOF
```

This allows different projects to connect to different Jira projects while sharing the same credentials.

## Step 3: Get Sprint Issues

Once configured, get the active sprint issues:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/venv/bin/python ${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/sprint_status.py
```

### If "No active sprint found"

**STOP.** Inform the user that there is no active sprint and they need to start one in Jira before running this skill. Do NOT create or start a sprint (unless in test mode).

### If all issues are "Done"

Inform the user that all issues in the sprint are already complete. Do NOT close the sprint.

## Workflow

For each issue in "To Do" status:

### 1. Start Work
- Read the issue details:
```bash
${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/venv/bin/python ${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/get_issue.py ISSUE_KEY
```
- Transition to "In Progress":
```bash
${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/venv/bin/python -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint')
from jira_client import JiraClient
client = JiraClient()
client.transition_issue('ISSUE_KEY', 'In Progress')
print('Transitioned to In Progress')
"
```

### 2. Implement
- Analyze the issue summary and description
- Implement the required changes in the codebase
- Follow existing code patterns and conventions

### 3. Test
- Write tests if needed
- Run existing tests to ensure nothing is broken
- Verify the implementation works as expected
- **Document what you tested and how**

### 4. Add Comment with Test Results

**IMPORTANT: Never overwrite the issue title or description. Always use comments to document implementation and test results.**

Add a comment documenting:
- What was implemented (files created/modified, functions added, etc.)
- Issues encountered and how they were resolved (if any)
- Test procedure with **runnable commands** that can be repeated deterministically
- Test result (PASSED or FAILED with details)

```bash
${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/venv/bin/python -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint')
from jira_client import JiraClient
client = JiraClient()
client.add_comment('ISSUE_KEY', '''## Implementation
- [Files created/modified]
- [What was done]

## Issues Encountered
- [Any problems hit during implementation and how they were solved]
- [Or \"None\" if no issues]

## Test Procedure
Run the following commands to verify:
\`\`\`bash
[actual runnable command 1]
[actual runnable command 2]
\`\`\`

Expected output: [what should be seen]

## Test Result: PASSED/FAILED
- [Actual output observed]
- [Details]''')
print('Comment added')
"
```

### 5. Complete
```bash
${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/venv/bin/python -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint')
from jira_client import JiraClient
client = JiraClient()
client.transition_issue('ISSUE_KEY', 'Done')
print('Transitioned to Done')
"
```

### 6. Repeat
Move to the next "To Do" issue and continue until all issues are complete.

## Notes
- Replace `ISSUE_KEY` with the actual issue key (e.g., DEMO-11)
- Always test changes before marking as Done
- **Never overwrite the issue title or description** - use `add_comment()` instead
- **Test procedures must be runnable** - include actual commands that can be copy-pasted to repeat the test
- **Document any issues encountered** - even if solved, this helps future debugging
- Always document test procedure and results as a comment before transitioning to Done
- **Never close the sprint** - this skill only implements issues, not manages sprints
- **Never create issues or sprints** during normal operation (only in test mode)

## Configuration Files
- **Plugin config** (`config.json` in plugin dir): Credentials (jira_domain, email, api_token) - gitignored
- **Project config** (`.jira_config.json` in project root): Project key only - can be committed to share with team

---

## Test Mode (ONLY when explicitly requested)

When the user specifically asks to "test the skill" or "run a full test cycle", you may perform the complete workflow:

1. Create a test issue
2. Create a new test sprint
3. Move the issue to the sprint
4. Start the sprint
5. Implement the issue
6. Add test results comment
7. Transition to Done
8. Close the sprint

**This is ONLY for testing the skill itself.** During normal operation:
- Do NOT create issues (issues come from the backlog)
- Do NOT create sprints (sprint planning is done by the team)
- Do NOT start sprints (sprint is already active)
- Do NOT close sprints (sprint closure is a team decision)

### Test Mode Helper Functions

Available in `jira_client.py` for test mode only:
- `create_issue(summary, issue_type, description)` - Create a new issue
- `create_sprint(name, board_id)` - Create a new sprint
- `move_issues_to_sprint(sprint_id, issue_keys)` - Move issues to a sprint
- `start_sprint(sprint_id, duration_days)` - Start a sprint
- `close_sprint(sprint_id)` - Close a sprint
