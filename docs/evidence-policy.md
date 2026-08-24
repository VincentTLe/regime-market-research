# What this repository publishes

This is a public repository about a study built on data we are not allowed to
republish. That tension is the whole problem this file resolves. It states one
rule, sorts every candidate file into one of four buckets, and records honestly
what a fresh clone still cannot check.

## The rule

> If an important number appears in `README.md`, `CURRENT.md`, `docs/`, or the
> manuscript, then a fresh clone must have **either** the lightweight evidence
> file itself, **or** tracked code plus tracked, legally redistributable inputs
> that reproduce it.

A number that exists only on the owner's laptop is not repository evidence.
Where neither half of the rule can be met, the claim says so where it is made.

## Why this file exists

`docs/unspecified-choices.md` used to report exact figures — the fixed Jump
Model selected its grid's largest penalty in 18.1% of German months, 28.7% of
US months, 37.0% of Japanese months. They were read off a `boundaries.csv`
inside a run directory that `.gitignore` excludes. A reader who cloned the
repository could not open the file, could not recompute it, and had no way to
tell that the numbers were unverifiable. They were deleted rather than
supported.

That was the right call for the sentence and the wrong fix for the repository.
The file was 1,050 bytes of our own model's output. It should simply have been
tracked. `artifacts/evidence/sealed-baseline-v11/boundaries.csv` now is, and it
reproduces those three figures exactly.

## Three kinds of material

**1. Public research data** — data we may legally redistribute and that helps
somebody reproduce or inspect the study.

*This repository has almost none.* The only material in this class is
primary-source paper text: the Shu, Yu and Mulvey preprint and two companion
arXiv preprints, tracked under `data/external/inputs/` because
`scripts/audit/check_paper_claims.py` verifies `[line NNN]` citations against
them. Every market series is excluded — see the classification below, and
the one accidental exception recorded under "One thing already tracked".

**2. Public research evidence** — small derived tables produced by our own
code that support a durable claim. This is where the repository can be
genuinely open, and it is the class this work extends.

Lives in `artifacts/evidence/`, plus the per-study carve-outs that predate it
(`artifacts/hmm-residual/`, `artifacts/jm-residual/`, `artifacts/audit/`,
`artifacts/grid-selection-rule/`, `artifacts/optimizer-fidelity/`,
`artifacts/v12-stress-gate/`, `artifacts/lagged-capguard/`,
`artifacts/confirmed2d-episodes/`). 186 tracked files in total, all small
tables, reports and the scripts that produced them.

**3. Local, regenerable, or restricted** — everything else. Vendor data,
uncertain-licence downloads, paywalled PDFs, and the roughly 2.9 GB of run
output under `artifacts/`, nearly all of it refit caches, state matrices,
feature tables and trade ledgers that a rerun regenerates.

## Classification

Read `A` as *safe to commit*, `B` as *commit the code and the recipe instead*,
`C` as *keep local*, `D` as *not enough evidence to decide*.

### A — safe to commit: our own derived output

| What | Where | Status |
| --- | --- | --- |
| Sealed v11 baseline: boundary fractions, scored metrics, gate verdict, data manifest, run record | `artifacts/evidence/sealed-baseline-v11/` | **added by this change** |
| Per-study evidence tables from earlier work | eight `artifacts/` carve-outs | already tracked, 180 files |
| Frozen configs, contracts, registry | `configs/`, `research/` | already tracked |
| Three arXiv preprints and the extracted paper text | `data/external/inputs/` | already tracked |

None of these contains a vendor price or yield value. They are model output,
summary statistics, hashes and row counts.

### B — regenerate instead: code and pinned hashes are tracked, the data is not

| What | Tracked route |
| --- | --- |
| The 7 canonical series in `data/external/` | `scripts/data/build_external_sources.py`, `build_sp500_tr.py`, `build_de_total_return.py`, with 17 pinned `INPUT_SHA256` values and 5 output hashes pinned in `configs/baselines/research-calibrated-v11.toml` |
| The per-run normalized series in `data/processed/<run>/` | the same builders; every output hash and row count is in `artifacts/evidence/sealed-baseline-v11/data-manifest.json` |
| Every heavy run output under `artifacts/` | the runners in `scripts/` and `src/adaptive_jump/`, against the sealed configs |

**The honest limit on B.** For the run outputs this works: given the data, the
code regenerates them. For the data itself it does not, because the 17 pinned
inputs cannot be shipped and, per `docs/data-provenance.md`, cannot be
re-downloaded dependably either. B is a *verification* route — rebuild your own
copy and compare hashes with ours — not a from-scratch reproduction route. This
repository does not reproduce its own data pipeline from a clean checkout, and
nothing here should be read as claiming it does.

### C — keep local

| What | Why |
| --- | --- |
| `data/external/*.csv`, `data/raw/`, `data/processed/` | the sealed contract sets `redistribute_raw_data = false`, `local_research_only = true` |
| `data/external/inputs/*.csv` (17 pinned raw inputs) | vendor downloads: Yahoo, Stooq, the Nikkei TR mirror, FRED-hosted IMF series, ECB, OECD, JST, Shiller |
| `data/external/fama-french/` | the frozen contract records `raw_redistribution = false` |
| `data/external/inputs/manual-verification/` | Investing.com and MSCI downloads used once as a cross-check |
| `data/processed/data_inventory.csv.gz` | leftover index of retired Kibot minute data — a paid vendor |
| `data/legacy-cold/` | cold storage for that same retired minute-era data |
| 5 paywalled PDFs in `paper/` (four SSRN, one Springer) | institutional access; terms do not grant redistribution |
| The Princeton dissertation and two author slide decks in `data/external/inputs/` | author artifacts behind a browser check or a personal Drive link; not data sources, and nothing in them feeds a run |
| 2.3 GB of `.npz`/`.npy` refit caches, plus daily state matrices, feature tables, trade ledgers and candidate-return tables | heavy and regenerable; no durable claim needs them directly |

### D — UNKNOWN

Redistribution terms have **not** been checked for any individual source. The
project-level `redistribute_raw_data = false` makes the question moot in
practice, but it is a policy decision, not a licence review, and the two are
easy to confuse later. Unchecked: Yahoo Finance, Stooq, Nikkei Inc., the
Investing.com mirror, MSCI, the IMF series FRED redistributes, the Ken French
data library, JST Macrohistory, OECD, ECB, and the Shiller dataset mirror on
GitHub.

Anything in D is treated as C until somebody actually reads the terms.

## One thing already tracked that this rule would not have allowed

Applying the classification above to what is already in the repository turns up
one conflict, found while writing this file. It predates this change and is not
repaired here.

`artifacts/lagged-capguard/01-us/trades-*.csv` — six tracked files, added
2026-08-07 by `d28d95e` under the `!artifacts/lagged-capguard/` carve-out — each
carry an `equity_simple` and a `cash_return` column holding the **full daily US
series, 13,787 rows from 1969-05-02 to 2023-12-29**. All six copies are
identical in those two columns. They are daily returns rather than index
levels, but a return series compounds back to the index: the growth factor they
imply, 217.08x, matches the 216.03x level ratio of the local
`data/external/us_equity_tr_sp500.csv` over the same window, which is the
official Yahoo `^SP500TR` index from 1988 spliced onto a `^GSPC`-plus-Shiller
reconstruction before that.

So the repository already publishes, in derived form, one of the six series the
sealed contract's `redistribute_raw_data = false` covers. Germany and Japan are
not affected, and no other tracked file carries a market series — this was
checked across every tracked `.csv`.

This is left for the owner to decide, for three reasons. Deleting the files
would remove tracked historical evidence. Stripping the two columns would
rewrite an existing evidence file and any hash recorded against it. And the
carve-out comment naming trades as committed evidence was a deliberate earlier
decision, not an accident of pattern matching. The options are: leave it and
record the exception, drop the two market columns from the six files, or drop
the ledgers and keep the study's small tables. **Status: UNRESOLVED.**

## What a fresh clone still cannot check

Listing these is the point of the file. Each is a real gap, not a formality.

**Durable claims whose evidence is local-only.** Most of
`docs/data-provenance.md` — the reconstruction correlations, the splice deltas,
the drift figures — was measured against series no clone has, and no derived
summary of those measurements is tracked. The claims are recorded there with
their sources; the measurements behind them are not independently inspectable
here.

**Historical audit receipts pointing into ignored runs.**
`docs/audit/frequency-ladder-001-audit.md`,
`docs/audit/heldout-delay-001-audit.md`,
`docs/audit/2026-08-06-ajm-ext-d1-receipt.md` and
`docs/audit/2026-08-08-baseline-reseal-v11-receipt.md` cite files under
`artifacts/frequency-ladder/`, `artifacts/penalty-frequency/`,
`artifacts/dense-menu/`, `artifacts/ajm-ext-001/` and
`artifacts/fixed-baselines/`, all local. These were left alone deliberately:
`docs/audit/` is history, not the main reading path, and bulk-copying old runs
into `artifacts/evidence/` is exactly what this directory is not for. If one of
those receipts is later promoted into a current claim, its table moves here
then.

**Paths cited in tracked files that exist nowhere at all.** Not a tracking
problem — these are stale citations, and no clone or laptop can open them:

- `artifacts/data-source-audit/20260712T012740Z/audit.json`, cited with a
  sha256 by the `[source_audit]` block of **all seven** baseline configs,
  including the sealed `research-calibrated-v11.toml`. Never tracked in git
  history, and absent locally.
- `data/raw/shu-replication-expanding-v9-3-20260729T081133Z/us_cash.csv`, cited
  in `docs/data-provenance.md` as the surviving copy of a manual download that
  was deleted in its favour.
- `artifacts/heldout-delay/`, `artifacts/data-audit/`,
  `artifacts/data-verification/`, `artifacts/dd-loss-scale-001/`,
  `artifacts/simple-jm-suite-001/`, `data/vintage`,
  `data/legacy-cold/legacy-minute-data.tar.zst`.

These are reported, not repaired. Repairing them means editing frozen contracts
and historical receipts, which `AGENTS.md` forbids doing to make old material
look current.

**The test suite does not pass from a clean clone.** Measured, not assumed: a
fresh clone of this branch runs 4 failed, 509 passed, 20 skipped — identical to
a fresh clone of `main`, so this predates the change. The 20 skips are correct
behaviour, each naming the local file it wanted. The 4 failures are not:
`tests/test_cli.py::test_fetch_cli_runs_complete_fixture_pipeline` dies on a
missing `data/external/us_equity_tr_sp500.csv`, and
`tests/test_heldout_delay_audit.py::test_delay_reaches_the_cross_validation`
(three delays) dies on a missing `us/features.csv` inside an ignored run
directory. Commit `5331d33` applied the skip-and-name fix to two other test
files; these two were missed. Until they are fixed, "the tests pass" is a
statement about the owner's machine.

**The manuscript's figures are not in the repository either.**
`paper/manuscript.tex` pulls eight `\includegraphics` files from
`artifacts/reports/`, `artifacts/holdout-2026-001/` and
`artifacts/separation-turnover-001/`. `reports/` is ignored globally, the other
two directories are ignored with the rest of `artifacts/`, and the two figures
spot-checked are absent from the owner's disk as well. The manuscript does not
build from a clean checkout.

## Adding evidence later

1. Is the number durable — does it appear in `README.md`, `CURRENT.md`, `docs/`
   or the manuscript? If not, leave the file local and cite the run.
2. Is the file our own code's derived output, with no vendor values in it, and
   small — kilobytes, not megabytes? If not, it belongs in C or B.
3. Copy it byte for byte into `artifacts/evidence/<study>/`, and add a row to
   `artifacts/evidence/README.md` giving its source run, its sha256 and what it
   is. Do not recompute, re-round or re-fit to produce it.
4. Do not add another `.gitignore` carve-out. `!artifacts/evidence/` already
   covers it.
