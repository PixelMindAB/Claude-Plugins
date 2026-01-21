# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Claude Code plugin marketplace by PixelMind AB. It contains the `jira-connector` plugin with the `/implement-sprint` skill for automating Jira sprint implementation.

## Architecture

**Marketplace structure** (multiple plugins in one repo):
- `.claude-plugin/marketplace.json` — Catalog listing all plugins
- `plugins/<plugin-name>/` — Each plugin has its own directory with `.claude-plugin/plugin.json`

**Key rule**: `plugin.json` is the source of truth for plugin metadata. `marketplace.json` should only contain `name`, `source`, `description`, `category` — no duplication of version/author.

## Development Commands

### Test plugin locally
```bash
claude --plugin-dir ./plugins/jira-connector
```

### Test CLI directly
```bash
cd plugins/jira-connector/skills/implement-sprint
python3 -m venv venv
venv/bin/pip install requests
venv/bin/python jira_client.py --help
venv/bin/python jira_client.py status
```

### Debug plugin loading
```bash
claude --debug
```

## jira-connector Plugin

The skill uses a single CLI (`jira_client.py`) with subcommands: `status`, `get-issue`, `transition`, `add-comment`.

**Two-level configuration**:
- Plugin credentials (`config.json` in skill dir) — jira_domain, email, api_token
- Project key (`.jira_config.json` in project root) — project_key

**Design decisions**:
- Comments over description updates (preserve requirements, audit trail)
- No sprint management (implementation only, not lifecycle)
- Single CLI file (eliminated sys.path hacks from separate scripts)

## Documentation

- `docs/plugin-development.md` — General plugin development guide
- `plugins/jira-connector/docs/jira-connector.md` — Plugin-specific documentation
