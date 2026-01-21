# Claude Code Plugin Development Guide

This document captures knowledge about developing, maintaining, and deploying Claude Code plugins.

## Table of Contents

- [Plugin Structure](#plugin-structure)
- [Single Plugin vs Marketplace](#single-plugin-vs-marketplace)
- [Development Workflow](#development-workflow)
- [Configuration Files](#configuration-files)
- [Distribution](#distribution)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Plugin Structure

### Standard Directory Layout

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # Required: Plugin metadata
├── commands/                # Slash commands (optional)
│   └── my-command.md
├── agents/                  # Specialized agents (optional)
│   └── my-agent.md
├── skills/                  # Agent skills (optional)
│   └── my-skill/
│       └── SKILL.md
├── hooks/                   # Event handlers (optional)
│   └── hooks.json
├── .mcp.json               # MCP server config (optional)
├── .lsp.json               # LSP server config (optional)
├── scripts/                # Supporting scripts (optional)
├── README.md               # Plugin documentation
├── CHANGELOG.md            # Version history
└── LICENSE                 # License file
```

### Reserved Directory Names

These directories have special meaning to Claude Code:

| Directory | Purpose |
|-----------|---------|
| `.claude-plugin/` | Contains only `plugin.json` |
| `commands/` | Slash command definitions |
| `agents/` | Agent definitions |
| `skills/` | Skills with `SKILL.md` files |
| `hooks/` | Hook configurations |

### Critical Rule

**Only `plugin.json` belongs in `.claude-plugin/`** — all component directories must be at the plugin root level, not nested inside `.claude-plugin/`.

---

## Single Plugin vs Marketplace

### When You Need What

| Scenario | Files Needed |
|----------|-------------|
| Single standalone plugin | Only `plugin.json` |
| Multiple plugins in one repo | `marketplace.json` + `plugin.json` per plugin |
| Referencing external plugins | Only `marketplace.json` |

### Single Plugin Structure

For a single plugin, users install directly from the repo:

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── skills/
└── README.md
```

Installation: `/plugin install owner/my-plugin`

### Marketplace Structure

For multiple plugins, use a marketplace:

```
my-marketplace/
├── .claude-plugin/
│   └── marketplace.json      # Catalog only
├── plugins/
│   ├── plugin-a/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json   # Plugin A metadata
│   │   └── skills/
│   └── plugin-b/
│       ├── .claude-plugin/
│       │   └── plugin.json   # Plugin B metadata
│       └── skills/
└── README.md
```

Installation:
```bash
/plugin marketplace add owner/my-marketplace
/plugin install plugin-a@my-marketplace
```

### Avoiding Duplication

When using a marketplace:
- **`plugin.json`** is the source of truth for plugin metadata (version, author, etc.)
- **`marketplace.json`** only needs `name`, `source`, `description`, and `category`
- Don't duplicate version/author/keywords in both files

---

## Development Workflow

### Local Development with `--plugin-dir`

During development, use the `--plugin-dir` flag to load your plugin directly:

```bash
claude --plugin-dir ./path/to/your/plugin
```

This runs the plugin **from your local directory** (not from cache), allowing rapid iteration.

### Development Cycle

1. **Create** plugin structure with `plugin.json`
2. **Develop** skills, agents, hooks, etc.
3. **Test** with `claude --plugin-dir ./your-plugin`
4. **Iterate** — modify files and restart Claude Code
5. **Debug** with `claude --debug` if issues arise
6. **Package** for distribution when ready

### Testing Multiple Plugins

```bash
claude --plugin-dir ./plugin-one --plugin-dir ./plugin-two
```

### Important: File Location During Development

| Mode | Plugin Runs From | Files Created In |
|------|------------------|------------------|
| `--plugin-dir` (dev) | Your local repo | Your local repo |
| `/plugin install` (prod) | Cache directory | Cache directory |

This means `.gitignore` files **are needed** during development to protect credentials or generated files.

---

## Configuration Files

### plugin.json (Required)

Minimal:
```json
{
  "name": "my-plugin"
}
```

Complete:
```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "What this plugin does",
  "author": {
    "name": "Your Name",
    "email": "you@example.com",
    "url": "https://github.com/you"
  },
  "homepage": "https://github.com/you/my-plugin",
  "repository": "https://github.com/you/my-plugin",
  "license": "MIT",
  "keywords": ["keyword1", "keyword2"]
}
```

### marketplace.json

```json
{
  "name": "my-marketplace",
  "owner": {
    "name": "Your Name",
    "url": "https://github.com/you"
  },
  "metadata": {
    "description": "Collection of plugins"
  },
  "plugins": [
    {
      "name": "plugin-a",
      "source": "./plugins/plugin-a",
      "description": "What plugin A does",
      "category": "productivity"
    }
  ]
}
```

### Categories

Standard categories for marketplace plugins:
- `development` — Development tools and SDKs
- `productivity` — Workflow and productivity tools
- `learning` — Educational tools
- `security` — Security-focused tools

---

## Distribution

### Installation Paths

When users install plugins, they're copied to a cache:

```
~/.claude/plugins/cache/{marketplace-name}/{plugin-name}/{version}/
```

Example:
```
~/.claude/plugins/cache/pixelmind-plugins/jira-connector/1.1.4/
```

### Installation Scopes

| Scope | Settings File | In Git | Use Case |
|-------|---------------|--------|----------|
| `user` | `~/.claude/settings.json` | N/A | Personal, all projects |
| `project` | `.claude/settings.json` | Yes | Shared with team |
| `local` | `.claude/settings.local.json` | No | Personal, this project |

Scope is selected in the interactive wizard when installing:

```bash
/plugin install my-plugin
# → Wizard prompts to choose scope: user, project, or local
```

Or use the `/plugin` command and navigate to **Discover** → select plugin → choose scope.

### Distribution Methods

1. **GitHub** (recommended)
   ```bash
   /plugin marketplace add owner/repo
   ```

2. **Other Git hosts**
   ```bash
   /plugin marketplace add https://gitlab.com/company/plugins.git
   ```

3. **Local path** (for testing)
   ```bash
   /plugin marketplace add ./my-marketplace
   ```

### Submitting to Official Marketplace

Third-party plugins can be submitted to Anthropic's official marketplace:

1. Use the [plugin directory submission form](https://clau.de/plugin-directory-submission)
2. Must meet quality and security standards
3. External plugins are reviewed before approval

---

## Best Practices

### Structure

- Keep `plugin.json` minimal in marketplace entries (avoid duplication)
- Use semantic versioning: `MAJOR.MINOR.PATCH`
- Include `README.md`, `CHANGELOG.md`, and `LICENSE`

### Development

- Start simple with one skill, then expand
- Use `${CLAUDE_PLUGIN_ROOT}` for all internal paths
- Make hook scripts executable: `chmod +x script.sh`
- Use `.gitignore` to protect credentials during development

### Skills

- Use `SKILL.md` for skill definitions
- Keep CLI interfaces consistent (prefer subcommands over multiple scripts)
- Handle missing configuration gracefully with clear error messages

### Versioning

- Update version in `plugin.json` for each release
- If using marketplace, keep `marketplace.json` in sync (or omit version there)
- Document changes in `CHANGELOG.md`

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Plugin not loading | Invalid JSON | Use `claude plugin validate` |
| Commands not appearing | Wrong directory structure | Ensure `commands/` at root, not in `.claude-plugin/` |
| Hooks not firing | Script not executable | `chmod +x script.sh` |
| Path errors | Absolute paths used | Use `${CLAUDE_PLUGIN_ROOT}` |
| Conflicting manifests | Duplicate definitions | Remove duplicates from marketplace entry |

### Debugging

```bash
# See plugin loading details
claude --debug

# Validate plugin structure
claude plugin validate

# Check installed plugins
/plugin list
```

### Cache Issues

If changes aren't reflected after update:

```bash
/plugin update my-plugin
```

Or reinstall:
```bash
/plugin uninstall my-plugin
/plugin install my-plugin
```

---

## References

- [Plugins Reference](https://code.claude.com/docs/en/plugins-reference)
- [Plugin Marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
- [Discover Plugins](https://code.claude.com/docs/en/discover-plugins)
- [Official Plugin Repository](https://github.com/anthropics/claude-code/tree/main/plugins)
- [Official Plugin Directory](https://github.com/anthropics/claude-plugins-official)
