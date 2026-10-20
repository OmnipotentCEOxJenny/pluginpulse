# PluginPulse

PluginPulse is a free, read-only tracker of **public** plugin data. Once a day it takes a snapshot of the official MCP Registry, GitHub stars, forks and releases for the repos you choose, and the public marketplace page at https://x.ai/bot/marketplace. Once a week it writes a **Movers & Shakers** digest: what is new, what was updated, what is rising by star growth, and how many listings each category has. Every number names its source and its capture time in Eastern Time (ET). It makes no install or rating claims.

![PluginPulse logo](assets/logo.png)

## Project status: done, pending, uncertain
**Done**
- 2026-10-20: v1.0.1 applies the Omnipotent README template: honest-assessment section, exact pillars, 23-language TRANSLATIONS.md.
- 2026-10-20: v1.0.0 built and tested with live data: a real snapshot (MCP Registry, 8 GitHub repos, the marketplace page; 38 requests, all HTTP 200 except `releases/latest` 404 for repos that have tags but no GitHub Release, reported as "no GitHub Release"; on day one the registry read hit the 20-page cap and is labeled partial), a real digest, manifest valid JSON, skill frontmatter valid, every file link resolves. Example in `examples/`.
- Publisher terms read (Cursor Marketplace Publisher Terms, last updated May 6, 2026): no conflict found. PluginPulse is free, MIT-licensed, collects only what its stated function needs and makes no unsubstantiated claims.

**Pending**
- Marketplace submission: not submitted yet.
- Translated summaries in TRANSLATIONS.md are machine-made and not reviewed by native speakers. Corrections welcome through an issue.
- "Rising" needs 7 or more days of daily snapshots before it ranks anything.

**Uncertain**
- The marketplace page is read from data embedded in the public page, not a documented API. If its layout changes, PluginPulse reports "page layout changed" rather than guessing.
- The marketplace currently shows `installCount: 0` for every listing, so installs cannot be measured. PluginPulse does not rank by installs.
- How listings work on the Grok Bot and Grok side: not described in the publisher terms.

## Quick start
1. `python3 -m venv .venv && .venv/bin/pip install -r scripts/requirements.txt`
2. Daily: `.venv/bin/python scripts/pluginpulse.py snapshot --contact mailto:you@example.com`
3. Weekly: `.venv/bin/python scripts/pluginpulse.py digest`
4. Or just ask: "Take today's PluginPulse snapshot" or "Who are this week's movers and shakers?"

## Installation
Install from this repository: https://github.com/OmnipotentCEOxJenny/pluginpulse (Cursor plugin format: `.cursor-plugin/plugin.json`, `skills/`, `rules/`). Python 3.10+ and one pinned free dependency (`requests==2.32.3`). No API keys, no accounts, no paid services.

## Data sources and limits
| Source | How | Limits honored |
|---|---|---|
| MCP Registry `https://registry.modelcontextprotocol.io/v0/servers` | Official public API, paged (`limit=100`, `cursor`), `version=latest`, `updated_since` (default 8 days) | 1 request per second, max 20 pages per run (marked partial if reached) |
| GitHub REST API | Unauthenticated `repos/{owner}/{repo}` and `releases/latest` | Budget of 50 requests per run, under GitHub's 60 per hour; stops on 403 |
| https://x.ai/bot/marketplace | robots.txt checked first (it allows `/bot/`), one page request | User-Agent `PluginPulse/1.0.0 (+contact)`, Retry-After honored on 429/503, stops if asked to wait over 10 minutes |

Only minimal marketplace fields are kept (id, name, creator handle, categories, updated date). Descriptions and images are not copied, and the digest links back to the listings instead of republishing them.

## Testing
1. Run the snapshot command above with your contact. Expected: `snapshot-YYYY-MM-DD.json` with `captured_et` for each source and a `request_log`.
2. Run the digest command. Expected: `digest-YYYY-MM-DD.md` with registry new/updated counts, repo stars and releases, "Rising: not enough history yet" on day one, and marketplace category counts with a link back.
3. Compare with `examples/digest-2026-10-20.md`.

## Privacy
PluginPulse runs on your machine and sends nothing anywhere except the read requests listed above. It collects no data about its users.

## Credits
- Inventor and publisher: Rob Domaine / Omnipotent Media LLC
- Builder: Jenny Echo

## Rob Domaine's four pillars
1. Trustworthy, honest, real data, truthful: never invent; anything unchecked is marked UNVERIFIED.
2. Use only legitimate means: legitimate, proven sources and methods; unreliable sources rejected.
3. Double-check everything: every finding is confirmed by two independent checks, and the report shows both.
4. Stay within the law and rules always: local, county, state, federal and platform rules.

## Components
- `scripts/pluginpulse.py`: snapshot and digest commands.
- `scripts/repos.txt`: GitHub repos to track.
- `scripts/requirements.txt`: pinned dependency.
- `skills/pluginpulse-snapshot`: taking and checking a daily snapshot.
- `skills/movers-and-shakers`: building and summarizing the weekly digest.
- `rules/pillars-and-scope.mdc`: the pillars and scope.
- `examples/digest-2026-10-20.md`: a real digest from the first test run.

## Languages
The AI answers in the user's language and keeps commands, file names and status labels unchanged. Title, description and honest-assessment summaries in 23 languages are in [TRANSLATIONS.md](TRANSLATIONS.md): es Español, fr Français, pt Português, de Deutsch, it Italiano, nl Nederlands, pl Polski, ru Русский, uk Українська, tr Türkçe, ar العربية, he עברית, fa فارسی, hi हिन्दी, bn বাংলা, ur اردو, zh 简体中文, ja 日本語, ko 한국어, id Bahasa Indonesia, vi Tiếng Việt, sw Kiswahili, tl Tagalog / Filipino. They are machine translations, not yet reviewed by native speakers; the English text is authoritative.

## License
MIT. See `LICENSE`.

## Honest assessment: what this plugin cannot do
Written to be fully transparent. If something here is wrong or out of date, please open an issue.

- No install or rating data: the public marketplace shows `installCount: 0` for every listing and no ratings, so PluginPulse never ranks or reports by installs or ratings.
- "Rising" needs 7 or more days of daily snapshots. Before that, the digest says so and lists current star counts for reference only.
- Registry reads can be partial: each run reads at most 20 pages of the MCP Registry, and when it hits the cap the snapshot and digest are labeled partial.
- The marketplace reader depends on the public page's current layout (data embedded in the page, not a documented API). If the layout changes, it reports "page layout changed" instead of guessing.
- Release data comes from GitHub Releases. Repos that publish only git tags (including Rob's own plugins) show "no GitHub Release", even when tagged versions exist.
- Star growth covers only plugins with a public GitHub repository. Plugins without one are listed but not ranked.
- GitHub requests are unauthenticated and capped at 50 per run (GitHub allows 60 per hour), so large watch lists are spread across runs.
- Marketplace: not submitted yet; it is not a listed plugin.
- Translations: the 23 translated summaries in [TRANSLATIONS.md](TRANSLATIONS.md) are machine-made and have not been reviewed by native speakers. The English text is authoritative.
- It is not legal advice and cannot guarantee that any particular use is lawful; you remain responsible for how you use it.
- Rules and compliance: it is built to follow all local, county, state and federal laws and every platform's rules. It uses no paid services, never bypasses logins, paywalls, CAPTCHAs or access controls, and never claims a feature it does not have.
