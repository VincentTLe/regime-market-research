# Adaptive Jump Model

This repository studies the Statistical Jump Model of Shu, Yu, and Mulvey for a simple equity/cash regime-switching strategy.

In plain terms: a *regime-switching strategy* is one that assigns each day to one of two market states and holds stocks in one state and cash in the other. The *Statistical Jump Model* from the Shu, Yu, and Mulvey paper is the model studied here for assigning those states.

## What this project has done

1. Rebuilt a public-data version of the Shu-style pipeline for the US, Germany, and Japan. (A *pipeline* is the chain of steps from the raw input data to a final strategy result.)
2. Tested several changes to the Jump Model.
3. Found that many changes did not produce a clear, reliable improvement.
4. Found real problems in the research pipeline and baseline choices (the *baseline* is the reference version of the strategy that every proposed change is compared against), including data, grid-selection, optimizer, and testing issues. (Here *grid selection* means how the list of candidate lambda values the model chooses from — the lambda *grid* — was itself chosen; lambda is explained under "What period the results cover" below. The *optimizer* is the routine that fits the model to the data.)
5. Stopped adding new models until the core pipeline has been checked by
   someone who did not build it.

## Current status

No current experimental result is treated as final.

The immediate job is:

1. verify the core pipeline from data to final P&L (P&L means the profit and loss of the strategy — the final number the whole pipeline produces);
2. decide which old experiments are still trustworthy;
3. only then choose the research question the paper will answer.

Read these files in order:

- `CURRENT.md` — where the project stands now.
- `SUMMER_2026.md` — what happened this summer.

Everything else is secondary.

## Core code

The main scientific path is:

```text
data.py
  -> features.py
  -> models.py
  -> walkforward.py
  -> backtest.py
```

These files live in `src/adaptive_jump/`.

Experiment code sits in two places. Any list of the project's experiments has to cover both:

- `src/adaptive_jump/experiments/` — experiments that were moved into the package;
- `scripts/experiments/` and `scripts/diagnostics/` — over 40 more probe and
  diagnostic scripts, several of which also produced results, including the ones
  that triggered this reset (the stop on new models described under "What this
  project has done"): grid selection, optimizer fidelity, the frequency ladder.

## What period the results cover

The current baseline and the main comparisons are scored on **1990-2023** in
all three markets. A few older or auxiliary experiments used shorter windows.

The raw data starts in the 1960s, but that early part is warm-up, not results.
*Warm-up* is the stretch of history the model must see before it is allowed to
make its first decision. It needs 3000 trading days to fit (about 12 years) and
then 8 more years to pick lambda (lambda is the model's *switching penalty*: the
setting that controls how reluctant the model is to switch from one market state
to the other; it is chosen from data). The warm-up alone does not explain why
results start in January 1990. The baseline config asks for `1990-01-01`, to
line the period up with the paper's, and its rule takes whichever is later — the
requested date, or the warm-up end. Which of the two actually applies in each
market is worked out during each run and is not written to any file kept in
Git. So read January 1990 as the requested date, not as a date the warm-up
forced.

Anything after `2023-12-31` is off limits without the owner's permission.

## Archive and audit material

The repository contains a large amount of historical material under `archive/`, `research/`, `docs/audit/`, and `artifacts/`.

That material is kept so that old results can be traced back to what produced them. It is not the main reading path and should only be opened when checking a specific old result.

## Rule for new work

Do not add a new model or experiment until the current pipeline has been checked by someone who did not build it and the owner can explain the result-producing path in plain language.
