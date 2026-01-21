# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.4] - 2025-01-21

### Improved
- Comment template now uses clearer, more concrete format with file locations and structured test results

## [1.1.3] - 2025-01-21

### Changed
- Command wrapper now references SKILL.md instead of duplicating logic (single source of truth)

## [1.1.2] - 2025-01-21

### Fixed
- Update command wrapper to use add_comment() instead of update_issue() - was missed in 1.1.1

## [1.1.1] - 2025-01-21

### Changed
- Use comments instead of overwriting issue description when documenting implementation results

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
