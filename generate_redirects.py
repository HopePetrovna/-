# generate_redirects.py (clean URLs + short base62 tokens)
import os, sys, html, csv, random, string
from datetime import datetime
import pathlib

TARGETS_ENV = os.getenv("TARGETS", "")
PER_TARGET = int(os.getenv("PER_TARGET", "50"))
BASE_URL = os.getenv("BASE_URL", "").rstrip("/")  # https://owner.github.io/repo
SHOW_FIRST = int(os.getenv("SHOW_FIRST", "50"))

# де лежатимуть редіректи (коротка папка 'r')
ROOT_DIR = pathlib.Path("docs")
OUT_DIR = ROOT_DIR / "r"   # docs/r/<token>/index.html
MAP_CSV = ROOT_DIR / "redirects_map.csv"
LINKS_TXT = ROOT_DIR / "links.txt"

if not TARGETS_ENV.strip():
    print("ERROR: provide targets via TARGETS (one per line)")
    sys.exit(2)

targets = [t.strip() for t in TARGETS_ENV.splitlines() if t.strip()]
if not targets:
    print("ERROR: no valid targets")
    sys.exit(3)

def rand_token(n=6):
    alphabet = string.ascii_letters + string.digits  # a-zA-Z0-9
    return "".join(random.choice(alphabet) for _ in range(n))

def html_doc(url: str) -> str:
    safe = html.escape(url, quote=True)
    ts = datetime.utcnow().isoformat() + "Z"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url={safe}">
  <title>Redirecting…</title>
  <script>try{{window.location.replace("{safe}");}}catch(e){{}}</script>
  <meta name="robots" content="noindex">
  <style>body{{font-family:system-ui,Arial;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}}.box{{text-align:center}}</style>
</head>
<body>
  <div class="box">
    <p>Redirecting… If not, <a href="{safe}">tap here</a>.</p>
    <p style="font-size:12px;color:#666">Generated: {ts}</p>
  </div>
</body>
</html>"""

OUT_DIR.mkdir(parents=True, exist_ok=True)

rows = []
full_links = []

for idx, tgt in enumerate(targets, start=1):
    for i in range(PER_TARGET):
        token = rand_token(6)  # короткий і унікальний
        folder = OUT_DIR / token
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "index.html").write_text(html_doc(tgt), encoding="utf-8")
        rel_link = f"r/{token}/"
        rows.append((rel_link, tgt))
        if BASE_URL:
            full_links.append(f"{BASE_URL}/{rel_link}")

# CSV карта: относительный путь -> target
MAP_CSV.parent.mkdir(parents=True, exist_ok=True)
with MAP_CSV.open("w", newline="", encoding="utf-8") as f:
    import csv
    w = csv.writer(f); w.writerow(["path","target_url"]); w.writerows(rows)

# TXT з повними URL (для копіпасту)
if BASE_URL and full_links:
    LINKS_TXT.write_text("\n".join(full_links) + "\n", encoding="utf-8")
    print(f"\n=== First {min(SHOW_FIRST,len(full_links))} links ===")
    for u in full_links[:SHOW_FIRST]:
        print(u)
    print("=== End ===\n")
else:
    print("WARNING: BASE_URL empty, links.txt not created.")

print(f"Created {len(rows)} redirects under {OUT_DIR}")
print(f"Map: {MAP_CSV}")
if LINKS_TXT.exists():
    print(f"All links: {LINKS_TXT}")
