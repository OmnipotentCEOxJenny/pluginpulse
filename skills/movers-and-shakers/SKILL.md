---
name: movers-and-shakers
description: 'Build the weekly "Movers & Shakers" digest from PluginPulse snapshots: new and updated MCP servers, tracked repos with stars and releases, rising by star growth (needs a 7-day snapshot span), and marketplace category counts. Use when a user asks what is new, trending or rising among plugins.'
---

# Movers & Shakers digest

Follow `rules/pillars-and-scope.mdc`. Required. Answer in the user's language; keep commands, file names and status labels unchanged.

## Workflow
1. Make sure at least one snapshot exists (skill `pluginpulse-snapshot`).
2. Run `.venv/bin/python scripts/pluginpulse.py digest --out pluginpulse-data [--days 7]`.
3. Open `pluginpulse-data/digest-YYYY-MM-DD.md` and check every number against the snapshot (pillar 3).
4. Summarize for the user:
   - **New** and **updated** MCP servers in the window (say if the registry read was partial).
   - **Tracked repos:** stars, forks, latest release, last push, each with source and capture time (ET).
   - **Rising:** only when snapshots span 7 or more days; otherwise say exactly how many days exist and that rising is not ready.
   - **Marketplace:** listing and category counts, recently updated listings, and a link back to https://x.ai/bot/marketplace. State that install counts show 0 and are not used.
5. Do not paste the full listing data or descriptions; link to the listings instead.
