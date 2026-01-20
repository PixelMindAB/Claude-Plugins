# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-01-20

### Changed
- Renamed plugin from `jira-sprint-automation` to `jira-connector`
- Plugin now serves as a container for Jira-related skills
- Skill command remains `/implement-sprint`

## [1.0.0] - 2025-01-20

### Added
- Initial release of jira-sprint-automation plugin
- Self-contained Jira client with config-based authentication
- `/implement-sprint` command for automating sprint implementation
- Automatic status transitions (To Do → In Progress → Done)
- Issue updates with implementation details and test results
- First-run setup flow for Jira credentials
