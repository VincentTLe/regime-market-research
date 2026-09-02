# Current Research State

Last updated: 2026-08-28

## Where the project stands

The project is not currently trying to add another Jump Model variant.

The main problem is simpler:

> Can we trust the existing pipeline and the results already produced?

A large part of the repository was built and checked with AI assistance.
Several later reviews found real problems in data handling, baseline
selection, optimizer behavior, experiment interpretation, and tests. Because
of that, old results are not being treated as final until the core path — the
chain of steps that turns input data into the strategy's profit and loss,
listed under "What we are doing now" — has been checked by someone who
did not build it.

## What is reasonably clear

- The project studies a two-state Jump Model used for a simple equity/cash
  strategy. (A two-state Jump Model assigns each day to one of two market
  states; the strategy switches between equities and cash according to that
  state.)
- The public-data reconstruction — the project's rebuild of the model from
  public data — is not an exact reproduction of the paper it follows (Shu et
  al.); some of the authors' source data and implementation choices are
  unavailable.
- Several model changes have been tested.
- Most did not produce a clear, robust improvement.
- Some experiments produced interesting behavior, but those results still
  depend on a pipeline that still needs a clean check by someone who did not
  build it.

## What everything is compared against

**What the comparator is.** The comparator is the fixed set of numbers every
new idea is measured against. Here it is the sealed
**calibrated-reconstruction-v11** fixed Jump Model, set up in
`configs/baselines/research-calibrated-reconstruction-v11.toml`
(run `fixed-baselines-3448b85e0fec-97ee407c64ce-7130da99b50b`, 2026-08-28).

*Sealed* means its settings and its fitted results are frozen and saved, so
every new idea is measured against the same numbers instead of a freshly
refitted target. Sealed does not mean the comparator is correct, and it does
not mean it is neutral.

*Calibrated reconstruction* means the baseline was rebuilt from public data,
and its lambda grid was chosen by searching for the grid whose output lands
closest to numbers the paper published (the two-stage search described
below). Closest does not mean equal: in Germany and Japan no grid reaches all
of the published cells. It is not a replication of the authors' model: some
source data and implementation choices are unavailable, and its lambda grid
was fitted to the paper's published output rather than taken from the paper.

**How the lambda grid was chosen, and why that matters.** Lambda is the
Jump Model's jump penalty: a setting that, the larger it is, makes the fitted
path switch between its two states less readily. The lambda grid is the short
list of lambda values the selection rule chooses from each refit month. The
paper never publishes its lambda grid, so ours was searched for, in two
stages, against numbers the authors did publish.

The first stage was exhaustive. Every subset of size 2 to 8 that can be drawn
from a fixed 29-value lambda menu — 6,474,511 grids in all — was scored
against the performance figures the paper prints in its Table 4 and Table 5.
What survived were the grids landing closest to those published cells. There
are fourteen published cells to reach. In the US, 36,657 grids reach all
fourteen. No German or Japanese grid reaches all fourteen, so for those
markets the survivors are the grids reaching the best available thirteen out
of fourteen: 366 grids in Germany and 2,948 in Japan.

The second stage ranked those survivors — all of them, not a sample. Each
grid produces its own daily regime path: the day-by-day sequence of which
state the model says the market is in. The grids were ranked by how closely
that path agrees with the state sequence the authors printed in their
Figure 5. The top-ranked grid in each market is the grid the sealed v11
baseline uses.

What this means: the comparator is fitted to published output at both
stages, first to the published tables and then to the published figure. So
"the new model beats the baseline" is a statement about that fitted
reference, not about the authors' model. Evidence:
`docs/audit/2026-07-31-jm-exhaustive-search.md`,
`docs/audit/2026-07-31-jm-per-market-grids.md`,
`docs/audit/2026-08-07-grid-selection-rule-001-receipt.md`,
`artifacts/grid-selection-rule/01-rule/summary.csv`.

The optimizer is the routine that fits the model to the data. Optimizer
restarts, set by `n_init`, are the number of different starting points it
tries; it keeps the run with the best fit objective, the score the fitting
routine is trying to optimise. More restarts give more chances to find a
better fit but do not guarantee the best one. The comparator's restarts are
not known to reach the best fit (the `n_init` finding below). So "sealed"
means frozen, not converged — converged would mean the optimizer had found
the best fit it can.

**What changed from the previous baseline.** The comparator is the
v11-ninit60 baseline with one input corrected. The problem was in the
Japanese total-return series that v11 read (a total-return series is a price
series with dividend income added back in; the dividend accrual is the
dividend amount credited to each day). That series set its dividend accruals
from information after the day they applied to. Across 2020-2022, where the
series is bridged over a gap (the "hole"; see the receipt), it used a value
two years ahead; before 2011 it used each year's own full-year yield. That
breaks the no-future-data rule for decisions in 1990-2011 and 2020-2022. The
corrected series uses the prior year's dividend yield before 2011 and, across
the bridge, the accrual realised before the hole — no accrual is set from a
value dated after the day it applies to.

Why the prior year's figure does not use future information: JST (the
dataset the yearly yield is taken from; see the receipt) defines its yearly
yield in its own documentation as that year's dividends over that year's
price, sourced for Japan from the Bureau of Statistics' annual Tokyo Stock
Exchange tables. So the previous year's figure (year y−1) contains only the
previous year's (year y−1) information. Two caveats. First, the
documentation does not say whether the price in that ratio is the year-end
price or the annual average. Second, the figure covers the whole exchange,
not the 225 Nikkei names (see the receipt).

What was held fixed: the grids, optimizer restarts, features (the input
variables the model is fitted on), HMM (hidden Markov model), selection rule,
metric definitions and the US and German data pins (the records that fix
which input files are read) are byte-identical to v11. The config also
differs in the text describing how the Japanese series is spliced together
and in a header comment.

What the rerun on the corrected input showed:

- In the US and Germany the outputs did not change at all: all 40 of 40
  output files per market are identical, and 0 of 54 metric values in the
  comparison table changed.
- In Japan the delay-1 Sharpe ratio of the fixed Jump Model is 0.294 either
  way. (Sharpe is a risk-adjusted return measure, average return relative to
  its variability; the exact formula this run uses is `annualized_excess_sharpe` in
  `src/adaptive_jump/backtest.py`.
  "Delay-1" and "delay-10" are two of the delay settings the receipt reports
  results at; this file quotes only those two.)
- In Japan the monthly lambda choice changed in 92 of 409 months, and the
  delay-10 Sharpe fell by 0.024.

Where those counts come from, and what they do not prove: the counts come
from run directories kept only on the owner's machine (local-only), so a
fresh checkout cannot inspect them. The inputs, configs and comparison script
are in Git, so both runs can be regenerated (about 41 minutes each). The
results were reported as measured, with no pass/fail bar set in advance, and
the new run became the comparator by a rule written before it was scored
(`docs/audit/2026-08-28-jp-causal-rebuild-receipt.md`, registry
`jp-causal-rebuild-001`). The exact bytes each sealed run read are published
under `data/snapshots/`. The sealed configs still contain the line
`redistribute_raw_data = false`; that line records the data-sharing policy in
force when they were sealed, not current practice.

**Frozen.** The owner's decision of 2026-08-27: this comparator is a
calibrated reconstruction, not a replication, and it stops here. No change to
the lambda grids, the feature standardizer, the refit months, the HMM grid or
the number of optimizer restarts will be made to move its numbers toward the
paper's. Each of those is a methodology change, and any future one needs its
own frozen question first — a research question written down and fixed
before the run is made. Bugs — code that does something other than what the
documents say, or data that uses information it could not have had — are
still fixed.

`configs/baselines/legacy/` holds older versions (v11-ninit60, v10, v9.4, and
earlier). v11-ninit60 differs from the comparator only in the Japanese input;
the older ones also use different lambda grids and optimizer settings. They
are history, not the current comparator, and auditing one of them answers a
different question.

**Known problem, and it is not only German.** The grid-choosing rule
described above was rerun using the 60 optimizer restarts the sealed baseline
actually runs at, and it then picks none of the three adopted grids. Germany
is the worst case: refit at 60 restarts, its grid stops meeting the
eligibility bar the rule required, so it drops out of the candidate list
altogether. The US and Japanese grids stay eligible but are no longer
top-ranked.

Separately, no market's fits are known to be fully converged. Running the
optimizer three times harder (180 restarts instead of 60) still finds a better
fit on 41 of the 1619 individual fits it compares (one fit per refit window
per lambda value), and it reports 11 fitted-state mismatches.

Read that 11 narrowly. The diagnostic walks every candidate lambda in each
market's grid, counts the days on which that lambda's fitted state differs
from the sealed run's, and adds those counts up across all three markets. So
11 is a total of lambda-day mismatches, not 11 distinct calendar dates; one
date can be counted once per lambda. The diagnostic also never asks whether
any of those mismatches belong to the lambda the selection rule would
actually pick for trading. Whether the traded position, the reported Sharpe,
or the P&L (profit and loss) moves at all has never been computed; that run
stopped at counting.

Nothing has been resealed in response. This is an open owner decision, and it
is part of why the first question below is still open. Evidence:
`docs/audit/2026-08-08-grid-selection-rule-001-ninit60-receipt.md`,
`artifacts/v12-stress-gate/v11-ninit180-report.txt` (the 41 and the 11),
`artifacts/optimizer-fidelity/report.txt` (the random-seed families).

## What is not settled

- Whether the sealed calibrated-reconstruction-v11 baseline is the right
  scientific comparator (its grids are fitted to published output; see above).
- Which old experiment results survive a fresh audit.
- Whether the current code path contains additional mistakes.
- What the final paper question should be.

## What we are doing now

1. No new model ideas.
2. No DA-JM implementation. (DA-JM is the work written up in
   `docs/theory/da-jm-formalization.md`; this file parks it.)
3. Audit the core path: data -> features -> Jump Model (JM) -> lambda selection -> regime signal (the day's state, used to decide equities or cash) -> equity/cash profit and loss (P&L).
4. Make one simple inventory of every important experiment already run.
5. Mark each old result as trustworthy, questionable, or invalid.
6. Look for a repeated scientific pattern only after that cleanup.

## The only files a human should need first

- `README.md`
- `CURRENT.md`
- `SUMMER_2026.md`

Detailed contracts, hashes, receipts, registry entries, and AI session logs
are archive material. They matter only when checking a specific historical
claim.

## Repository cleanup — what is left

Material that is history rather than current work now sits under `archive/`,
including the old audit scripts. Only one standalone audit script remains:
`scripts/audit/check_paper_claims.py`. It does two things. First, it checks
the quotations from the paper that carry an explicit `[line N]` citation.
Second, it searches the paper for five configured terms — terms the paper is
asserted *not* to contain — and fails if any of them turns up in the paper
body. What it does not do: it does not check unannotated prose (text with no
`[line N]` citation attached), which it reports as unchecked; and the list of
files it checks no longer includes the sealed config files, even though those
files quote the paper.
Checking code also still lives inside the package (`simple_jm_verifier.py`)
and in four audit-labelled test modules.

Still to do: `docs/theory/da-jm-formalization.md` describes work this file
has parked, and `docs/audit/` is 23 historical receipts. Six of them supply
21 of the 43 quotations the claim checker verifies; the other 17 contribute
none and are kept as history only.

## Current stop rule

Do not add more research complexity until the owner can explain the
result-producing pipeline and the important past experiments in plain
language.
