# Summer 2026 Research Story

This file is the short human history of the project. It tells what happened
this summer in five parts, in order, and ends with what "progress" means now.

## 1. Rebuild the Shu-style Jump Model

The project started by trying to reproduce the regime-switching method and the
equity/cash results from the paper by Shu, Yu, and Mulvey.

A few terms, explained once:

- A *regime-switching method* is a model that sorts market days into a small
  number of "states" (for example, calm versus stressed) and lets the state
  change over time.
- The *Jump Model* is the regime-switching method that paper uses. It has a
  penalty that makes the model reluctant to switch states; the size of that
  penalty is called *lambda*.
- An *equity/cash backtest* is a test on past data in which the strategy holds
  the stock index in one state and cash in the other, and we measure what that
  would have earned.

Work completed:

- rebuilt market data from public sources;
- implemented the feature pipeline (the code that turns raw market data into
  the inputs the model reads);
- implemented the fixed Jump Model walk-forward process (*fixed* means the
  switching penalty does not change with market conditions during a fit;
  *walk-forward* means the model is refit as time moves forward, and is meant
  to use only data available up to each decision date);
- implemented monthly lambda selection (choosing the switching penalty afresh
  each month);
- implemented the delayed equity/cash backtest with transaction costs. A
  *signal* is the model's decision on day `t` to hold the stock index or cash;
  it earns its return two trading days later, on day `t+2`. Each trade is
  charged 10 basis points one way, that is, 0.10% of the amount traded in each
  direction;
- compared results for the US, Germany, and Japan.

Main lesson:

> We have not been able to reproduce the paper exactly from the public
> information available to us.

Important pieces are still missing or uncertain. These include the original
source data the authors used. They also include some implementation choices:
the exact lambda grid (the list of penalty values the monthly selection chooses
from), and the details of feature standardization (how each input is rescaled
before the model sees it).

## 2. Try to improve the Jump Model

Several changes were tested:

- simple challengers (plain alternative rules to compare against);
- adaptive switching penalties (letting lambda change with conditions instead
  of staying fixed);
- confirmation rules (waiting for a state change to persist before acting on
  it);
- lagged evidence (letting the switching penalty respond to evidence from
  earlier days);
- related controls (comparison runs used to check what a change actually did).

Main lesson:

> No tested change is treated as a final result. Each experiment's outcome
> is recorded in the registry; several were retracted or corrected on audit.

The *registry* is the project's running record of experiments and their
outcomes. *Retracted* means a result that was later withdrawn after an audit.

Some variants changed the regime behaviour in interesting ways. But a regime
path (the day-by-day sequence of states the model assigns) that looked better
did not automatically produce better investment results.

## 3. Audit the foundation

Later checks found real problems in both the research process and the
implementation.

Examples:

- a US index splice (the point where two price series were joined into one)
  had deleted or misaligned one trading day;
- one holdout turnover calculation used the wrong scale (a *holdout* is a
  period of data set aside from the data used to build the model; *turnover*
  is how much the strategy trades);
- the German baseline (the reference run that other results are compared
  against) had a grid-selection process that was not clean — here the *grid*
  means the baseline's list of candidate lambda values, and the problem was in
  how that list was chosen;
- increasing the number of optimizer starts changed some grid conclusions (the
  fitting routine is run from several different starting points and the best
  fit is kept; using more starting points changed some conclusions drawn from
  the lambda grid);
- some tests looked stronger than they actually were;
- some earlier scientific claims had to be corrected or withdrawn.

Main lesson:

> Passing tests and producing sealed artifacts did not mean the research was scientifically settled.

A *sealed artifact* is a saved result file whose contents are recorded with a
fingerprint (a hash) so that later changes can be detected. Sealing shows a
file has not changed; it does not show the file was right.

## 4. Build too much research infrastructure

To prevent more mistakes, the repository accumulated a lot of process
machinery:

- contracts (written specifications an experiment must follow);
- hashes (fingerprints of files);
- registries (see section 2);
- audit receipts (records that a check was run);
- agent logs (records of what AI tools did);
- and many tests.

This improved traceability — the ability to trace a result back to the code,
data and settings that produced it. But it also created a new problem:

> The repository became difficult for the owner to understand.

By August, the project contained more process and historical machinery than a
human needed for everyday research.

## 5. Current reset

As of 2026-08-28, the project is deliberately paused before any new model work.

The plan is:

1. understand and check the core pipeline (the whole chain of steps from raw
   data to equity/cash positions), with the checking done by someone who did
   not build it;
2. inventory the important experiments already run;
3. decide which results are still trustworthy;
4. only then choose the paper question.

DA-JM (a proposed new variant of the Jump Model, the Duration-Aware Jump
Model) and other new model ideas are parked for now.

## What counts as progress now

Progress is not another experiment, another audit document, or another
AI-generated framework.

Progress means being able to answer, in plain language:

- What data are used?
- How are features computed?
- How does the Jump Model produce states?
- How is lambda chosen?
- How do states become equity/cash positions (the decision to hold the stock
  index or cash)?
- Which past experiments are trustworthy?
- What repeated scientific question remains after the audit?
