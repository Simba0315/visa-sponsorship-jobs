"""Rewrites README.md from a Jobs Every Hour list feed. Runs in GitHub Actions; standard library only.
The feed is read from list.json ("feed"); if it cannot be read, the README stays as it is."""
import datetime, json, sys, urllib.request

C = json.load(open("list.json", encoding="utf-8"))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "daily-job-list (+https://github.com/" + C["repo"] + ")"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def cell(s):
    return " ".join(str(s or "").replace("|", "/").split())


try:
    d = fetch(C["feed"])
except Exception as err:
    print("feed not reachable, README unchanged:", err)
    sys.exit(0)
jobs = d.get("jobs") or []
if not jobs:
    print("feed is empty, README unchanged")
    sys.exit(0)

today = datetime.date.today().isoformat()
rows = []
for j in jobs:
    place = cell(j.get("location")) or ("Remote" if j.get("remote") else "")
    if j.get("remote") and "remote" not in place.lower():
        place = (place + " · Remote").strip(" ·")
    rows.append(f"| **{cell(j['company'])}** | [{cell(j['title'])}]({j['url']}) | {place or '—'} | {cell(j.get('salary')) or '—'} | {cell(j.get('posted'))} |")

more = " · ".join(f"[{name}]({url})" for name, url in C["more"])
readme = f"""# {C['title']}

{C['intro']}

**{d.get('total', len(jobs)):,} open right now · updated {today}.** The list below shows the {len(jobs):,} newest. Jobs come from
[Jobs Every Hour]({C['page']}), which reads employers' own career pages every hour and drops a job as soon as the employer closes it,
so you do not apply to stale copies. Each link opens the job's page with the employer's own apply button.

⭐ Star or watch this repository to see new jobs as they come in.

| Company | Role | Location | Pay | Posted |
| --- | --- | --- | --- | --- |
{chr(10).join(rows)}

## More

{more}

The same list as JSON: {C['feed']} (free, no key; please link back to [Jobs Every Hour](https://jobseveryhour.com/)).
This list only links to jobs; applications go to each employer.
"""
with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)
print(f"README.md rewritten: {len(jobs)} jobs, {d.get('total')} open")
