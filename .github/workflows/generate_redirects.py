# generate_redirects.py
import os, sys, html, csv
from datetime import datetime
import uuid, pathlib

TARGETS_ENV = os.getenv("TARGETS", "")
PER_TARGET = int(os.getenv("PER_TARGET", "50"))
OUT_DIR = pathlib.Path("docs/redirects")
MAP_CSV = pathlib.Path("docs/redirects_map.csv")

if not TARGETS_ENV.strip():
    print("ERROR: provide targets via TARGETS (one per line)")
    sys.exit(2)

targets = [t.strip() for t in TARGETS_ENV.splitlines() if t.strip()]
if not targets:
    print("ERROR: no valid targets")
    sys.exit(3)

OUT_DIR.mkdir(parents=True, exist_ok=True)

def make_html(url: str) -> str:
    s = html.escape(url, quote=True)
    ts = datetime.utcnow().isoformat() + "Z"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url={s}">
  <title>Redirecting…</title>
  <script>try{{window.location.replace("{s}");}}catch(e){{}}</script>
  <meta name="robots" content="noindex">
  <style>body{{font-family:system-ui,Arial;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}}.box{{text-align:center}}</style>
</head>
<body>
  <div class="box">
    <p>Redirecting… If not, <a href="{s}">tap here</a>.</p>
    <p style="font-size:12px;color:#666">Generated: {ts}</p>
  </div>
</body>
</html>"""

created = []
for idx, tgt in enumerate(targets, start=1):
    for i in range(1, PER_TARGET + 1):
        token = f"t{idx}-{i:03d}-{uuid.uuid4().hex[:5]}"
        (OUT_DIR / f"{token}.html").write_text(make_html(tgt), encoding="utf-8")
        created.append((f"{token}.html", tgt))

MAP_CSV.parent.mkdir(parents=True, exist_ok=True)
with MAP_CSV.open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["filename","target_url"]); w.writerows(created)

print(f"Created {len(created)} files in {OUT_DIR}")
print(f"Map at {MAP_CSV}")
