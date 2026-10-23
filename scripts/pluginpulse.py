#!/usr/bin/env python3
"""PluginPulse (free, MIT): read-only daily snapshots of PUBLIC plugin data and a
weekly "Movers & Shakers" digest.

Sources (public only, no login, no API keys):
  1. Official MCP Registry API  https://registry.modelcontextprotocol.io/v0/servers (paged)
  2. GitHub REST API, unauthenticated (stars, forks, releases, updated dates), kept
     under the 60 requests/hour unauthenticated limit
  3. Public marketplace page https://x.ai/bot/marketplace (robots.txt allows /bot/);
     one request, identified with contact info, 429/503 honored

Usage:
  python pluginpulse.py snapshot --contact EMAIL_OR_URL [--out DIR] [--repos FILE]
                                 [--registry-pages N] [--skip SOURCE ...]
  python pluginpulse.py digest [--out DIR] [--days 7]

Tested with Python 3.13 and requests==2.32.3.
"""
import argparse, datetime as dt, glob, json, os, re, sys, time, urllib.robotparser
from collections import Counter
from zoneinfo import ZoneInfo
import requests

VERSION = "1.0.9"
ET = ZoneInfo("America/New_York")
REGISTRY = "https://registry.modelcontextprotocol.io/v0/servers"
MARKETPLACE = "https://x.ai/bot/marketplace"
GITHUB = "https://api.github.com"
GH_BUDGET = 50          # stay safely under GitHub's 60 unauthenticated requests/hour
MAX_RETRY_AFTER = 600


def now_et():
    return dt.datetime.now(ET).replace(microsecond=0)


def stamp(t):
    return t.strftime("%Y-%m-%d %H:%M %Z")


class Client:
    def __init__(self, contact, delay=1.0):
        self.s = requests.Session()
        self.s.headers["User-Agent"] = f"PluginPulse/{VERSION} (+{contact})"
        self.delay, self.last = delay, 0.0
        self.log = []

    def get(self, url, **kw):
        for attempt in range(3):
            wait = self.delay - (time.time() - self.last)
            if wait > 0:
                time.sleep(wait)
            r = self.s.get(url, timeout=30, **kw)
            self.last = time.time()
            self.log.append(f"{r.status_code} {url}")
            if r.status_code in (429, 503):
                ra = r.headers.get("Retry-After", "60")
                secs = int(ra) if ra.isdigit() else 60
                if secs > MAX_RETRY_AFTER:
                    raise RuntimeError(f"{url}: asked to wait {secs}s; stopping politely")
                time.sleep(secs)
                continue
            return r
        raise RuntimeError(f"{url}: still rate-limited after 3 tries; stopping")

    def allowed(self, url):
        p = requests.utils.urlparse(url)
        rp = urllib.robotparser.RobotFileParser()
        r = self.get(f"{p.scheme}://{p.netloc}/robots.txt")
        if r.status_code >= 500:
            return False
        rp.parse(r.text.splitlines() if r.status_code == 200 else [])
        return rp.can_fetch(self.s.headers["User-Agent"], url)


def snap_registry(c, pages, since_days):
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=since_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    servers, cursor, n = [], None, 0
    while n < pages:
        params = {"limit": 100, "version": "latest", "updated_since": since}
        if cursor:
            params["cursor"] = cursor
        try:
            r = c.get(REGISTRY, params=params)
            if r.status_code >= 500:  # one polite retry on a server error
                time.sleep(5)
                r = c.get(REGISTRY, params=params)
            r.raise_for_status()
            d = r.json()
        except Exception as e:
            if not n:
                raise  # nothing read yet: report the whole source as an error
            # keep the pages already read, flagged as partial
            return {"source": REGISTRY, "updated_since_utc": since, "pages_read": n, "complete": False,
                    "partial": True, "error": f"page {n + 1}: {e}", "servers": servers}
        for item in d.get("servers", []):
            s, meta = item.get("server", {}), item.get("_meta", {}).get(
                "io.modelcontextprotocol.registry/official", {})
            if not meta.get("isLatest", True):
                continue
            servers.append({
                "name": s.get("name"), "title": s.get("title"), "version": s.get("version"),
                "repository": (s.get("repository") or {}).get("url"),
                "status": meta.get("status"), "publishedAt": meta.get("publishedAt"),
                "updatedAt": meta.get("updatedAt")})
        n += 1
        cursor = d.get("metadata", {}).get("nextCursor")
        if not cursor:
            break
    return {"source": REGISTRY, "updated_since_utc": since, "pages_read": n, "complete": cursor is None, "servers": servers}


def snap_github(c, repos):
    out, used = [], 0
    for repo in repos:
        if used + 2 > GH_BUDGET:
            out.append({"repo": repo, "error": "skipped: hourly request budget reached"})
            continue
        r = c.get(f"{GITHUB}/repos/{repo}", headers={"Accept": "application/vnd.github+json"})
        used += 1
        if r.status_code != 200:
            out.append({"repo": repo, "error": f"HTTP {r.status_code}"})
            if r.status_code == 403:
                break
            continue
        d = r.json()
        rel = c.get(f"{GITHUB}/repos/{repo}/releases/latest")
        used += 1
        tag = None
        if rel.status_code == 200:
            tag = {"tag": rel.json().get("tag_name"), "publishedAt": rel.json().get("published_at")}
        out.append({"repo": repo, "url": d.get("html_url"), "stars": d.get("stargazers_count"),
                    "forks": d.get("forks_count"), "open_issues": d.get("open_issues_count"),
                    "createdAt": d.get("created_at"), "pushedAt": d.get("pushed_at"),
                    "updatedAt": d.get("updated_at"), "latestRelease": tag})
    return {"source": GITHUB + " (unauthenticated)", "requests_used": used, "repos": out}


def snap_marketplace(c):
    if not c.allowed(MARKETPLACE):
        return {"source": MARKETPLACE, "error": "robots.txt disallows; not fetched"}
    r = c.get(MARKETPLACE)
    r.raise_for_status()
    text = r.text.replace('\\"', '"')
    i = text.find('"templates":[')
    if i < 0:
        return {"source": MARKETPLACE, "error": "page layout changed; no listings parsed"}
    items, _ = json.JSONDecoder().raw_decode(text[i + len('"templates":'):])
    # Keep only minimal fields; descriptions and images are NOT copied (no bulk republishing).
    keep = [{"id": t.get("id"), "name": t.get("name"), "creatorHandle": t.get("handle"),
             "categories": t.get("categories", []), "updatedAt": t.get("updatedAt"),
             "installCountShown": t.get("installCount")} for t in items]
    return {"source": MARKETPLACE, "listings": keep}


def cmd_snapshot(a):
    if not a.contact or "@" not in a.contact and "://" not in a.contact:
        sys.exit("A --contact email or URL is required so site owners can reach you.")
    os.makedirs(a.out, exist_ok=True)
    c = Client(a.contact)
    t = now_et()
    snap = {"pluginpulse": VERSION, "captured_et": stamp(t), "sources": {}}
    repos = [l.strip() for l in open(a.repos) if l.strip() and not l.startswith("#")]
    jobs = {"registry": lambda: snap_registry(c, a.registry_pages, a.registry_days),
            "github": lambda: snap_github(c, repos),
            "marketplace": lambda: snap_marketplace(c)}
    for name, fn in jobs.items():
        if name in a.skip:
            continue
        try:
            snap["sources"][name] = fn()
        except Exception as e:  # record the failure honestly, keep other sources
            snap["sources"][name] = {"error": str(e)}
        snap["sources"][name]["captured_et"] = stamp(now_et())
    snap["request_log"] = c.log
    path = os.path.join(a.out, f"snapshot-{t:%Y-%m-%d}.json")
    json.dump(snap, open(path, "w"), indent=1, ensure_ascii=False)
    print(f"wrote {path} ({len(c.log)} requests)")


def load_snaps(out):
    snaps = []
    for p in sorted(glob.glob(os.path.join(out, "snapshot-*.json"))):
        d = json.load(open(p))
        d["_date"] = dt.date.fromisoformat(re.search(r"(\d{4}-\d{2}-\d{2})", p).group(1))
        snaps.append(d)
    return snaps


def recent(iso, since):
    if not iso:
        return False
    try:
        return dt.datetime.fromisoformat(iso.replace("Z", "+00:00")) >= since
    except ValueError:
        return False


def cmd_digest(a):
    snaps = load_snaps(a.out)
    if not snaps:
        sys.exit("No snapshots found. Run `snapshot` first.")
    cur, first = snaps[-1], snaps[0]
    span = (cur["_date"] - first["_date"]).days
    since = dt.datetime.now(ET) - dt.timedelta(days=a.days)
    src = cur["sources"]
    L = [f"# Movers & Shakers: week ending {cur['_date']}",
         f"Generated {stamp(now_et())} by PluginPulse {VERSION}. Every number below names its source "
         f"and capture time (ET). Read-only public data. No install or rating claims are made.", ""]
    reg = src.get("registry", {})
    if "servers" in reg:
        cap = reg["captured_et"]
        new = [s for s in reg["servers"] if recent(s["publishedAt"], since)]
        upd = [s for s in reg["servers"] if recent(s["updatedAt"], since) and s not in new]
        L += [f"## MCP Registry (source: {REGISTRY}, captured {cap})",
              f"- Servers changed since {reg.get('updated_since_utc', '?')} (UTC; latest versions, {reg['pages_read']} page(s), "
              f"{'complete' if reg['complete'] else ('PARTIAL: ' + reg['error'] if reg.get('partial') else 'partial: page limit reached')}): {len(reg['servers'])}",
              f"- Published in last {a.days} days (new server or new version; the registry does not separate them): {len(new)}", f"- Metadata updated in last {a.days} days without a new version: {len(upd)}", ""]
        for s in sorted(new, key=lambda s: s["publishedAt"], reverse=True)[:10]:
            L.append(f"  - PUBLISHED `{s['name']}` v{s['version']} (published {s['publishedAt'][:10]})")
        L.append("")
    gh = src.get("github", {})
    if "repos" in gh:
        cap = gh["captured_et"]
        L += [f"## Tracked GitHub repos (source: GitHub REST API, captured {cap})", ""]
        base = {r["repo"]: r for r in first["sources"].get("github", {}).get("repos", []) if "stars" in r}
        rows = []
        for r in gh["repos"]:
            if "stars" not in r:
                L.append(f"- {r['repo']}: not captured ({r.get('error')})")
                continue
            growth = r["stars"] - base[r["repo"]]["stars"] if r["repo"] in base else None
            rows.append((growth if growth is not None else -1, r, growth))
            rel = r["latestRelease"]["tag"] if r.get("latestRelease") else "no GitHub Release"
            L.append(f"- [{r['repo']}]({r['url']}): {r['stars']} stars, {r['forks']} forks, "
                     f"latest release {rel}, last push {r['pushedAt'][:10]}")
        L.append("")
        L.append("### Rising (star growth)")
        if span < 7:
            L.append(f"- Not enough history yet: snapshots cover {span} day(s); rising needs 7 or more days. "
                     "Keep the daily snapshot running.")
        else:
            for g, r, growth in sorted(rows, key=lambda x: x[0], reverse=True)[:10]:
                if growth is None:
                    L.append(f"- {r['repo']}: no baseline (not in the {first['_date']} snapshot); "
                             f"{r['stars']} stars now, growth not ranked")
                else:
                    L.append(f"- {r['repo']}: {growth:+d} stars since {first['_date']}")
        L.append("")
    mp = src.get("marketplace", {})
    if "listings" in mp:
        cap = mp["captured_et"]
        ls = mp["listings"]
        cats = Counter(c for t in ls for c in t["categories"])
        upd = [t for t in ls if recent(t["updatedAt"], since)]
        L += [f"## Marketplace (source: {MARKETPLACE}, captured {cap})",
              f"- Listings shown: {len(ls)}",
              f"- Updated in last {a.days} days: {len(upd)}"]
        for t in upd[:10]:
            L.append(f"  - {t['name']} by @{t['creatorHandle']} (updated {t['updatedAt'][:10]})")
        L.append("- Category counts (a listing can be in more than one): " +
                 ", ".join(f"{k} {v}" for k, v in cats.most_common()))
        if all(t.get("installCountShown") == 0 for t in ls):
            L.append("- Install counts: the page shows 0 for every listing, so PluginPulse does not rank by installs.")
        L += [f"- See the listings themselves: {MARKETPLACE}", ""]
    for name, d in src.items():
        if "error" in d:
            L.append(f"- {name}: not captured ({d['error']})")
    path = os.path.join(a.out, f"digest-{cur['_date']}.md")
    open(path, "w").write("\n".join(L) + "\n")
    print(f"wrote {path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("snapshot")
    s.add_argument("--contact", required=True)
    s.add_argument("--out", default="pluginpulse-data")
    s.add_argument("--repos", default=os.path.join(os.path.dirname(__file__), "repos.txt"))
    s.add_argument("--registry-pages", type=int, default=20)
    s.add_argument("--registry-days", type=int, default=8, help="only servers updated in the last N days")
    s.add_argument("--skip", nargs="*", default=[], choices=["registry", "github", "marketplace"])
    d = sub.add_parser("digest")
    d.add_argument("--out", default="pluginpulse-data")
    d.add_argument("--days", type=int, default=7)
    a = ap.parse_args()
    cmd_snapshot(a) if a.cmd == "snapshot" else cmd_digest(a)


if __name__ == "__main__":
    main()
