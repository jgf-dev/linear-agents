# linear-agents

Linear issue sync repo for agent-automation project related repos.

## Overview

This repository contains a GitHub Actions workflow that automatically syncs issues from [Linear](https://linear.app) into GitHub Issues. It is scoped to the **agent-automation** project and runs every 30 minutes.

Each synced Linear issue becomes a GitHub Issue with:
- A `linear` label
- A `linear-id:<IDENTIFIER>` label (e.g. `linear-id:ENG-42`) used to deduplicate updates
- A `linear:<state>` label reflecting the current Linear workflow state
- A `priority:<level>` label when a priority is set
- Open/closed state mirrored from Linear (completed or cancelled → closed)

## Setup

### Secrets

| Secret | Description |
|--------|-------------|
| `LINEAR_API_KEY` | Linear personal API key (Settings → API → Personal API keys) |

### Variables (optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `LINEAR_TEAM_KEY` | _(none)_ | Linear team key to filter issues (e.g. `ENG`) |
| `LINEAR_PROJECT_NAME` | `agent-automation` | Linear project name substring to filter issues |

### Running manually

Trigger the **Linear Issue Sync** workflow from the **Actions** tab at any time using the `workflow_dispatch` event.

## Agent-automation related repos

The following repositories in this organisation are covered by the agent-automation project:

- [genai-auto-tasks](https://github.com/jgf-dev/genai-auto-tasks)
- [adk-agent-eval](https://github.com/jgf-dev/adk-agent-eval)
- [agent-data](https://github.com/jgf-dev/agent-data)
- [linear-agents](https://github.com/jgf-dev/linear-agents) *(this repo)*
