---
name: pluginpulse-snapshot
description: Take a read-only daily snapshot of public plugin data (official MCP Registry, GitHub stars/forks/releases for tracked repos, public marketplace page). Use when a user asks to track plugins, MCP servers or repos over time, or to "take today's PluginPulse snapshot".
---

# PluginPulse snapshot

Follow `rules/scope.mdc`. Required. Answer in the user's language; keep commands, file names and status labels unchanged.

## Workflow
1. **Set up (free, once):** `python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt` (only `requests==2.32.3`).
2. **Choose repos:** edit `scripts/repos.txt` (one public `owner/name` per line). Keep it under 25 repos: each costs 2 of the 50 GitHub requests the script budgets per run.
3. **Run once a day:** `.venv/bin/python scripts/pluginpulse.py snapshot --contact mailto:YOU@example.com --out pluginpulse-data`
   - `--contact` is required so site owners can reach the operator.
   - `--skip marketplace` (or `registry`, `github`) to leave a source out.
4. **Check the result:** open `pluginpulse-data/snapshot-YYYY-MM-DD.json`. Each source has `captured_et`; any `error` must be reported as "not captured", never as zero. `request_log` lists every request and its status code.
5. **Tell the user** what was captured, what failed and why, and when to run the next snapshot. Never claim installs or ratings.
