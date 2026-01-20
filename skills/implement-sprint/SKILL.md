---
name: implement-sprint
description: Connect to Jira, get active sprint issues, and implement them one by one
disable-model-invocation: true
---

# Implement Active Sprint Issues

You are implementing issues from the active Jira sprint.

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

If it shows "NOT_CONFIGURED" or "INCOMPLETE", ask the user for:
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

## Step 3: Get Sprint Issues

Once configured, get the active sprint issues:

```bash
${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/venv/bin/python ${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/sprint_status.py
```

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

### 4. Update Issue with Results
```bash
${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/venv/bin/python -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint')
from jira_client import JiraClient
client = JiraClient()
client.update_issue('ISSUE_KEY', description='Implementation: ... | Testing: ... | Result: PASSED')
print('Issue updated')
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
- The config.json file is gitignored to protect credentials
