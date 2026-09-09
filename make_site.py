#!/usr/bin/env python3
"""Render index.html (GitHub Pages) from latest/: today's cross-venue spreads and top markets, with links back to the actor."""
from __future__ import annotations

import html
import json
from pathlib import Path

ACTOR = 'https://apify.com/brenton8907/prediction-markets-data'
MCP = 'https://mcp.apify.com/?tools=brenton8907/prediction-markets-data'
REPO = 'https://github.com/brenton-keller/prediction-markets-daily'


def rows(name: str) -> list[dict]:
    p = Path('latest') / f'{name}.jsonl'
    return [json.loads(l) for l in p.open()] if p.exists() else []


def td(v, fmt=None):
    if v is None:
        return '<td></td>'
    if isinstance(v, float) and fmt:
        v = fmt % v
    return f'<td>{html.escape(str(v))}</td>'


def link(url: str | None, text: str) -> str:
    return f'<a href="{html.escape(url)}">{html.escape(text)}</a>' if url else html.escape(text)


def main() -> None:
    m = json.load(open('latest/manifest.json'))
    spreads = sorted(rows('spreads'), key=lambda r: -(r.get('abs_spread_pts') or 0))[:40]
    markets = rows('markets')[:40]
    settled = rows('settled')[:20]
    s_rows = ''.join(
        f"<tr>{td(link(r.get('kalshi_url'), r.get('event_title') or r.get('title') or ''))}{td(r.get('outcome_label'))}"
        f"{td(r.get('kalshi_price'), '%.3f')}{td(r.get('polymarket_price'), '%.3f')}{td(r.get('spread_pts'), '%.1f')}{td(r.get('net_edge_pts'), '%.1f')}"
        f"{td(r.get('match_score'))}</tr>" for r in spreads)
    m_rows = ''.join(
        f"<tr>{td(r.get('source'))}{td(link(r.get('url'), (r.get('title') or '')[:90]))}{td(r.get('implied_probability'), '%.3f')}"
        f"{td(r.get('volume_24h'))}{td(r.get('liquidity'))}{td((r.get('close_time') or '')[:10])}</tr>" for r in markets)
    t_rows = ''.join(f"<tr>{td(r.get('source'))}{td(link(r.get('url'), (r.get('title') or '')[:90]))}{td(r.get('result'))}</tr>" for r in settled)
    counts = ', '.join(f'{k} {v:,}' for k, v in m['rows'].items())
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Prediction Markets Daily: Kalshi + Polymarket prices, spreads and settled markets ({m['date']})</title>
<meta name="description" content="Free daily snapshot of Kalshi and Polymarket prediction markets: top markets by volume, cross-venue spread pairs with executable edge, and markets settled in the last 24h. CSV and JSONL.">
<link rel="canonical" href="https://brenton-keller.github.io/prediction-markets-daily/">
<style>body{{font:15px/1.45 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;color:#1b1b1b}}table{{border-collapse:collapse;width:100%;font-size:13px;margin:.5rem 0 1.5rem}}th,td{{border-bottom:1px solid #ddd;padding:4px 6px;text-align:left;vertical-align:top}}th{{background:#f4f4f4}}td:nth-child(n+3){{white-space:nowrap}}a{{color:#1f6f4a}}.cta{{background:#eef6f1;border:1px solid #cfe3d7;padding:.8rem 1rem;border-radius:8px}}small{{color:#666}}</style></head><body>
<h1>Prediction Markets Daily</h1>
<p>Kalshi and Polymarket in one schema, snapshotted every morning. Snapshot <b>{m['date']}</b> ({counts}).
Download: <a href="latest/markets.csv">markets.csv</a> · <a href="latest/spreads.csv">spreads.csv</a> · <a href="latest/settled.csv">settled.csv</a> · <a href="latest/">JSONL</a> · <a href="{REPO}">history on GitHub</a></p>
<div class="cta"><b>Need it live?</b> The Apify actor that produces this file returns any category, keyword, ticker or tag with orderbooks, recent trades, changes-only monitoring and on-demand spreads:
<a href="{ACTOR}">apify.com/brenton8907/prediction-markets-data</a> (pay per result). For AI agents: <code>{MCP}</code></div>
<h2>Cross-venue spreads (same question on both venues)</h2>
<p><small>Sorted by absolute spread. Prices are P(yes). Large edges on weather pairs usually mean the venues settle on different stations; check the rules before trading.</small></p>
<table><tr><th>Event</th><th>Outcome</th><th>Kalshi</th><th>Polymarket</th><th>Spread pts</th><th>Net edge</th><th>Match</th></tr>{s_rows}</table>
<h2>Top open markets by 24h volume</h2>
<table><tr><th>Venue</th><th>Market</th><th>P(yes)</th><th>Vol 24h</th><th>Liquidity</th><th>Closes</th></tr>{m_rows}</table>
<h2>Settled in the last 24h</h2>
<table><tr><th>Venue</th><th>Market</th><th>Result</th></tr>{t_rows}</table>
<p><small>Data as-is from the venues' public APIs via <a href="{ACTOR}">the actor</a>. CC0. Not financial advice.</small></p>
</body></html>"""
    Path('index.html').write_text(page)
    print(f'index.html: {len(spreads)} spreads, {len(markets)} markets, {len(settled)} settled')


if __name__ == '__main__':
    main()
