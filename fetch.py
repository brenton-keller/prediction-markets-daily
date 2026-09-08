#!/usr/bin/env python3
"""Daily snapshot of Kalshi + Polymarket markets and cross-venue spreads via the Apify actor
brenton8907/prediction-markets-data. Writes data/<date>/*.{jsonl,csv} and refreshes latest/.

Env: APIFY_TOKEN (required). Owner runs of a pay-per-event actor are not charged events."""
from __future__ import annotations

import csv
import json
import os
import shutil
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ACTOR = 'brenton8907~prediction-markets-data'
API = 'https://api.apify.com/v2'
TOKEN = os.environ.get('APIFY_TOKEN', '')
SNAPSHOTS = {
    'markets': {'maxItems': 1000, 'sortBy': 'volume_24h'},
    'spreads': {'mode': 'spread', 'weatherPreset': True, 'maxItems': 500},
    'settled': {'status': 'settled', 'settledLookbackDays': 1, 'maxItems': 2000},
}
DROP = {'raw', 'orderbook', 'recent_trades', 'rules', 'kalshi_rules', 'polymarket_rules'}


def api(method: str, path: str, body: dict | None = None) -> dict | list:
    req = urllib.request.Request(f'{API}{path}', method=method, headers={'Authorization': f'Bearer {TOKEN}', 'Content-Type': 'application/json'},
                                 data=json.dumps(body).encode() if body is not None else None)
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.load(r)


TERMINAL = {'SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'}


def run(inp: dict, max_wait_secs: int = 1200) -> list[dict]:
    d = api('POST', f'/acts/{ACTOR}/runs?waitForFinish=60', inp)['data']
    waited = 60
    while d['status'] not in TERMINAL and waited < max_wait_secs:  # the API waits at most 60s per call; queued runs need polling
        d = api('GET', f"/actor-runs/{d['id']}?waitForFinish=60")['data']
        waited += 60
    if d['status'] != 'SUCCEEDED':
        raise SystemExit(f"run {d['id']} ended {d['status']}")
    items = api('GET', f"/datasets/{d['defaultDatasetId']}/items?clean=true&limit=10000")
    print(f"{d['id']}: {len(items)} rows", file=sys.stderr)
    return items


def write(rows: list[dict], path: Path) -> None:
    rows = [{k: v for k, v in r.items() if k not in DROP} for r in rows]
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path.with_suffix('.jsonl'), 'w') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(path.with_suffix('.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (json.dumps(v) if isinstance(v, (list, dict)) else v) for k, v in r.items()})


def main() -> None:
    if not TOKEN:
        raise SystemExit('APIFY_TOKEN missing')
    day = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    out = Path('data') / day
    counts = {}
    for name, inp in SNAPSHOTS.items():
        rows = run(inp)
        write(rows, out / name)
        counts[name] = len(rows)
    latest = Path('latest')
    shutil.rmtree(latest, ignore_errors=True)
    shutil.copytree(out, latest)
    shutil.copy('dataset-metadata.template.json', latest / 'dataset-metadata.json')  # Kaggle reads it from the upload dir
    (latest / 'manifest.json').write_text(json.dumps({'date': day, 'fetched_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                                                       'rows': counts, 'source_actor': 'https://apify.com/brenton8907/prediction-markets-data'}, indent=2))
    print(json.dumps(counts))


if __name__ == '__main__':
    main()
