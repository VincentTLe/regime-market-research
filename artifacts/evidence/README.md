# Committed evidence

Everything under `artifacts/` is a generated run output, and `.gitignore` keeps
it local — the runs are hundreds of megabytes of refit caches, state matrices
and trade ledgers. This one directory is the exception.

**What belongs here.** A small derived table, produced by this repository's own
code, that a durable claim depends on. Durable means a claim in `README.md`,
`CURRENT.md`, `docs/`, or the manuscript — something a reader meets without
being told to go looking for a specific old run.

**What does not.** Raw or reconstructed market data (see `data/README.md`),
daily state matrices, feature tables, trade ledgers, `.npz` refit caches, or a
whole run directory copied in for completeness. `docs/evidence-policy.md`
states the rule these follow from.

**These are stand-ins, not a second source of truth.** Each file is a
byte-for-byte copy of a file inside a local run directory. Nothing was
recomputed, re-rounded, or re-fitted to produce them, and no pipeline code
reads this directory. The sha256 below identifies each copy. On a machine that still has the run,
the copy and the original can be compared byte for byte; nothing runs that
comparison automatically, so a regenerated run does not update this copy and a
stale copy is detected only when someone compares.

---

## `sealed-baseline-v11/`

The sealed **v11-ninit60** fixed Jump Model — the comparator `CURRENT.md`
measures every new idea against. Its settings are tracked
(`configs/baselines/research-calibrated-v11.toml`); until now its *results* were
not, so a fresh clone could read what the comparator is but not what it scored.

Kind: **derived** — model output and summary statistics computed by
`src/adaptive_jump/` from the local canonical series. Not raw data, and not a
canonical input to anything. Audit evidence only.

Source run: `artifacts/fixed-baselines/fixed-baselines-5b12efa2948c-d57a9e7d9c07-b277dea3beb3/`
(local-only, 73 MB). **2026-09-01:** the machine that held that run is gone, so
these five files are now the only surviving record of the sealed v11-ninit60
results, and the byte-for-byte comparison described above can no longer be run
by anyone. Produced by that run on 2026-08-08 from config sha256
`5b12efa2948c…`, which is the sha256 of the tracked
`configs/baselines/research-calibrated-v11.toml` — the same bytes, so no copy of
the config is kept here.

| File | Bytes | sha256 | What it is |
| --- | --- | --- | --- |
| `boundaries.csv` | 1,050 | `c4fe2130e12238ea906ccf118a8dc516abea16474378fdce0335daad05b6baeb` | How often the fixed JM and the HMM picked the largest candidate in their own grid: 18 rows, one per market × model × trading delay, with the month counts behind each fraction. |
| `metrics.csv` | 5,245 | `5f905cbea441c752820f19d669df893625eae9c1c4af335767b0fa1216a8c48e` | The comparator's scored performance: 27 rows, one per market × model × delay. CAGR, volatility, Sharpe, maximum drawdown, Calmar, 5% expected shortfall, turnover, leverage. Every row ends 2023-12-29; US and German rows start 1990-01-02 and Japanese rows 1990-01-19. |
| `claim.json` | 673 | `b21e85390e9ce8103d019e4a1bba295c221461b729769c6196de795da9a85658` | The run's directional gate: per market, whether the fixed JM beat buy-and-hold and the HMM on Sharpe and drawdown. |
| `data-manifest.json` | 13,124 | `d57a9e7d9c07e76c87ef094068246054ebaf9170665a69fa4bfa8cc4391e3a25` | For each of the six input series: the sha256, row count and date range of both the raw file the run read and the processed file it built. This is what a rebuilt copy is compared against. |
| `run.json` | 840 | `c56f717fb4940621acc2d0ffa1a47f5e4a315a45c08ffbe0b66aea3ed3992c6a` | Config sha256, git sha, timestamps, and the exact package versions (numpy, pandas, scikit-learn, hmmlearn, jumpmodels, scipy). |

The run's own `inventory.json` independently records the first four hashes.
`run.json` is not in it, because the inventory is sealed before the run record
is written.

One cosmetic wart, left as-is because these are verbatim copies:
`data-manifest.json` records `config_path` as an absolute path on the owner's
machine. It is a local path, not a repository path, and nothing reads it.

### What these numbers do and do not settle

`boundaries.csv` is the file the "upper boundary" passage in
`docs/unspecified-choices.md` needed and did not have. It reports, at the
primary 1-day delay, that the fixed JM selected its grid's largest penalty in
**18.1%** of German months (74 of 408), **28.7%** of US months (117 of 408) and
**37.0%** of Japanese months (151 of 408). That is a count of which *tested*
penalty scored best. It does not show that a larger penalty would have been
selected had one been offered — no lambda-widening test has been run — and the
gate that reports it, `upper_boundary_month_fraction_limit`, is set to 1.0, so
it cannot fail.

`metrics.csv` is what the sealed comparator scored, not evidence that the
comparator is the right one. `CURRENT.md` records the open problem: rerun at the
60 optimizer restarts this baseline actually uses, the rule that chose its
lambda grids ranks a different grid first in every market, and the German
adopted grid drops out of the eligible set altogether; the US and Japanese
adopted grids stay eligible and close to the top
(`docs/audit/2026-08-08-grid-selection-rule-001-ninit60-receipt.md`). The
German leg is the defect `CURRENT.md` names.

None of these five files lets a fresh clone *recompute* anything. The six input
series they were computed from are not in this repository and cannot be
published. See `data/README.md`.
