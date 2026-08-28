# jp-causal-rebuild-001 — receipt (2026-08-28)

Registry row `jp-causal-rebuild-001` (FROZEN 2026-08-28T01:52:35Z, before the
rerun started). A correction of the Japanese equity input under AGENTS.md
rule 1, not a tuning step. Written by the same AI assistant that made the
change; nothing here is an independent check.

## What you need to understand

- The Nikkei total-return series the v10 and v11 baselines read (`jp_equity_tr.csv`)
  set two dividend accruals with numbers from *after* the day they were applied
  to. The 2020-07-09..2022-05-31 bridge across a hole in the official mirror
  was calibrated on the official value at the *end* of the hole; each
  pre-2011 day used its own calendar year's full-year JST dividend yield.
  Decisions in 1990-2011 and 2020-2022 therefore read returns that depended on
  data up to one and two years later.
- The fix builds a second series, `jp_equity_tr_causal.csv`, from the same
  pinned inputs with accruals that avoid the current period's figure (the
  prior year's JST yield before 2011; the accrual realised before the hole
  across it — when JST's prior-year value became public was not
  established), and reruns the
  fixed-JM baseline with **nothing else changed**. That rerun is the project's
  comparator from now on, by a rule written down before it was scored.
- The two input series differ very little: at most 5.1e-5 per session in log
  return, against a Japanese daily standard deviation of 0.0147 over
  1990-2023. What that did to the fitted states and the strategy is the table
  below.
- Because the rerun recomputes everything, the US and German outputs double as
  a determinism check: their inputs are byte-identical, so their outputs
  should be too.

## What changed

- `scripts/data/build_external_sources.py`: new `jp_causal_total_return()` /
  `build_jp_total_return_causal()`, writing `jp_equity_tr_causal.csv`
  (sha256 `d263e8bf4d8002ee3fad7e5f319218daeafcc21fc5ae80331d627cf871d0eb27`,
  14,507 sessions 1965-01-05..2023-12-29). Rules: a pre-official day in
  calendar year y accrues JST `eq_dp[y-1]/252`; the hole is bridged forward
  along the `^N225` price path with the accrual realised over the 252
  official sessions ending 2020-07-09 (0.021775 log per year, against the
  0.017730 the old bridge took from the 2022 endpoint); the official series
  after the hole is multiplied by 1.006144 so the level continues from the
  bridge — official returns unchanged.
- `configs/baselines/research-calibrated-reconstruction-v11.toml`
  (config_sha256 `c4b7d476e5a444ad8cb763dcdf67651ab1c3aadd80f0ead7bcbb846ad1f7578f`).
  `diff` against `research-calibrated-v11.toml`: `config_id`,
  `frozen_at_utc`, a 13-line header comment, and the Japanese equity
  `file_path` / `sha256` / `construction` / deviation text. Grids, n_init=60,
  features, HMM protocol, selection rule, metric definitions, US and DE data
  pins: byte-identical.
- Four unit tests on synthetic data in `tests/test_series_splices.py`:
  perturbing the value at the end of the hole leaves every bridge return
  unchanged; the bridge accrual equals the trailing realised one; the session
  after the hole carries the official return; pre-official year y uses the
  year y-1 yield.
- `scripts/diagnostics/compare_jp_causal_rebuild.py`: the measurement below.
  Self-checked on the sealed run against itself: every delta zero.

## What did not change

`jp_equity_tr.csv` (sha256 `e8717952…`) and `research-calibrated-v11.toml`
are untouched. In an isolated worktree the builder could not start from an
empty output folder (its German step reads `de_cash_ladder.csv` before
`main()` writes it); with that one file copied in first, it reproduced all
seven outputs byte-for-byte (5/5 v11 pins matched). Whether each older sealed
config's pins are among those seven was not re-checked here. The US and German reconstructions also spread in-period dividend
figures (monthly Shiller, annual JST) but end before 1988; every scored
decision is 1990 or later, so they are recorded in `docs/data-provenance.md`,
not changed.

## The rerun

- Acquisition `calibrated-reconstruction-v11-20260828T015445Z`; the FRED DTB3
  download and every non-Japanese raw/processed file are byte-identical to the
  sealed v11 acquisition (checked file by file).
- Run `fixed-baselines-c4b7d476e5a4-e6e7e8302ad3-67cf52166219`, executed in
  a git worktree at commit `67cf521`. Local-only under `artifacts/`; its
  inputs are published as `data/snapshots/calibrated-reconstruction-v11/`.

## What was measured (registry list a–g), old = v11-ninit60, new = this run

All counts are days on which both runs define a value; the Japanese
regime path is defined on 10,448 (HMM) or 10,342 (JM) days from the first
complete 3000-session window, and the scored strategy on 8,347 days of
1990-2023.

**(a) Markets whose input did not change.** US and DE: 40 of 40 inventory
files hash-identical to the sealed run in each market; 0 of 54 US/DE metric
cells moved. Read this as: the pipeline is deterministic on this machine,
and the Japanese input is the only thing that differs between the two runs
(same code, same seeds, same settings).

**(b) Japanese HMM.** The online HMM state differs on 2 of 10,448 days. The
HMM signal differs on 5 / 6 / 5 of 8,452 days at delays 1 / 5 / 10.

**(c) Japanese jump model, per candidate lambda** (days on which the fitted
state differs, out of 10,342):

| lambda | 1.93 | 20 | 25 | 26.83 | 40 | 51.79 | 220 |
|---|---|---|---|---|---|---|---|
| days differ | 95 | 144 | 64 | 57 | 47 | 19 | 10 |

**(d) Which lambda the monthly rule picked** (months out of 409):
delay 1: 92 · delay 5: 113 · delay 10: 65.

**(e) Traded fixed-JM position** (days out of 8,347): delay 1: 70 ·
delay 5: 237 · delay 10: 233.

**(f) Japanese strategy metrics, 1990-2023, 10 bp one-way cost:**

| model | delay | Sharpe old → new | max drawdown old → new | turnover old → new |
|---|---|---|---|---|
| fixed_jm | 1 | 0.2938 → 0.2943 (+0.0004) | −44.02% → −43.56% | 0.756 → 0.786 |
| fixed_jm | 5 | 0.2458 → 0.2485 (+0.0026) | −52.23% → −51.23% | 0.998 → 1.028 |
| fixed_jm | 10 | 0.2320 → 0.2077 (−0.0244) | −58.53% → −61.02% | 1.088 → 0.998 |
| hmm | 1 | 0.1771 → 0.1734 (−0.0037) | −51.73% → −51.86% | 3.144 → 3.114 |
| hmm | 5 | 0.1446 → 0.1321 (−0.0125) | −52.61% → −52.75% | 3.053 → 3.083 |
| hmm | 10 | 0.0943 → 0.0969 (+0.0026) | −55.30% → −55.37% | 3.779 → 3.718 |
| buy_and_hold | any | 0.1383 → 0.1371 (−0.0012) | −77.33% → −77.67% | 0 |

**(g) Directional gate** (`claim.json`): passed in both runs, all three
markets.

### What we can say

- On the primary delay (1), the Japanese fixed-JM Sharpe is unchanged to
  three decimals (0.294) and the drawdown improves by 0.5 points; the
  conclusion "fixed JM beats buy-and-hold and the HMM in Japan at delay 1"
  is the same on the corrected input.
- The buy-and-hold row moves by −0.0012 of Sharpe: that is the size of the
  input change itself, with no model in between.
- An input change of that size still changed which lambda the monthly rule
  selected in 92 of 409 months at delay 1, and moved the delay-10 fixed-JM
  Sharpe by −0.024 — a measured sensitivity of the selection rule and of
  the delay-10 cell, on this market, this grid, this run pair.

### What we cannot say

- Whether the state and lambda changes come from the input itself or from
  the optimizer landing in a different basin under a slightly different
  input: n_init=60 is already known not to be a convergence certificate
  (`CURRENT.md`). Separating the two would need the two inputs refit under
  several `random_state` families, as `optimizer-fidelity-characterization`
  did for one input. UNKNOWN, not done.
- Anything about the US or Germany beyond "unchanged".
- Which of the two Japanese results is closer to the authors'. Neither
  input is theirs.

## What could still be wrong

- The trailing-252-session accrual is one defensible causal rule among
  several (a prior-year JST yield would be another). It was chosen before any
  result was seen and is not tuned, but it is still a choice the paper does
  not make; it belongs in `docs/unspecified-choices.md` if the Japanese
  reconstruction is ever re-opened.
- The level constant 1.006144 after 2022-05-31 means the series is no longer
  the official index level from then on. Returns, which are all the model and
  the backtest use, are the official ones.
- Nothing here addresses the other open problems of the comparator: the
  lambda grids are fitted to published output, the German grid fails its own
  eligibility rule at n_init=60, and no market's fits are known to be
  converged (`CURRENT.md`).

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
  2026-08-08). New run `fixed-baselines-c4b7d476e5a4-e6e7e8302ad3-67cf52166219`,
  01:54:48 → 02:35:36 UTC 2026-08-28 (41 min), worktree at commit `67cf521`,
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
  outputs byte-identical to the live files; 5/5 v11 pins matched. The builder cannot run from an empty
  output folder because `build_de_total_return.validate` reads
  `de_cash_ladder.csv` before `main()` writes it — a pre-existing ordering
  defect, worked around by copying that file in first; not fixed here.
- `jp_equity_tr_causal.csv` construction constants printed by the builder:
  first_official 2011-12-19, hole 2020-07-09 → 2022-05-31, 460 bridge
  sessions, trailing accrual 0.021775 log/yr, post-hole level factor
  1.006144.
- Series delta (`jp_equity_tr.csv` vs `jp_equity_tr_causal.csv`, log
  returns per session): pre-2011 max 5.14e-5 (all 11,561 sessions change),
  bridge 1.34e-5 (all 459), after 2022-05-31 zero; 5,861 of 8,346 scored
  sessions change; mean drift 1990-2023 −0.028 pp/yr.
- Tests and lint on the branch: see the PR body.
