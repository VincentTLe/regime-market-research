# jp-causal-rebuild-001 — receipt (2026-08-28)

This is the record of one correction. Registry row `jp-causal-rebuild-001`
was frozen at 2026-08-28T01:52:35Z, before the rerun started. (A registry row
records, before the run starts, what will be measured. FROZEN means that list
was locked at the stated time.) The correction changes the Japanese equity
input to address AGENTS.md rule 1 (no future data); whether the prior-year JST
yield fully satisfies rule 1 is discussed under "What could still be wrong".
It is not a tuning step. The same AI assistant that made the change wrote this
receipt; nothing here is an independent check.

## What you need to understand

- The Japanese input had a look-ahead problem. "Look-ahead" (or "future
  information") means a number used on a given day that was not yet knowable
  on that day. The Nikkei total-return series (price change plus dividends, as
  an investor would actually have earned it) that the v10 and v11 baselines
  read (`jp_equity_tr.csv`) set two dividend accruals with numbers from
  *after* the day they were applied to. (A baseline is a sealed reference run
  that later results are compared against.) A "dividend accrual" is the small
  daily amount added to a price index to stand in for the dividends investors
  would have received, so the series behaves like a total-return series. The
  two problems: (1) The 2020-07-09..2022-05-31 bridge across a hole (a stretch
  of missing days) in the project's downloaded copy of the official Nikkei
  total-return index was set using the official value at the *end* of the
  hole. A "bridge" is a stretch of days where the official series is missing
  and the series is filled in by walking a price index forward and adding an
  accrual. (2) Each pre-2011 day used its own calendar year's full-year JST
  dividend yield (JST is the Jorda-Schularick-Taylor Macrohistory database,
  the source of the yearly yields). Decisions in 1990-2011 and 2020-2022
  therefore read returns that depended on data up to one and two years later.
- The fix builds a second series, `jp_equity_tr_causal.csv`, from the same
  pinned inputs ("pinned" means the input files are fixed by their hash), with
  accruals that avoid the current period's figure: before 2011, the prior
  year's JST yield; across the hole, the accrual actually observed in the year
  before the hole. When JST's prior-year value became public was not
  established. Then it reruns the fixed-JM baseline (the fixed jump model that
  the project compares against: it labels each day as being in one of a few
  market states and pays a penalty every time the label switches) with
  **nothing else changed**. That
  rerun is the project's comparator from now on — the run every later result
  is measured against — by a rule written down before it was scored.
- The two input series differ very little: at most 5.1e-5 (about 0.00005) per
  session in log return (a "session" is one trading day; a log return is the
  natural log of today's level over yesterday's) — roughly one three-hundredth
  of the Japanese daily standard deviation of 0.0147 over 1990-2023. What that
  small change did to the model's day-by-day state labels and to the strategy
  is the table below.
- Because the rerun recomputes everything, the US and German outputs double as
  a determinism check (does the same code on the same input give the same
  output?): their inputs are byte-identical, so their outputs should be too.

## What changed

- The data builder gained a second Japanese series.
  `scripts/data/build_external_sources.py` has two new functions,
  `jp_causal_total_return()` and `build_jp_total_return_causal()`, which write
  `jp_equity_tr_causal.csv` (14,507 sessions, 1965-01-05..2023-12-29; sha256
  `d263e8bf4d8002ee3fad7e5f319218daeafcc21fc5ae80331d627cf871d0eb27`). A
  sha256 is a fingerprint of a file's exact bytes; two files with the same
  sha256 have the same content. The new series follows three rules. (1) A day
  before the official index begins (2011-12-19) in calendar year y accrues JST
  `eq_dp[y-1]/252`, that is, the prior year's yield spread over 252 sessions.
  (2) The hole is bridged forward along the Nikkei 225 price index (`^N225`)
  with the "trailing accrual", meaning the accrual actually observed over the
  252 official sessions ending 2020-07-09 (0.021775 log per year, against the
  0.017730 the old bridge took from the 2022 endpoint). (3) The official
  series after the hole is multiplied by 1.006144 so the level continues from
  the bridge; official returns are unchanged.
- `configs/baselines/research-calibrated-reconstruction-v11.toml`
  (config_sha256 `3448b85e0fecb8b4…`; see "Executed three times" below).
  `diff` against `research-calibrated-v11.toml` (12 lines removed, 31 added):
  `config_id`, `frozen_at_utc`, a 14-line header comment, the Japanese
  paragraph and builder-path line of `[data_policy].splice_documentation`, and
  the Japanese equity `file_path` / `sha256` / `construction` / deviation text.
  The candidate lambda lists (grids), n_init=60 (the number of optimizer
  starting points per fit), the features (the inputs computed from returns
  that the models read), the HMM protocol (HMM is the hidden Markov model, the
  comparison model), the monthly rule that selects a lambda, the metric
  definitions, and the US and DE data pins: byte-identical.
- Four unit tests on synthetic (made-up) data in `tests/test_series_splices.py`:
  changing the value at the end of the hole leaves every bridge return
  unchanged; the bridge accrual equals the trailing realised one; the session
  after the hole carries the official return; pre-official year y uses the
  year y-1 yield.
- `scripts/diagnostics/compare_jp_causal_rebuild.py`: the script that produced
  the measurement below. As a sanity check it was run on the sealed run (the
  old, locked v11 run) compared against itself, and every difference came out
  zero, as it must.

## What did not change

`jp_equity_tr.csv` (sha256 `e8717952…`) and `research-calibrated-v11.toml`
are untouched. The data builder (the script that produces the input files)
was rerun in an isolated worktree, a separate checkout of the repository used
so the working copy is not disturbed. It could not start from an empty output
folder, because its German step reads `de_cash_ladder.csv` before `main()`
writes it. With that one file copied in first, it reproduced all seven outputs
byte-for-byte on this machine from the local pinned inputs on 2026-08-28. All
five input files whose hashes the v11 config pins matched (5/5). Whether each
older sealed config's pins are among those seven was not re-checked here. The
US and German rebuilt series have the same kind of look-ahead — each spreads a
whole month's (US, Shiller data) or whole year's (Germany, JST) dividend
figure across the days of that same period — but both end before 1988; every
scored decision is 1990 or later, so they are recorded in
`docs/data-provenance.md`, not changed.

## The rerun

- The input-preparation step (an "acquisition") was re-run as
  `calibrated-reconstruction-v11-20260828T033808Z`. The FRED DTB3 download
  (the 3-month US Treasury bill rate from the St. Louis Fed's data service)
  and every non-Japanese raw and processed file are byte-identical to the
  sealed v11 acquisition, checked file by file.
- Run `fixed-baselines-3448b85e0fec-97ee407c64ce-7130da99b50b`, executed in
  a git worktree at commit `7130da9`. Local-only under `artifacts/`; its
  inputs are published as `data/snapshots/calibrated-reconstruction-v11/`.
- **Executed three times, same results.** Two findings from owner/Codex review (Codex is a second AI coding tool used
  for review) changed the config
  file after it had already been run. A config change changes the run id, so
  the study was re-executed each time. The alternative would have left a run
  whose lock file (the copy of the settings a run records as what it actually
  ran with) no longer matched the config file. (1)
  `fixed-baselines-c4b7d476e5a4-…` (01:54–02:35 UTC, commit `67cf521`):
  `frozen_at_utc` was a rounded `00:00:00Z`, earlier than the registry row
  that actually froze the measurement list (01:52:35Z); set to that timestamp.
  (2) `fixed-baselines-d8bdf14ff660-…` (02:51–03:32 UTC, commit `df2e0f7`):
  the config's `[data_policy].splice_documentation` still described the
  superseded Japanese construction; rewritten to describe the causal one.
  (3) the run above. Between consecutive executions, 123 of 125 inventory
  files are hash-identical (an "inventory file" is one of the 125 files the
  run writes to its output folder and hashes); only `config.lock.toml` and
  `data-manifest.json` differ. Every number below is from the third execution
  and is identical in the first two.

## What was measured (registry list a–g), old = v11-ninit60, new = this run

Here "old" is `v11-ninit60`, the previous comparator run, and "new" is the
run described above. The two run directories live only on the owner's machine
(`artifacts/` is gitignored). Everything needed to regenerate them is tracked
— the two configs, the inputs under `data/snapshots/`, and the comparison
script — at about 41 minutes per run.

All counts are days on which both runs define a value. The Japanese regime
path (the model's day-by-day label of which market state it is in) is defined
on 10,448 days for the HMM and 10,342 for the JM, starting once the model has
its first full 3000 sessions of history to fit on; the scored strategy is
defined on 8,347 days of 1990-2023. HMM is the hidden Markov model, the
comparison model; JM is the jump model.

**(a) Markets whose input did not change.** US and DE: 40 of 40 inventory
files hash-identical to the sealed run in each market; 0 of 54 US/DE metric
cells moved. Read this as: the pipeline is deterministic on this machine,
and the Japanese input is the only thing that differs between the two runs
(same code, same seeds, same settings).

**(b) Japanese HMM.** The online HMM state (the state label computed each day
using only data up to that day) differs on 2 of 10,448 days. The HMM signal
differs on 5 / 6 / 5 of 8,452 days at delays 1 / 5 / 10. (The "signal" is the
model's decision on the day it is made; "delay" is the signal-lag setting —
the position is actually held delay+1 sessions after the signal, as (e′)
below describes.)

**(c) Japanese jump model, per candidate lambda** (days on which the fitted
state differs, out of 10,342). Lambda is the jump model's penalty on
switching state; the monthly rule picks one lambda from this list each month.
The table shows, for each candidate lambda, how many of the 10,342 days got a
different fitted state in the new run than in the old one:

| lambda | 1.93 | 20 | 25 | 26.83 | 40 | 51.79 | 220 |
|---|---|---|---|---|---|---|---|
| days differ | 95 | 144 | 64 | 57 | 47 | 19 | 10 |

**(d) Which lambda the monthly rule picked** (months out of 409 in which the
old and new runs picked a different lambda):
delay 1: 92 · delay 5: 113 · delay 10: 65.

**(e) Selected fixed-JM signal, unshifted** (the model's decision on the day
it is made, before the trading delay is applied; days out of 8,347 on which
the signal differs): delay 1: 70 · delay 5: 237 · delay 10: 233.

**(e′) Position actually held on trade dates** — this is the held position,
not the signal. The backtest turns a signal into a position by shifting it
forward delay+1 sessions (`backtest.apply_signal`); these counts are read from
the trade files (`jp/trades/*.csv`). Out of 8,336 trade dates, the held
position differs on 70 / 237 / 233 days for fixed_jm and 5 / 6 / 5 days for
hmm, at delays 1 / 5 / 10. (Added after a Codex review pointed out that (e)
was labelled as the traded position; the counts coincide here.)

**(f) Japanese strategy metrics, 1990-2023, 10 bp one-way cost:** Sharpe is
the annualised average excess return over cash divided by the strategy's
volatility; max drawdown is the largest peak-to-trough loss; turnover is
annualised, per the `[metrics]` definitions in
the config. Each cell shows the old run's value, then the new run's:

| model | delay | Sharpe old → new | max drawdown old → new | turnover old → new |
|---|---|---|---|---|
| fixed_jm | 1 | 0.2938 → 0.2943 (+0.0004) | −44.02% → −43.56% | 0.756 → 0.786 |
| fixed_jm | 5 | 0.2458 → 0.2485 (+0.0026) | −52.23% → −51.23% | 0.998 → 1.028 |
| fixed_jm | 10 | 0.2320 → 0.2077 (−0.0244) | −58.53% → −61.02% | 1.088 → 0.998 |
| hmm | 1 | 0.1771 → 0.1734 (−0.0037) | −51.73% → −51.86% | 3.144 → 3.114 |
| hmm | 5 | 0.1446 → 0.1321 (−0.0125) | −52.61% → −52.75% | 3.053 → 3.083 |
| hmm | 10 | 0.0943 → 0.0969 (+0.0026) | −55.30% → −55.37% | 3.779 → 3.718 |
| buy_and_hold | any | 0.1383 → 0.1371 (−0.0012) | −77.33% → −77.67% | 0 |

**(g) Directional gate** (`claim.json`; the gate is a pass/fail check,
recorded in `claim.json`, of whether the result points the claimed way):
passed in both runs, all three markets.

### What we can say

- On the primary delay (1), the Japanese fixed-JM Sharpe is unchanged to
  three decimals (0.294) and the max drawdown improves by 0.47 percentage
  points (−44.02% → −43.56%); the conclusion "fixed JM beats buy-and-hold and
  the HMM in Japan at delay 1" is the same on the corrected input.
- The buy-and-hold row moves by −0.0012 of Sharpe: that is the size of the
  input change itself, with no model in between.
- An input change of that size, passed through the n_init=60 optimizer,
  still changed which lambda the monthly rule selected in 92 of 409 months at
  delay 1, and moved the delay-10 fixed-JM Sharpe by −0.024 — a measured
  sensitivity of the selection rule and of the delay-10 cell, on this market,
  this grid, this run pair. How much of that is the input and how much is the
  optimizer landing elsewhere is not separated (next section).

### What we cannot say

- Whether the state and lambda changes come from the input itself or from
  the optimizer landing in a different basin under a slightly different
  input (that is, the fit settling on a different answer because its starting
  point now leads somewhere else): 60 optimizer starting points is already
  known not to guarantee that a fit found its best answer (`CURRENT.md`).
  Separating the two would need both inputs refit under several different
  sets of random starting seeds (`random_state` families), as the
  `optimizer-fidelity-characterization` study did for one input. UNKNOWN, not
  done.
- Anything about the US or Germany beyond "unchanged".
- Which of the two Japanese results is closer to the authors'. Neither
  input is theirs.

## What could still be wrong

- The trailing-252-session accrual is one defensible causal rule among
  several. It was chosen before any result was seen and is not tuned, but it
  is still a choice the paper does not make; it belongs in
  `docs/unspecified-choices.md` if the Japanese reconstruction is ever
  re-opened.
- **The prior-year JST yield and rule 1 (raised as a high-priority (P1)
  finding by Codex on PR #31).** Rule 1 asks whether the *information* existed
  on the day, not when a database printed it. JST Macrohistory is a
  compilation first released in 2017, so no lag of any length makes its
  publication date precede 1990; by that reading every JST-based
  reconstruction in this repository, including the US and German ones, would
  be inadmissible. The reading used here: the dividends paid on Nikkei
  constituents during year y−1 and the year-end price were public facts on the
  first session of year y, so an accrual equal to their ratio uses no
  information generated after the day. Whether JST's figure is built only from
  year y−1 data was checked against the JST documentation (2026-08-28:
  `JST_documentationR6.pdf` and `JST_RORE_Documentation_R6.pdf`, both
  downloaded from https://www.macrohistory.net/database/ — external
  documents, not in this repository):
  the codebook (the database's own documentation of each column) defines the
  dividend yield `eq_dp[t] = dividend[t]/p[t]` (the year's dividends divided
  by the year's price) and the total return
  `eq_tr[t] = (p[t]+d[t])/p[t−1] − 1` (price plus dividend, over last year's
  price); for Japan 1952–2015 the appendix's Table 27 sources capital gain and
  dividend return from the Bureau of Statistics Japan, tables 14-25-a/b (Tokyo
  Stock Exchange 1st and 2nd sections), plus Fujino and Akiyama (1977)
  stock-operation gains up to 1975. So JST's value for year y−1 is an annual
  statistic of year y−1 data (prices and dividends; through 1975 also the
  Fujino–Akiyama operations term). Two limits remain: the codebook does not
  state whether `p[t]` is the year-end or the annual-average price, and the
  underlying statistic covers the whole Tokyo exchange, not the 225 Nikkei
  constituents — a proxy this reconstruction has always used. The compiled
  yearbook figure for year y−1 would typically be printed during year y; the
  argument here rests on the underlying prices and dividends, not on the
  yearbook. Checked on the Japan file
  (`data/external/inputs/jst_japan_eq.csv`, gitignored — local-only): the
  three columns agree with each other the way the codebook says they should —
  total return equals capital gain plus dividend yield grown by the capital
  gain, `eq_tr = eq_capgain + eq_dp·(1+eq_capgain)` — to within 3e-8
  (effectively exactly) for 1976–2020. The identity fails only through 1975,
  with a mismatch of up to 2.2 percentage points, exactly the years the
  appendix says carry the extra Fujino–Akiyama stock-operation term. So the
  file behaves as the codebook describes.
- The level constant 1.006144 after 2022-05-31 means the series is no longer
  the official index level from then on. Returns, which are all the model and
  the backtest use, are the official ones.
- Nothing here addresses the other open problems of the comparator: the
  candidate lambda lists were chosen to match the paper's published numbers,
  the German list fails its own eligibility rule at n_init=60 (the rule that
  chose the candidate lists no longer accepts the German one when refit with
  60 starting points), and no market's fits are known to be converged
  (`CURRENT.md`).

## What the checks do NOT prove

The unit tests prove the new construction does not read the end of the hole
or the current year's yield on synthetic data. The rebuild proves the builder
is deterministic on this machine. The comparison proves how far the sealed
outputs moved, and nothing about whether either set of outputs is right. The
`verify` command replays the run's own arithmetic. None of this is an
independent check of the science, and the person who wrote the fix wrote this
receipt.

## Technical details

- Old run `fixed-baselines-5b12efa2948c-d57a9e7d9c07-b277dea3beb3` (sealed
  2026-08-08). New run `fixed-baselines-3448b85e0fec-97ee407c64ce-7130da99b50b`,
  03:38:23 → 04:19:34 UTC 2026-08-28 (41 min), worktree at commit `7130da9`,
  python 3.12, the repo `.venv` with the `data` extra installed
  (`uv sync --extra data --inexact`, requests 2.34.2 as in the sealed run).
- `adaptive-jump verify --run …`: status complete, 125 inventory files, 27
  metric rows, 18 boundary rows, maximum metric absolute difference on replay
  3.80e-14.
- Comparison: `python scripts/diagnostics/compare_jp_causal_rebuild.py OLD NEW`
  → `artifacts/jp-causal-rebuild/summary.{csv,md}` (local-only; the numbers
  above are copied from it).
- Isolated rebuild (`scripts/data/build_external_sources.py` in a worktree
  with the pinned inputs and `de_cash_ladder.csv` copied in): all seven
  outputs byte-identical to the live files; 5/5 v11 pins matched. The builder
  cannot run from an empty output folder because
  `build_de_total_return.validate` reads `de_cash_ladder.csv` before `main()`
  writes it — a pre-existing ordering defect, worked around by copying that
  file in first; not fixed here.
- `jp_equity_tr_causal.csv` construction constants printed by the builder:
  first_official 2011-12-19, hole 2020-07-09 → 2022-05-31, 460 bridge
  sessions, trailing accrual 0.021775 log/yr, post-hole level factor
  1.006144.
- Series delta (`jp_equity_tr.csv` vs `jp_equity_tr_causal.csv`, log
  returns per session): pre-2011 max 5.14e-5 (all 11,561 sessions change),
  bridge 1.34e-5 (all 459), after 2022-05-31 zero; 5,861 of 8,346 scored
  sessions change; mean drift 1990-2023 −0.028 percentage points per year.
- Tests and lint on the branch: see the PR body.
