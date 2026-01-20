---
name: implement-sprint
description: Connect to Jira, get active sprint issues, and implement them one by one
disable-model-invocation: true
---

# Implement Active Sprint Issues

You are implementing issues from the active Jira sprint. This skill is self-contained with its own Jira client.

## Dependencies

This skill requires the `requests` library. Install with:
```bash
pip install requests
```

## Configuration Check

Current config status:
!`python3 ${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/sprint_status.py 2>&1 | head -1`

## First-Time Setup

If the config status shows "NOT_CONFIGURED" or "INCOMPLETE", you need to help the user set up their Jira credentials.

Ask the user for:
1. **Jira Domain** - e.g., `yourcompany.atlassian.net`
2. **Project Key** - e.g., `DEMO`, `PROJ`
3. **Email** - Their Atlassian account email
4. **API Token** - From https://id.atlassian.com/manage-profile/security/api-tokens

Then save the config:
```bash
cat > ${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/config.json << 'EOF'
{
  "jira_domain": "DOMAIN_HERE",
  "project_key": "PROJECT_KEY_HERE",
  "email": "EMAIL_HERE",
  "api_token": "TOKEN_HERE"
}
EOF
```

After setup, verify by running:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/sprint_status.py
```

## Current Sprint Status

Active sprint issues:
!`python3 ${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/sprint_status.py 2>&1`

## Workflow

For each issue in "To Do" status:

### 1. Start Work
- Read the issue details:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/get_issue.py ISSUE_KEY
```
- Transition to "In Progress":
```bash
python3 -c "
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

### 4. Update Issue with Results
- Update the issue description with implementation details and test results:
```bash
python3 -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint')
from jira_client import JiraClient
client = JiraClient()
client.update_issue('ISSUE_KEY', description='Implementation: ... | Testing: ... | Result: PASSED')
print('Issue updated')
"
```

### 5. Complete
- Transition to "Done":
```bash
python3 -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint')
from jira_client import JiraClient
client = JiraClient()
client.transition_issue('ISSUE_KEY', 'Done')
print('Transitioned to Done')
"
```

### 6. Repeat
- Move to the next "To Do" issue
- Continue until all issues are done

## Important Notes
- Replace `ISSUE_KEY` with the actual issue key (e.g., DEMO-11)
- Always test changes before marking as Done
- If an issue cannot be implemented, leave a comment explaining why and skip it
- Ask for clarification if issue requirements are unclear
- The config.json file is gitignored to protect credentials
