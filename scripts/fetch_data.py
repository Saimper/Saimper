#!/usr/bin/env python3
"""Recolecta metricas reales de GitHub (repos propios, publicos y privados)."""
import json, subprocess, collections, datetime, sys, os

USER = "Saimper"
DAYS = 371

def gh(path, paginate=True):
    cmd = ["gh", "api", path]
    if paginate:
        cmd += ["--paginate", "--slurp"]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        return []
    try:
        data = json.loads(out.stdout or "[]")
    except json.JSONDecodeError:
        return []
    if paginate and isinstance(data, list):
        return [item for page in data for item in (page if isinstance(page, list) else [page])]
    return data

since = (datetime.date.today() - datetime.timedelta(days=DAYS)).isoformat()
# user/repos usa el token: incluye repos privados propios. users/<login>/repos solo devuelve publicos.
repos = gh("user/repos?per_page=100&affiliation=owner")
if not repos:
    repos = gh(f"users/{USER}/repos?per_page=100&type=owner")

by_day = collections.Counter()
langs = collections.Counter()
repo_stats = []

for r in repos:
    if r.get("owner", {}).get("login") != USER:
        continue
    name = r["name"]
    commits = gh(f"repos/{USER}/{name}/commits?author={USER}&since={since}T00:00:00Z&per_page=100")
    n = 0
    for c in commits:
        d = (c.get("commit", {}).get("author", {}) or {}).get("date")
        if d:
            by_day[d[:10]] += 1
            n += 1
    lg = gh(f"repos/{USER}/{name}/languages", paginate=False)
    if isinstance(lg, dict):
        for k, v in lg.items():
            langs[k] += v
    repo_stats.append({
        "name": name, "private": r["isPrivate"] if "isPrivate" in r else r.get("private", False),
        "commits": n, "lang": (r.get("language") or ""), "stars": r.get("stargazers_count", 0),
        "pushed": (r.get("pushed_at") or "")[:10], "desc": r.get("description") or "",
        "url": r.get("homepage") or "",
    })
    print(f"  {name}: {n}", file=sys.stderr)

data = {
    "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    "by_day": dict(by_day),
    "languages": dict(langs.most_common(14)),
    "repos": sorted(repo_stats, key=lambda x: -x["commits"]),
    "total_commits": sum(by_day.values()),
    "active_days": len(by_day),
    "repo_count": len(repo_stats),
}
out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

# Guarda: si el token no alcanza los repos privados, la recoleccion sale mucho mas
# pobre que la anterior. Preferimos abortar antes que sobrescribir el perfil con
# datos parciales (un GITHUB_TOKEN normal solo ve el repo del workflow).
if os.path.exists(out_path):
    prev = json.load(open(out_path))
    if data["total_commits"] < prev["total_commits"] * 0.6:
        print(f"ABORTA: {data['total_commits']} commits frente a {prev['total_commits']} previos. "
              f"El token no esta viendo los repos privados (falta el secret METRICS_TOKEN).",
              file=sys.stderr)
        sys.exit(1)

json.dump(data, open(out_path, "w"), indent=1)
print(f"\ntotal={data['total_commits']} dias_activos={data['active_days']} repos={data['repo_count']}", file=sys.stderr)
