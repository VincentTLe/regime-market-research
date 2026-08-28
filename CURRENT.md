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
(run `fixed-baselines-c4b7d476e5a4-e6e7e8302ad3-67cf52166219`, 2026-08-28).

*Sealed* means its settings and its fitted results are frozen and saved, so
every new idea is measured against the same numbers instead of a freshly
refitted target. It does not mean the comparator is correct: its lambda grids
were searched against the paper's published tables and figure, so agreement
with the paper is by construction, and its optimizer restarts are not known to
reach the best fit (`docs/unspecified-choices.md` rows 2-3,
`docs/audit/2026-08-08-grid-selection-rule-001-ninit60-receipt.md`).

It is the v11-ninit60 baseline with one input corrected. The Japanese
total-return series v11 read set its dividend accruals from information after
the day they applied to — from a value two years ahead across the 2020-2022
bridge, and from each year's own full-year yield before 2011 — which breaks the
no-future-data rule for decisions in 1990-2011 and 2020-2022. The corrected
series uses the prior year's yield before 2011 and, across the bridge, the
accrual realised before the hole — it avoids the current period's figure;
when JST's prior-year value became public was not established. Everything
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

Known problem: the German leg is not clean. Its lambda grid fails the rule that
was supposed to pick it, and some German fits did not fully converge. That is
part of why the first question below is still open.

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
including the old audit scripts. Only one audit remains live:
`scripts/audit/check_paper_claims.py`, which checks that quotations attributed
to the paper are really in it.

Still to do: `docs/theory/da-jm-formalization.md` describes work this file has
parked, and `docs/audit/` is 22 historical receipts kept only because the claim
checker reads them.

## Current stop rule

Do not add more research complexity until the owner can explain the result-producing pipeline and the important past experiments in plain language.