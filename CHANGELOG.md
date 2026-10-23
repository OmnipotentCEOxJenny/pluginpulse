# Changelog

## 1.0.7 (2026-10-23)
- Search keywords: 33 to 40 (added GithubForks, MarketplaceSnapshot, ReadOnly, StarHistory, ReleaseTracker, RegistryWatch, PublicData), per Rob's keyword rules.
- Local tests re-run and passed. Not tested in-app. Not submitted to the marketplace.

## 1.0.6 (2026-10-22)
- `scripts/repos.txt`: TruthTrace was renamed TruthSweep; now tracks OmnipotentCEOxJenny/truthsweep. Dated example outputs left as recorded.

## 1.0.5 (2026-10-22)
- Fix: in the Rising list, a repo missing from the oldest snapshot printed "+None stars". It now says "no baseline ... growth not ranked", and growth is printed with its sign (e.g. +3, -1).
- `scripts/repos.txt` now tracks all 8 Omnipotent plugins (adds inplug-plugin and lingolink): 10 repos, 20 of the 50 budgeted GitHub requests.
- README now matches the code: Rising ranks only when the oldest and newest snapshots are at least 7 days apart (8 daily snapshots).

## 1.0.4 (2026-10-22)
- Registry snapshot: if a later page errors (after one polite retry on a 5xx), the pages already read are kept and flagged `"partial": true` with the error, instead of dropping the whole registry section. The digest labels such data PARTIAL.
- `.gitignore` also ignores Python cache folders.

## 1.0.3 (2026-10-21)
- Added `tests/check_frontmatter.py`: a strict YAML front-matter check (PyYAML `safe_load`) for every SKILL.md and rules .mdc file, plus a plugin.json JSON check. Run `python3 tests/check_frontmatter.py` from the repo root; it catches the unquoted-colon bug fixed in PluginPulse 1.0.2.
- `.gitignore` now ignores `data/` (local daily snapshots are not committed).
- No behavior changes to skills or rules.

## 1.0.2 (2026-10-21)
- Fix: the movers-and-shakers skill description had an unquoted ": " that strict YAML parsers reject, so the front matter could fail to load. The description is now quoted; wording unchanged.

## 1.0.1 (2026-10-20)
- README follows the Omnipotent template: title, description, logo, content, Rob Domaine's four pillars in exact wording, and a closing "Honest assessment: what this plugin cannot do" section (no install/rating data, rising needs 7+ days, partial registry reads, page-layout dependence, tags vs GitHub Releases, GitHub-only star growth, unreviewed translations, compliance).
- New TRANSLATIONS.md: title, description and honest assessment with the specific limits in 23 languages (adds Tagalog / Filipino), machine-made and not native-reviewed.
- Skills and rule: answer in the user's language; keep commands, file names and status labels unchanged.

## 1.0.0 (2026-10-20)
- First release: `scripts/pluginpulse.py` (snapshot and digest commands; MCP Registry API with paging and updated_since, GitHub REST unauthenticated within a 50-request budget, public marketplace page read once with robots.txt check and Retry-After handling), pluginpulse-snapshot and movers-and-shakers skills, pillars rule, real example digest, logo, translated summaries in 22 languages (machine-made, not native-reviewed).
