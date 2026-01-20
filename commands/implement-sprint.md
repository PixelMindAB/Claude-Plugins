---
name: implement-sprint
description: Connect to Jira, get active sprint issues, and implement them one by one
disable-model-invocation: true
---

# Implement Active Sprint Issues

You are implementing issues from the active Jira sprint.

## First-Time Setup

Before using this command, the user needs a `jira-config.json` file in their project root:

```json
{
  "jira_domain": "yourcompany.atlassian.net",
  "project_key": "DEMO",
  "email": "your-email@example.com",
  "api_token": "your-api-token"
}
```

To get an API token: https://id.atlassian.com/manage-profile/security/api-tokens

If `jira-config.json` doesn't exist, ask the user for these 4 values and create it.

## Check Sprint Status

Run this to get active sprint issues:

```bash
python3 -c "
import json, requests
from requests.auth import HTTPBasicAuth

with open('jira-config.json') as f:
    cfg = json.load(f)

auth = HTTPBasicAuth(cfg['email'], cfg['api_token'])
headers = {'Accept': 'application/json'}
base = f\"https://{cfg['jira_domain']}\"

# Get board
r = requests.get(f\"{base}/rest/agile/1.0/board\", headers=headers, auth=auth, params={'projectKeyOrId': cfg['project_key']})
boards = r.json().get('values', [])
if not boards:
    print('No board found')
    exit()
board_id = boards[0]['id']

# Get active sprint
r = requests.get(f\"{base}/rest/agile/1.0/board/{board_id}/sprint\", headers=headers, auth=auth, params={'state': 'active'})
sprints = r.json().get('values', [])
if not sprints:
    print('No active sprint')
    exit()
sprint = sprints[0]
print(f\"Sprint: {sprint['name']}\")

# Get issues
r = requests.get(f\"{base}/rest/agile/1.0/sprint/{sprint['id']}/issue\", headers=headers, auth=auth, params={'fields': 'summary,status'})
for issue in r.json().get('issues', []):
    status = issue['fields']['status']['name']
    print(f\"{issue['key']} [{status}]: {issue['fields']['summary']}\")
"
```

## Workflow

For each issue in "To Do" status:

### 1. Get Issue Details

```bash
python3 -c "
import json, requests
from requests.auth import HTTPBasicAuth

ISSUE_KEY = 'DEMO-1'  # Replace with actual issue key

with open('jira-config.json') as f:
    cfg = json.load(f)

auth = HTTPBasicAuth(cfg['email'], cfg['api_token'])
r = requests.get(f\"https://{cfg['jira_domain']}/rest/api/3/issue/{ISSUE_KEY}\", auth=auth)
issue = r.json()
fields = issue['fields']
print(f\"Issue: {issue['key']}\")
print(f\"Summary: {fields['summary']}\")
print(f\"Status: {fields['status']['name']}\")

desc = fields.get('description')
if desc:
    for block in desc.get('content', []):
        if block.get('type') == 'paragraph':
            for item in block.get('content', []):
                if item.get('type') == 'text':
                    print(f\"Description: {item.get('text')}\")
"
```

### 2. Transition to In Progress

```bash
python3 -c "
import json, requests
from requests.auth import HTTPBasicAuth

ISSUE_KEY = 'DEMO-1'  # Replace with actual issue key

with open('jira-config.json') as f:
    cfg = json.load(f)

auth = HTTPBasicAuth(cfg['email'], cfg['api_token'])
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
base = f\"https://{cfg['jira_domain']}/rest/api/3\"

# Get transitions
r = requests.get(f\"{base}/issue/{ISSUE_KEY}/transitions\", auth=auth, headers=headers)
for t in r.json().get('transitions', []):
    if t['to']['name'].lower() == 'in progress':
        requests.post(f\"{base}/issue/{ISSUE_KEY}/transitions\", auth=auth, headers=headers, json={'transition': {'id': t['id']}})
        print('Transitioned to In Progress')
        break
"
```

### 3. Implement the Issue

- Read the issue summary and description
- Implement the required changes in the codebase
- Follow existing code patterns

### 4. Test the Implementation

- Run relevant tests
- Verify the changes work correctly

### 5. Update Issue with Results

```bash
python3 -c "
import json, requests
from requests.auth import HTTPBasicAuth

ISSUE_KEY = 'DEMO-1'  # Replace with actual issue key
DESCRIPTION = 'Implementation: [describe what was done] | Testing: [how it was tested] | Result: PASSED'

with open('jira-config.json') as f:
    cfg = json.load(f)

auth = HTTPBasicAuth(cfg['email'], cfg['api_token'])
headers = {'Content-Type': 'application/json'}

payload = {'fields': {'description': {'type': 'doc', 'version': 1, 'content': [{'type': 'paragraph', 'content': [{'type': 'text', 'text': DESCRIPTION}]}]}}}
requests.put(f\"https://{cfg['jira_domain']}/rest/api/3/issue/{ISSUE_KEY}\", auth=auth, headers=headers, json=payload)
print('Issue updated')
"
```

### 6. Transition to Done

```bash
python3 -c "
import json, requests
from requests.auth import HTTPBasicAuth

ISSUE_KEY = 'DEMO-1'  # Replace with actual issue key

with open('jira-config.json') as f:
    cfg = json.load(f)

auth = HTTPBasicAuth(cfg['email'], cfg['api_token'])
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
base = f\"https://{cfg['jira_domain']}/rest/api/3\"

r = requests.get(f\"{base}/issue/{ISSUE_KEY}/transitions\", auth=auth, headers=headers)
for t in r.json().get('transitions', []):
    if t['to']['name'].lower() == 'done':
        requests.post(f\"{base}/issue/{ISSUE_KEY}/transitions\", auth=auth, headers=headers, json={'transition': {'id': t['id']}})
        print('Transitioned to Done')
        break
"
```

### 7. Repeat

Move to the next "To Do" issue and continue until all issues are complete.

## Notes

- Replace `ISSUE_KEY = 'DEMO-1'` with the actual issue key in each command
- The `jira-config.json` file should be added to `.gitignore` to protect credentials
- Always test changes before marking as Done
