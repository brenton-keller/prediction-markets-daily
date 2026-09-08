---
license: cc0-1.0
tags: [prediction-markets, kalshi, polymarket, finance, weather, arbitrage]
pretty_name: Prediction Markets Daily (Kalshi + Polymarket)
---

# Prediction Markets Daily: Kalshi + Polymarket

A daily snapshot of the two largest US prediction-market venues in one schema, refreshed every morning by a GitHub Action.

| File | Rows | What |
|---|---|---|
| `latest/markets.{csv,jsonl}` | top 1,000 open markets by 24h volume, both venues | price, bid/ask, volume, liquidity, open interest, close time, links |
| `latest/spreads.{csv,jsonl}` | matched Kalshi/Polymarket weather pairs | both prices, spread, executable edge, fee estimate, match score |
| `latest/settled.{csv,jsonl}` | markets settled in the last 24h | result, settlement value |
| `data/<date>/` | the same files per day | history back to the first snapshot |

Schema: [actor README](https://apify.com/brenton8907/prediction-markets-data). Prices are 0 to 1 (P(yes)); Kalshi volume is contracts, Polymarket volume is USD.

## Live data, more markets, orderbooks, monitor mode

This snapshot is once a day and drops orderbooks and rules to keep files small. For live pulls (any category, keyword, ticker or tag, orderbook depth, recent trades, changes-only monitoring, cross-venue spreads on demand) run the actor that produces it:

- Apify Store: https://apify.com/brenton8907/prediction-markets-data (pay per result, $1.50 per 1,000 rows)
- From an AI agent: `https://mcp.apify.com/?tools=brenton8907/prediction-markets-data` (MCP), or the official MCP registry entry `io.github.brenton-keller/prediction-markets-data`
- API: `POST https://api.apify.com/v2/acts/brenton8907~prediction-markets-data/runs`

Data is provided as-is from the venues' public APIs. Not financial advice.
