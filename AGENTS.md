# AGENTS.md

Rules for AI tools working in this repository.

The owner must be able to understand every result-producing change in plain
language.

## Current priority

Do not add a new model or experiment.

The current task is to simplify and independently verify the existing project.
In plain words: make what already exists easier to understand, and re-check,
separately from the original run, that it does what it says it does.

Read first:

1. `README.md`
2. `CURRENT.md`
3. `SUMMER_2026.md`

Historical audit material is secondary. Open it only when checking a specific
old result. (An audit here means a later check of an old result: how it was
produced and what evidence it rests on.)

## Before changing research code

Explain to the owner:

- what file or step is being changed;
- why it is needed;
- whether it can change a scientific result;
- how the change will be checked.

Do not make a large research change without owner approval.

## Scientific rules

1. **No future data.** A decision made on day `t` may only use information that
   existed on or before day `t`.
   In plain words: when the model decides something for day `t`, it may only
   look at information that existed on or before day `t`.

2. **Timing and cost are fixed.** A signal on day `t` earns its return two
   trading days later, on `t+2`, and pays its trading cost on that same day.
   The cost is 10 basis points one way. These numbers are set in
   `configs/baselines/research-calibrated-reconstruction-v11.toml` and enforced in
   `src/adaptive_jump/config.py`. Do not change them inside an experiment.
   Never show a result with no cost or no delay as if it were real strategy
   performance.
   In plain words: a signal is the model's decision for the day, and a trading day is a day the market is open. A basis
   point is one hundredth of one percent. "One way" is the cost per trade in one
   direction; how the code applies it is not stated in this rule. A result that
   skips the delay or the cost is not a real strategy result and must not be
   shown as one.

3. **The baseline and the main comparisons are scored on 1990-2023.** A few
   older or auxiliary experiments used shorter windows, so check the artifact
   before quoting a period. Anything after `2023-12-31` needs the owner's
   permission first. The 2024-2026 window is not a fresh test set: it was
   already opened and read once (`holdout-2026-001` in the registry), so it can
   no longer prove that a result holds on unseen data.
   In plain words: the baseline is the reference result that other results are
   compared against. A fresh test set is data the project has not yet used to
   evaluate or pick a model. A window is a stretch of dates. An artifact here means a
   run's saved output; the registry here means the file
   `research/experiment_registry.jsonl`, and `holdout-2026-001` is the entry in it that records the one read of the
   2024-2026 window. That window was already used once for that, so it can no
   longer show that a result holds on data the project has not seen.

4. **Never overwrite the current input files.** The files in `data/raw/` and
   `data/external/` are the evidence an audit is checking. Rebuilding data to
   verify it is fine and expected — but write the rebuilt copy somewhere else
   and compare it against the current files. The builders in `scripts/data/`
   write straight into `data/external/` and have no output option, so do not
   run them against this working tree at all: copy the repository elsewhere and
   rebuild there. Never swap one market's series for another. Git ignores these
   files, so if they do change, `git status` will still look clean.
   In plain words: the builders are the scripts that create the data files, and
   they have no setting to write anywhere else, so running them here would
   overwrite the current files. The working tree is the copy of the repository
   you are working in. A market's series is its run of daily values. "Git
   ignores these files" means Git does not track them, so a change to them will
   not show up as a change. You have to compare copies yourself.

5. Do not tune an unknown paper setting simply to match the paper's reported numbers.
   In plain words: if the paper does not say what value it used, do not choose
   a value just because it makes the numbers match the paper's table.

6. Do not hide failed or inconclusive experiments.
   In plain words: an experiment that gave a bad answer, or no clear answer, is
   still reported.

7. Do not call something reproduced, verified, or proven unless the specific check was actually run.
   In plain words: say a thing was reproduced, verified or proven only if that
   exact check was run.

8. AI review is not independent scientific validation.
   In plain words: an AI reading the work, even a second time or a different
   AI, is not an outside scientific check. Do not report it as one.

9. A passing test suite is not proof that the research conclusion is correct.
   In plain words: a passing test only shows that the cases the tests cover
   behave the way the tests expect. It does not show that the science behind
   the code is right.

10. Keep claims narrow: say exactly which market, sample, model, and assumptions support them.
    In plain words: a claim is only as wide as the evidence behind it, so name
    the exact setting the evidence came from (the sample is which data and
    which dates were used).

11. Never use a broad word such as "verified", "validated", "correct", or
    "independent" without naming exactly what was checked and what remains
    unchecked.
    In plain words: a broad word on its own is not evidence. Say what was
    checked, and say what was not.

## Complexity rule

Prefer the smallest implementation that answers the current question.

Do not add:

- new governance systems;
- dashboards;
- duplicate runners;
- new audit frameworks;
- new model families;

unless the owner explicitly asks for them.

Roughly: a runner is a script that launches an experiment, a governance system
is extra process machinery for approving or tracking work, and a model family
is a new kind of model rather than a new setting of an existing one. None of
these is added unless the owner asks.

## Historical material

Do not rewrite old registry entries, frozen experiment contracts, or audit
receipts merely to make them look current. They are historical records.
In plain words: they record what was done and claimed at the time ("frozen"
means the record is not edited after it was written). Changing them would
change the record.

If old material conflicts with `CURRENT.md`, treat `CURRENT.md` as the current
research direction and the old file as history.
