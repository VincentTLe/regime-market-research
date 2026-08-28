# Current Research State

Last updated: 2026-08-28

## Where the project stands

The project is not currently trying to add another Jump Model variant.

The main problem is simpler:

> Can we trust the existing pipeline and the results already produced?

A large amount of the repository was built and checked with AI assistance. Several later reviews found real problems in data handling, baseline selection, optimizer behavior, experiment interpretation, and tests. Because of that, old results are not being treated as final until the core path is independently checked.

## What is reasonably clear

- The project studies a two-state Jump Model used for a simple equity/cash strategy.
- The public-data reconstruction is not an exact reproduction of Shu et al.; some source data and implementation choices are unavailable.
- Several model changes have been tested.
- Most did not produce a clear, robust improvement.
- Some experiments produced interesting behavior, but those results still depend on a pipeline that needs a cleaner independent audit.

## What everything is compared against

The comparator is the sealed **calibrated-reconstruction-v11** fixed Jump
Model, set up in `configs/baselines/research-calibrated-reconstruction-v11.toml`
(run `fixed-baselines-3448b85e0fec-97ee407c64ce-7130da99b50b`, 2026-08-28).

*Sealed* means its settings and its fitted results are frozen and saved, so
every new idea is measured against the same numbers instead of a freshly
refitted target. It does not mean the comparator is correct, and it does not
mean it is neutral. The paper never publishes its lambda grid, so ours was
searched for, in two stages, against numbers the authors did publish.

The first stage was exhaustive. Every subset of size 2 to 8 that can be drawn
from a fixed 29-value lambda menu — 6,474,511 grids in all — was scored against
the performance figures the paper prints in its Table 4 and Table 5. What
survived were the grids landing closest to those published cells: 36,657 in the
US, which reach all fourteen of them, and, because no German or Japanese grid
reaches all fourteen, the best available thirteen out of fourteen, which is 366
grids in Germany and 2,948 in Japan.

The second stage ranked those survivors — all of them, not a sample — by how
closely each grid's own daily regime path agrees with the state sequence the
authors printed in their Figure 5. The top-ranked grid in each market is the
grid the sealed v11 baseline uses.

The comparator is therefore fitted to published output at both stages, first to
the published tables and then to the published figure, and "the new model beats
the baseline" is a statement about that fitted reference, not about the authors'
model. Evidence: `docs/audit/2026-07-31-jm-exhaustive-search.md`,
`docs/audit/2026-07-31-jm-per-market-grids.md`,
`docs/audit/2026-08-07-grid-selection-rule-001-receipt.md`,
`artifacts/grid-selection-rule/01-rule/summary.csv`.

Its optimizer restarts are also not known to reach the best fit (the
`n_init` finding below), so "sealed" means frozen, not converged.

It is the v11-ninit60 baseline with one input corrected. The Japanese
total-return series v11 read set its dividend accruals from information after
the day they applied to — from a value two years ahead across the 2020-2022
bridge, and from each year's own full-year yield before 2011 — which breaks the
no-future-data rule for decisions in 1990-2011 and 2020-2022. The corrected
series uses the prior year's dividend yield before 2011 and, across the
bridge, the accrual realised before the hole — no accrual is set from a value
dated after the day it applies to. JST's own documentation defines its
yearly yield as that year's dividends over that year's price, sourced for
Japan from the Bureau of Statistics' annual Tokyo Stock Exchange tables, so
the year y−1 figure contains only year y−1 information (whether the price is
year-end or the annual average is not stated; the figure covers the whole
exchange, not the 225 Nikkei names — see the receipt). Everything
else — grids, optimizer
restarts, features, HMM, selection rule, metrics, US and German data — is
byte-identical to v11. Rerun on the corrected input, the US and German outputs
did not change at all; in Japan the delay-1 fixed-JM Sharpe is 0.294 either
way, but the monthly lambda choice changed in 92 of 409 months and the delay-10
Sharpe fell by 0.024. That was reported as measured, with no threshold, and the
new run became the comparator by a rule written before it was scored
(`docs/audit/2026-08-28-jp-causal-rebuild-receipt.md`, registry
`jp-causal-rebuild-001`). The exact bytes each sealed run read are published
under `data/snapshots/`; the `redistribute_raw_data = false` line inside the
sealed configs describes the policy when they were sealed, not current
practice.

**Frozen.** The owner's decision of 2026-08-27: this comparator is a calibrated
reconstruction, not a replication, and it stops here. No change to the lambda
grids, the feature standardizer, the refit months, the HMM grid or the number
of optimizer restarts will be made to move its numbers toward the paper's.
Each of those is a methodology change, and any future one needs its own frozen
question first. Bugs — code that does something other than what the documents
say, or data that uses information it could not have had — are still fixed.

`configs/baselines/legacy/` holds older versions (v11-ninit60, v10, v9.4, and
earlier). v11-ninit60 differs from the comparator only in the Japanese input;
the older ones also use different lambda grids and optimizer settings. They are
history, not the current comparator, and auditing one of them answers a
different question.

Known problem, and it is not only German. That grid-choosing rule was rerun
using the 60 optimizer restarts the sealed baseline actually runs at, and it
then picks none of the three adopted grids. Germany is the worst case: refit at
60 restarts, its grid stops meeting the eligibility bar the rule required, so it
drops out of the candidate list altogether. The US and Japanese grids stay
eligible but are no longer top-ranked. Separately, no market's fits are known to
be fully converged — running the optimizer three times harder (180 restarts
instead of 60) still finds a better fit on 41 of the 1619 (window, lambda) fits
it compares, and it reports 11 fitted-state mismatches. Read that 11 narrowly.
The diagnostic walks every candidate lambda in each market's grid, counts the
days on which that lambda's fitted state differs from the sealed run's, and adds
those counts up across all three markets. So 11 is a total of lambda-day
mismatches, not 11 distinct calendar dates — one date can be counted once per
lambda — and the diagnostic never asks whether any of them belong to the lambda
the selection rule would actually pick for trading. Whether the traded position,
the reported Sharpe, or the P&L moves at all has never been computed; that run
stopped at counting. Nothing has been resealed in response; this is an open
owner decision, and it is part of why the first question below is still open.
Evidence:
`docs/audit/2026-08-08-grid-selection-rule-001-ninit60-receipt.md`,
`artifacts/v12-stress-gate/`, `artifacts/optimizer-fidelity/report.txt`.

## What is not settled

- Whether the sealed calibrated-reconstruction-v11 baseline is the right
  scientific comparator (its grids are fitted to published output; see above).
- Which old experiment results survive a fresh audit.
- Whether the current code path contains additional mistakes.
- What the final paper question should be.

## What we are doing now

1. No new model ideas.
2. No DA-JM implementation.
3. Audit the core path: data -> features -> JM -> lambda selection -> regime signal -> equity/cash P&L.
4. Make one simple inventory of every important experiment already run.
5. Mark each old result as trustworthy, questionable, or invalid.
6. Look for a repeated scientific pattern only after that cleanup.

## The only files a human should need first

- `README.md`
- `CURRENT.md`
- `SUMMER_2026.md`

Detailed contracts, hashes, receipts, registry entries, and AI session logs are archive material. They matter only when checking a specific historical claim.

## Repository cleanup — what is left

Material that is history rather than current work now sits under `archive/`,
including the old audit scripts. Only one standalone audit script remains:
`scripts/audit/check_paper_claims.py`. It does two things: it checks the
quotations that carry an explicit `[line N]` citation, and it runs a refutation
pass over five configured terms the paper is asserted *not* to contain, failing
if any of them turns up in the paper body. It does not check unannotated prose,
which it reports as unchecked, and its target list no longer reaches the sealed
configs, which do quote the paper. Checking code also still lives inside the package
(`simple_jm_verifier.py`) and in four audit-labelled test modules.

Still to do: `docs/theory/da-jm-formalization.md` describes work this file has
parked, and `docs/audit/` is 22 historical receipts. Six of them supply 21 of
the 43 quotations the claim checker verifies; the other 16 contribute none and
are kept as history only.

## Current stop rule

Do not add more research complexity until the owner can explain the result-producing pipeline and the important past experiments in plain language.