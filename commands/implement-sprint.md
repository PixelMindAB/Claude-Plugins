---
name: implement-sprint
description: Automate Jira sprint implementation - fetches issues and implements them with status transitions
argument-hint: ""
---

# Implement Active Sprint Issues

Automate implementing Jira sprint issues. This command will guide you through setup and then implement each issue.

## Setup (first time only)

1. **Create venv** (if not exists):
```bash
if [ ! -d "${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/venv" ]; then
  python3 -m venv ${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/venv
  ${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/venv/bin/pip install requests
fi
```

2. **Check config**:
```bash
${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/venv/bin/python ${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/sprint_status.py
```

If NOT_CONFIGURED, ask user for: Jira Domain, Project Key, Email, API Token, then save to `${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/config.json`

## Get Sprint Issues

```bash
${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/venv/bin/python ${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/sprint_status.py
```

## For Each "To Do" Issue

1. **Get details**: `${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/venv/bin/python ${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/get_issue.py ISSUE_KEY`

2. **Transition to In Progress**:
```bash
${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/venv/bin/python -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint')
from jira_client import JiraClient
JiraClient().transition_issue('ISSUE_KEY', 'In Progress')
"
```

3. **Implement** the issue in the codebase

4. **Test** the implementation

5. **Add comment** with implementation details and test results (never overwrite description):
```bash
${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/venv/bin/python -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint')
from jira_client import JiraClient
JiraClient().add_comment('ISSUE_KEY', '''## Implementation
- Files modified: ...

## Test Procedure
\`\`\`bash
[runnable test commands]
\`\`\`

## Result: PASSED/FAILED
''')
"
```

6. **Transition to Done**:
```bash
${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint/venv/bin/python -c "
import sys; sys.path.insert(0, '${CLAUDE_PLUGIN_ROOT}/skills/implement-sprint')
from jira_client import JiraClient
JiraClient().transition_issue('ISSUE_KEY', 'Done')
"
```

7. **Repeat** for next issue
