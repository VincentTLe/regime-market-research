# data/

**None of the market data in this directory is published.** `.gitignore` keeps
all of it local, on purpose, and a fresh clone gets an almost empty `data/`.
This file says what is here, why it stays here, and what a fresh clone can do
instead.

`docs/data-provenance.md` is the full account of where each series comes from
and what it can and cannot be. `docs/evidence-policy.md` is the rule that
decides what this repository publishes. This is only the map.

## What is where

| Path | Holds | Tracked? |
| --- | --- | --- |
| `data/external/inputs/` | The 17 sha256-pinned raw files the builders read, plus the papers | 6 files: the Shu paper text and three freely-licensed arXiv PDFs and extractions |
| `data/external/*.csv` | The 7 canonical series the builders write; 5 of them are what the sealed baseline reads | no |
| `data/external/fama-french/` | Ken French daily factor files for the ajm-ext extension | no |
| `data/external/inputs/manual-verification/` | Independent downloads used once to cross-check the Japanese reconstruction | no |
| `data/raw/<run>/` | What each run actually acquired, with a `manifest.json`. 5 runs kept | no |
| `data/processed/<run>/` | The normalized canonical series each run built from those. 5 runs kept | no |
| `data/legacy-cold/` | Cold storage for the retired minute-era data (paid vendor) | no |

Two of the seven files in `data/external/` — `de_equity_tr.csv` and
`us_equity_tr.csv` — are superseded series that only the legacy v8.5 config
reads. They are history, not current inputs.

## Why none of it is published

The sealed baseline contract says so directly. In
`configs/baselines/research-calibrated-v11.toml`:

```toml
[data_policy]
local_research_only = true
redistribute_raw_data = false
```

and the frozen contract for the Fama-French files records
`raw_redistribution = false` for those specifically
(`research/contracts/ajm-ext-001-data.lock.toml`).

That is a project decision already on the record, and it settles the question
for now. It is **not** the same as having checked each vendor's terms one by
one. Nobody in this repository has done that, and the individual terms for
Yahoo Finance, Stooq, Nikkei, Investing.com, MSCI, the IMF series that FRED
redistributes, the Ken French library, JST Macrohistory, OECD, ECB and the
Shiller dataset mirror are all still **UNKNOWN** here. `docs/evidence-policy.md`
lists them.

## What a fresh clone can do instead

The rebuild route is fully tracked:

- `scripts/data/build_external_sources.py` — builds five of the canonical
  series, and refuses to run unless all 17 inputs hash to their pinned
  `INPUT_SHA256` values, which are in that file.
- `scripts/data/build_sp500_tr.py` — the US total-return reconstruction, with
  three overlap gates it raises on rather than returning.
- `scripts/data/build_de_total_return.py` — the German pre-1988 dividend
  repair, with three gates of its own.
- `configs/baselines/research-calibrated-v11.toml` — pins the sha256 of every
  canonical file the sealed baseline reads.
- `artifacts/evidence/sealed-baseline-v11/data-manifest.json` — the sha256, row
  count and date range of both the raw and the processed copy of all six series
  the sealed run used.

So a rebuilt series can be checked against ours byte for byte.

**But a fresh clone cannot start that route**, and this is the honest limit:
the 17 pinned inputs are not in the repository, and `docs/data-provenance.md`
records that they cannot be re-downloaded dependably either — Yahoo's chart
endpoint rate-limits hard, Stooq's CSV link now answers with a browser
challenge, and the Nikkei total-return mirror and MSCI comparison were manual
downloads. Getting the inputs is a manual job against sources that have since
changed their access. Nothing here should be read as "the data pipeline
reproduces from a clean checkout."

## If you do change something here

`AGENTS.md` rule 4: the files in `data/raw/` and `data/external/` are the
evidence an audit is checking, and git ignores them, so if they change
`git status` still looks clean. The three builders write straight into
`data/external/` with no output option, so rebuild in a copy of the repository
and compare, never in place.
