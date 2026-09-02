# Snapshot `v11-ninit60` — the bytes the sealed v11-ninit60 baseline read

This folder is **archival evidence, never an input**. Nothing in the research
code reads it. It is a byte-exact copy of the eighteen data files that the
sealed run `fixed-baselines-5b12efa2948c-d57a9e7d9c07-b277dea3beb3` (2026-08-08)
consumed, kept so that a fresh checkout can inspect exactly what that run saw.

Do not edit anything here. If a file must change, the run it documents has
changed, and that is a new snapshot with a new id.

## What is inside

| folder | files | what they are |
|---|---|---|
| `external/` | 5 | the processed series `configs/baselines/research-calibrated-v11.toml` pins by sha256 (S&P 500 TR, DAX TR dividend-adjusted, German cash ladder, Nikkei 225 TR, Japanese cash ladder) |
| `raw/shu-replication-calibrated-v11-20260808T073312Z/` | 8 | the acquisition manifest, the FRED DTB3 download (`us_cash.csv`), and the six localfile copies as acquired |
| `processed/shu-replication-calibrated-v11-20260808T073312Z/` | 6 | the canonical `date,value` series the model actually loads |
| `SHA256SUMS` | — | sha256 of every file above |
| `snapshot.json` | — | which config, which acquisition run, which sealed run |

Three of the five `external/` series (the equity indices) are reconstructions
built from vendor downloads (Yahoo, Stooq, Nikkei via an Investing.com mirror);
see `docs/data-provenance.md`. The vendor downloads themselves are not
published.

## How it relates to the live inputs

The live inputs stay where the code reads them and stay git-ignored:
`data/external/`, `data/raw/<run>/`, `data/processed/<run>/`. Publishing the
snapshot at a separate path means checking out this commit can never overwrite
a locally built input.

`tests/test_data_snapshots.py` checks, on every run, that this folder matches
`SHA256SUMS`, the config pins, and the acquisition manifest. When a live input
exists at the corresponding ignored path it also checks the two are
byte-identical, so a local rebuild that drifted from the sealed bytes is
reported instead of silently coexisting.

## What this snapshot does not establish

That the data is correct, that the sealed run's results are right, or that the
reconstruction choices are the paper's. It only fixes which bytes the run read.
