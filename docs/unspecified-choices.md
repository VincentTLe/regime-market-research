# Free parameters the paper never fixes

Shu, Yu and Mulvey (2024), arXiv:2402.05272v3.

**What this file is.** The paper describes a method, but it leaves many
settings unstated. Every row below is one such setting: a knob **we** had to
set because the paper does not. The results reported here are conditional on
these settings. Read this file before proposing a change to any knob listed in
it. Never search a row for the setting that best matches the paper's numbers:
choosing a setting because it reproduces the target is fitting to the answer,
and AGENTS.md rule 5 forbids it.

**How each row is laid out.** What the paper says (with the line quoted
wherever the paper says anything), what the paper does not say, what we chose,
and what we measured when we tried alternatives. A row with no measured spread
means we do not know how sensitive the results are to that choice.

**Where the line numbers come from.** Every quote below cites a line number.
Those refer to the text produced by
`pdftotext -layout data/external/inputs/2402.05272v3.pdf`, which has 1168 lines
when split on newlines only (Python's str.splitlines also breaks on form feeds
and shifts every number).

**Three terms that appear in almost every row.** The *Sharpe ratio* is a
strategy's average return above cash, divided by the strategy's volatility (how
much its return bounces around); row 12 gives the exact denominator used here.
It is the score the paper's selection rule uses. A *regime* is a market state
(roughly, bull or bear) that a model infers from data; the paper's two models
are the *jump model* (JM) and the *hidden Markov model* (HMM). *Table 4* is the
paper's main results table, with eight performance numbers per market and
model; most rows below measure how far a choice moves us from it.

**Four project words.** A *sealed* run is one whose configuration and outputs
have been frozen and recorded so they cannot change silently; the *comparator*
is the sealed run that new results are compared against. The *registry* is the
project's written record of experiments and the decisions taken on them.
*Out-of-sample* is the reported period, on which each day's signal comes only
from models fitted to earlier data.

Two reading notes. Rows are numbered in the order they were added, so row 6
sits after row 10 in the file. Numbers quoted from runs before v10 (the v8.x
and v9.x series) come from run directories that are no longer on disk; they are
recorded values, not re-checkable ones.

Status legend: **open** = still our choice, alternatives materially move the
numbers · **bounded** = alternatives measured, spread known · **closed** = the
paper does pin it after all, row kept so nobody re-opens it.

---

## 1. Feature standardisation geometry — CLOSED as bracketed-but-unidentifiable; largest measured lever

**What the paper says.** Only that the features arriving at the model are
standardised. To *standardise* a feature is to subtract a mean from it and
divide by a standard deviation, so that the three input features sit on a
comparable scale. The paper says this happens and nothing more:

> [line 397] "In our application, given an observation sequence of D standardized features"

Section 3.4.1 (line 494 onward) defines the three features and their halflives
and says nothing further about scaling. Searched: `clip`, `winsor`,
`standardi[sz]`, `normali[sz]`, `preprocess`, `scale`, `outlier`, `robust`.

**What the paper does NOT say.** Which data the mean and standard deviation are
computed from: the whole history, the training window, or a fresh estimate at
each refit. Whether extreme feature values are clipped (capped) or winsorised
(pulled in to a chosen percentile) at all. `DataClipperStd` / clipping at three
sigma (capping any value more than three standard deviations from the mean)
appears in the authors' GitHub example notebook for the NASDAQ data set. **It is
not in the paper.** Do not cite it as if it were.

The one adjacent statement is about raw returns, not features, and sits in the
Data section:

> [line 169-170] "Despite a few extreme returns during these events, we do not process outlier values to minimize manual intervention."

**What we chose.** Causal expanding full-history standardisation anchored at the
sample start, `min_observations = 63`, then `_IdentityScaler` into the jump
model (`src/adaptive_jump/features.py:124-138`, config key `standardizer =
"expanding_full_history_ddof1"`). In plain terms: on each day, the mean and
standard deviation are computed from every observation from the sample start up
to that day ("expanding"), never from later days ("causal"); no output is
produced until 63 observations exist; and the jump model then applies no
further rescaling of its own (`_IdentityScaler`).

**Consequence, measured.** Because the mean and standard deviation come from the
whole history rather than from the fit window itself, the features inside each
fit window are not centred at zero and do not have a spread of one. The three
features are `dd_10`, a downside-deviation measure (how large the negative
returns have been), and `sortino_20` and `sortino_60`, Sortino ratios (return
divided by downside deviation). The number in each name is the halflife in
days — how quickly old days stop counting — explained in row 13. The table
below shows the standard deviation of each feature entering each JM refit on
the v8.4 run, by market. *Anisotropy* is the largest of the three standard
deviations divided by the smallest; 1.00x would mean the three features carry
equal spread.

| market | `dd_10` std | `sortino_20` std | `sortino_60` std | anisotropy |
|---|---|---|---|---|
| us | 1.220 | 0.769 | 0.656 | 1.86x |
| de | 1.242 | 0.927 | 0.892 | 1.39x |
| jp | 1.020 | 0.854 | 0.824 | 1.24x |

with means +0.196 to +0.307 on `dd_10`. Why this matters: the jump model
minimises `0.5*||x - theta||^2`, an isotropic distance, meaning it measures
distance the same way in every direction and so gives a feature with a bigger
spread a bigger say. In the US fit, `dd_10` therefore carries about 3.5x the
weight of `sortino_60`. The distortion differs by market. This row treats that
as the reason the gap to the paper also differs by market; that is an inference
from the mechanism, not a separately cited measurement.

**Spread across alternatives** (Japan JM Sharpe, paper reports 0.31). The table
shows the Japanese jump-model Sharpe under the standardisation and anchoring
variants listed. Every row names the run it came from, because the same recipe moves as other
settings change and stale figures were previously carried forward under the
label "current":

| variant | run | jp JM Sharpe | side effect |
|---|---|---|---|
| expanding, anchored 1969-05 | **v8.4 (current)** | **0.197** | us JM 0.662 vs 0.68, de JM 0.391 vs 0.44 |
| expanding, anchored 1970 | v8.3 | 0.260 | out-of-sample window started 1990-08, not 1990-01 |
| expanding, min_obs 250 | v8.1 / v8.2 | 0.157 / 0.169 | superseded windows |
| per-refit clip 3 sigma + StandardScaler ⚠ | v8.2 variant | 0.219 | degrades us 0.788 -> 0.460, de 0.361 -> 0.310 |
| the same with lambda fixed at 35 ⚠ | v8.2 variant | 0.310 | not a selectable spec; leverage (average fraction of the time invested) 43% vs 75% |
| cold start 1970 | v8.2 variant | 0.260 | |

⚠ **The two clip-3-sigma rows are historical measurements only and are withdrawn
from interpretation.** `DataClipperStd` / clipping at three sigma is example code
from the authors' GitHub for a different data set, it is nowhere in the paper,
and by standing owner instruction (2026-07-31, registry `AMENDED` on
`jm-standardizer-geometry-002`) it must not be proposed, run, or cited as an
author-method candidate at all. The numbers stay so nobody re-measures them.

The v8.4 row is stale. The numbers above belong to the v8.4 run. Later runs
read differently:

- v10 run (`fixed-baselines-36ca1ace131c-…`): us 0.683, de 0.398, jp 0.291;
- v11-ninit60, the sealed baseline as of 2026-08-08
  (`fixed-baselines-5b12efa2948c-…`), fixed JM (the paper's jump model as run
  in this project's frozen baseline, not any rival variant; the name is used
  throughout this file): us 0.677, de 0.389, jp 0.294;
- calibrated-reconstruction-v11, the comparator since 2026-08-28
  (`fixed-baselines-3448b85e0fec-…`; corrected Japanese input, same grids):
  us 0.677, de 0.389, jp 0.294.

Quote the run, never the word "current".

**Axis status.** This row is no longer open. Table 3 of the paper reports how
many regime shifts per year each setting produces; that pattern across settings
is the "persistence curve". `jm-standardizer-geometry-002/-003` exhausted the
family of geometries suggested by the authors' own artifacts, and no cadence
reproduces the paper's Table-3 persistence curve (V0 2/6, V1 1/6, V3 3/6
against a rule requiring 5/6 — that is, the variants matched 2, 1 and 3 of the
six Table-3 comparison points, where the rule required 5 of 6). The registry
closes the axis with `no_further_geometry_variants = true`. The honest label is
**bracketed but unidentifiable from public information**, not "open". That is:
the alternatives have been measured, so the range they span is known
(*bracketed*), but nothing the paper publishes says which one the authors used
(*unidentifiable*).

**And it is not an independent choice.** The registry records
(`CORRECTION`, `expanding_full_history_ddof1`) that this geometry was identified
partly by which recipe reproduced Table-4 economics — a published number. In
other words, the choice was partly steered by the target. It is therefore
target-conditioned in the same way the lambda grid is, must be disclosed
wherever the grid's circularity is disclosed, and **no result may be described
as independent of it**.

Ledger conclusion, already established: no single preprocessing variant
reproduces Table 3 and Table 4 at the same time. Treat this row as bounded
evidence, not as an unsolved bug to keep re-litigating.

---

## 2. Jump-penalty candidate grid — OPEN

A short explanation first. The jump model labels each day with a regime. The
*jump penalty*, written lambda, is a cost the model pays every time it switches
regime; a larger lambda means fewer switches. The model does not pick lambda
freely: it chooses from a short list of allowed values, the *candidate grid*.
The rule for choosing is *validation Sharpe*: for each candidate, compute the
Sharpe ratio the strategy would have earned over a recent lookback period, and
pick the candidate with the highest one.

**What the paper says.** That the penalty is chosen monthly by validation
Sharpe over an eight-year lookback:

> [line 704-711] "we use a time-series cross-validation approach, updating the optimal jump penalty monthly... We then select the value λ̂ that yields the highest Sharpe ratio during this validation period"

Table 3 (line 643) exercises lambda in {0, 5, 15, 35, 70, 150} and the text
calls 50 to 100 "a typical value" (line 638-639).

**What the paper does NOT say.** The candidate grid actually used for selection.
Table 3 is an illustration of persistence, not a stated search space.

**What we chose.** `[0, 5, 15, 35, 70, 150]`, matching Table 3, was the v8.4-era
choice and is no longer what runs. The sealed v11-ninit60 baseline uses
per-market grids that resemble Table 3 not at all: us `[0, 0.1, 20, 220]`, de
`[0.1, 1, 10, 21.544…, 26.827…, 40, 100, 500]`, jp `[1.931…, 20, 25, 26.827…,
40, 51.795…, 220]`. These were not read off the paper. They were searched
against the paper's published Table 4 and Table 5 cells, then ranked by daily
agreement with the authors' printed Figure 5 state path. Agreement with
published output is therefore by construction — the grids were chosen because
they agree, so their agreement with the paper is not evidence of replication —
and this row
carries the same circularity disclosure as row 1: **no result may be described
as independent of the lambda grid.** Note the two stages: the candidate pool was
filtered on the paper's published Sharpe, turnover and drawdown cells, and only
the final ranking among survivors avoided strategy metrics. (Turnover is how
much of the portfolio is bought and sold in a year; row 7 gives the paper's
exact definition.) The filter used the eight Table-4 cells (CAGR, volatility,
Sharpe, maximum drawdown, Calmar, 5% expected shortfall, turnover and leverage)
plus the three Table-5 cells at each long delay. (The *delay* is the number of
trading days between a signal and the trade it triggers; Table 5 reports the
strategies at longer delays than Table 4.)

**And the choice is not stable.** The jump-model fit is repeated from several
starting points and the best fit is kept; "restarts" counts those starting
points. Rerun at the 60 optimizer restarts the sealed baseline
actually uses, that same grid-selection rule picks none of the three adopted
grids, and Germany's leaves the eligible set entirely
(`docs/audit/2026-08-08-grid-selection-rule-001-ninit60-receipt.md`). Nothing
has been resealed in response. The size of this free parameter has been
measured once, for Germany. The `-009` grid-search artifacts (study
`jm-per-market-grid-009`) list twelve example grids for that market, each
meeting 13 of the 14 published target cells listed just above. Across those
twelve, the fixed JM's Sharpe ranged from 0.398 to 0.457 (registry
`baseline-reseal-v10` NOTE): a spread of about 0.06 with everything else held
fixed. Those twelve are an example subset of the 366 German grids that passed
the filter, not a sample chosen to span them. That spread has not been measured
on the same run, market and settings as any rival model's improvement over the
baseline, so this file does not express it as "N times" such an improvement.
Treat this row as an unresolved lever, not a settled choice.

**An unresolved boundary diagnostic, and its evidence is not in the
repository.** A "boundary" month is one in which the selector picks the largest
lambda in its grid — the edge of what it was allowed to test. Each run writes
the fraction of months in which the fixed JM selects its grid's largest lambda
to that run's `boundaries.csv`. Those files live under `artifacts/`, which
`.gitignore` excludes, and no tracked file records the sealed v11 run's
fractions. Earlier drafts of this row quoted exact percentages from a local
copy; they are removed, because a number a fresh checkout cannot reproduce is
not repository evidence. To see them, rerun the sealed baseline and read its
own `boundaries.csv`.

Three things about this diagnostic *are* checkable here, and they all say the
same thing — it is unresolved. First, whatever the fraction is, it would only
show that the largest *tested* lambda scored best in those months; it would not
show that the selector wants a still larger penalty, or that the endpoint rather
than the data set the choice, because no lambda-widening test has been run.
Second, the statistic is not self-interpreting: padding the German HMM grid with
a candidate almost nobody selects flipped the same boundary gate from FAIL to
PASS with turnover identical to six decimal places and the shift count unchanged
at 144, though Sharpe did move slightly, 0.2228 to 0.2202
(`docs/audit/2026-07-29-codex-review-verdicts.md`). In other words, the gate can
be passed by adding a candidate that changes almost nothing. Third, the
configured limit that would flag it, `upper_boundary_month_fraction_limit`, is
1.0 in `configs/baselines/research-calibrated-reconstruction-v11.toml` (as it
was in v11), and no fraction can exceed 1.0, so it reports and cannot fail.
When the HMM grid was widened, the best-scoring candidate moved out to the new
values instead of settling inside the old range; the same test has not been run
for lambda.

---

## 3. HMM smoothing grid — OPEN

A short explanation first. The HMM's raw day-by-day regime labels can flicker.
The paper smooths them with a *median filter* of window k: each day's label is
replaced by the majority label over the k most recent days ending on that day
(a trailing, causal window), which removes short-lived flips. k = 0 means no filter is applied. Like lambda in row 2, k is
chosen monthly from a candidate grid by validation Sharpe.

**What the paper says.** The same monthly validation-Sharpe procedure selects
the HMM smoothing window:

> [line 715-716] "We employ the same method to optimally select the smoothing hyperparameter k for HMMs."

**What the paper does NOT say.** The candidate set. Section 3.4.3 describes the
selection procedure and never lists what it selects from. Table 3 exercises k in
{0, 2, 4, 8, 20} (line 643), but that table is an illustration of how
persistence responds to k, not a declaration of the search space:

> [line 646] "Table 3: Average number of shifts per year in the online inferred regime sequence from 1982 to 2023,"

The one value the paper does name is the literature default it inherits from
Bulla et al. (2011), the same paper cited at line 387 as the source of the
median filter:

> [line 390] "Originally, k was set at 6; in our approach, it is selected from a range of candidate values automatically via a cross-validation framework."

**What we chose.** v8 through v8.4: `smoothing_grid = [0, 2, 4, 8, 20]`, copied
from Table 3. **v8.5 onward: `[0, 2, 4, 6, 8, 20]`.** Copying Table 3 dropped
k = 6, so the candidate range excluded the only value the paper names — our
construction error, not a property of the paper. The grid as a whole stays a
free parameter; only the omission of 6 was a defect.

The justification for adding 6 is that the paper names it. It is **not** that it
improves agreement with Table 4 — see AGENTS.md rule 5 on never tuning an
unspecified knob for the setting that best matches the target. The direction of
the effect was measured after the decision, not before it.

**Consequence, measured.** A "boundary gate" here is a check that fails when
the selector picks the largest k in the grid too often. Under the Table-3 grid
the boundary gates fail because the selector parks at k = 20 (jp delay-1 39.5%,
us delay-10 39.0% — the share of months in which k = 20 was chosen). Extending
the grid was separately measured across six shapes: extensions that clear the
gate on one market break it on another, and the long-tail grids that clear all
three move the HMM Sharpe far from the paper (Germany HMM Sharpe +0.043 ->
-0.240). Grid choice
is therefore a live free parameter with a known, large spread; the v8.5 change
is the one edit to it that has an a priori justification, meaning a reason that
could be given before seeing its effect on the numbers.

**How much of Table 4 this row now owns (2026-07-28).** After the S&P 500
substitution (a change of the US input series, recorded outside this file) and
the drawdown basis of row 8, turnover is the *only* Table 4 metric outside
tolerance (the pre-set allowance for how far a cell may sit from the paper's
value; see "Do not report confidence intervals" below) in any of the three
markets, and this grid is the only
free parameter it depends on. The dependence is not in the smoother and not in
the metric. Three checks support that:

- our fixed-k persistence curve reproduces Table 3 to a mean 1.9% on the paper's
  own index, so the smoother and the online state sequence are right;
- Shu's own position path, read off Figure 6 and applied to our returns, gives
  turnover 1.4123 against the published 1.410 and exactly 96 regime shifts, so
  the turnover definition and the trading accounting are right;
- of 128 / 152 / 208 signal flips, only 3 / 3 / 2 are manufactured by switching
  candidate at a month boundary, so the composition layer (the step that stitches
  each month's chosen candidate into one signal) is not the cause.

Inverting the published turnover through our own fixed-k curve (that is, asking
which single k would produce the paper's turnover on our curve) puts Shu's
effective k near 13.4 (us), 3.6 (de) and 6.4 (jp). That is no single value, and
one of them lands in the gap our grid leaves between 8 and 20. Our v9 US picks are k20
33%, k8 29%, k6 21%, k0 9%, k4 6% (share of months selecting each k); the 9% of
months at k = 0, where no filter is applied at all, contribute about 23% of all
our trading.

**Update 2026-07-30, after the sealed runs and an external source sweep.**

*Identification, sharpened.* (Identification here means: can the paper's
candidate set be pinned down from what it publishes?) Measured on the sealed
v9.3/v9.4 regime labels across eight defensible candidate sets, no single set
puts turnover inside tolerance in more than one market. The two sets that
manage one market demand opposite ends: the US is matched only by
{4, 8, 12, 16, 20}, which puts all eight US Table-4 metrics inside tolerance
(8/8), and Germany only by {2, 4}, likewise 8/8 for Germany. Japan is matched
by none, though its 2.90 is attainable. One shared candidate set cannot
satisfy both, so no grid choice reproduces the row. This matches the effective-k
inversion above (13.4 / 3.6 / 6.4).

*The grids are unpublished everywhere, now checked at the source.* The author's
`jumpmodels` package (PyPI 0.1.1, sole release) has no CV code, no grid, no HMM
and no median filter; the GitHub repo's only example hard-codes λ = 50 on
Nasdaq-100 data; arXiv v1 published a λ grid ({10, 22, 50, 100, 220, 500, 1000})
for a *different* protocol and dataset and v3 withdrew it; the companion paper
gives only endpoints (0-100, log-spaced). Checked 2026-07-29/30 by three
separate AI-agent passes per claim — a second reading, not independent
validation (AGENTS.md rule 8).

*Where our excess turnover concentrates.* Comparing bear episodes one by one
against Shu's own Figure 6 path: we have 13 extra US bear episodes, 10 of them
five sessions or shorter, mostly post-2000 (so not attributable to the
reconstructed pre-1988 segment); 7 of the 11 post-2000 flickers fall in months
where the monthly selection (the cross-validation, "CV") picked k = 0. Removing
the k = 0 excess arithmetically (US turnover 1.795 → 1.528) agrees with the
no-zero candidate
set measured separately by an actual run (1.530) — and still leaves the US
outside tolerance, so this refines the attribution without changing the
verdict. There is a defensible a-priori reading that k = 0 is not a *filter
window* candidate at all; it is recorded, not adopted, because adopting it for
its effect on Table 4 would be fitting.

*External echo.* Li, Chen, Tao & Ji (2025), citing the paper, select λ by
information criteria from {0, 5, 10, 25, 50, 100} and land on the upper endpoint
for all twelve assets — the same top-of-grid concentration our runs show, under
a different rule on different data.

**This row is therefore recorded as UNIDENTIFIED, not as an open gap to be
closed.** The paper publishes a selection procedure and no candidate set, and
the turnover row is reachable from within our grid — so a set that reproduces
the published US turnover of 141% (1.410 in the table below) certainly exists.
Finding it by search is the move AGENTS.md rule 5 forbids. Any
future change here needs a justification that could have been written before the
number was known, as adding k = 6 did.

**The spread, measured.** Eight candidate sets, none adopted, delay 1, all three
markets (artifacts/hmm-residual/08-grid-identification/). The table shows the
lowest and highest annual turnover the eight sets produced in each market, next
to the paper's Table 4 value:

| market | turnover across the eight sets | Table 4 | inside? |
|---|---|---|---|
| S&P 500 | 1.295 .. 2.913 | 1.410 | yes |
| DAX | 1.816 .. 2.432 | 2.460 | 0.028 above; bracketed by the fixed-k curve, so reachable |
| Nikkei | 2.751 .. 4.686 | 2.900 | yes |

The spread is several times the deviation under investigation in every market,
so this row carries no information about replication quality in either
direction.

**A set that gets the US to 8/8, and why it was not taken.** Dropping k = 0 —
`{2, 4, 6, 8, 20}` — puts the S&P 500 inside tolerance on all eight metrics
(turnover 1.442 against 1.410, total deviation 0.088). There is a real a priori
argument for it: the paper says it *applies* a median filter of window k, and a
window of zero applies none, exactly as Table 3 lists it beside lambda = 0 while
calling that column "equivalent to k-means clustering" — a reference point, not
a candidate. It is nonetheless **not adopted**, on two grounds. The argument was
noticed only after measuring that the 9% of months selecting k = 0 drive about
23% of our trading, so its ordering is contaminated: the reason came after the
number. And it does not generalise: Japan is unchanged and Germany gets slightly
worse. A rule that works in one market out of three is a fit, not a rule.

**And the rule chooses unstably across sub-samples, even with the set fixed.**
Splitting each 8-year validation window in half and comparing the argmax of each
half (the k that scored best on each half) gives agreement of 17.1% (us), 15.1%
(de) and 17.4% (jp) — the share of windows in which both halves picked the same
k.

> **Corrected 2026-08-06.** This paragraph used to compare those rates against
> "a chance rate of 16.7%" and to conclude that the rule "is not reproducible in
> principle". Both were retracted by
> `docs/audit/2026-07-29-codex-review-verdicts.md` §5 and the wording was never
> propagated here. 16.7% is one in six — the agreement rate if each half picked
> one of the six candidates uniformly at random (this 6 is the number of
> candidates, not a window k) — and the rule's choices are far from uniform
> (us: k20 33%, k8 29%, k6 21%, k0 9%, k4 6%, k2 1%). Using how often each half
> actually picks each k, the agreement rate you would expect if the two halves'
> picks were unrelated (the *independence baseline*) is **20.2% (us), 20.8%
> (de), 22.7% (jp)** — so observed agreement is *below* what unrelated picks
> would give, not merely at chance. The audit's instruction is explicit: "17.1%
> against chance 16.7%" must not be quoted again.

The selection rule is deterministic: identical data, code and grid always select
the same window, so nothing here makes it irreproducible. What is unstable is
the *estimate* — which candidate wins depends on which sample it is scored on.

Two limits of this split-half test belong with the number. A *control* is a
comparison whose right answer is known in advance. In a deterministic control —
two identical return paths, one handicapped by a constant 0.1 of Sharpe — the
two halves agree on the winner 100% of the time. In the realistic controls they
do not: comparing "always invested" against "always in cash", two strategies
that differ enormously, the two halves agree on the winner only 77% (us), 63%
(de) and 46% (jp) of the time. And two halves of a validation window are consecutive periods, not two draws
from one distribution, so if the best k genuinely drifts then disagreement is
signal rather than noise. The design cannot separate those.

What survives without any baseline argument: the median winning margin is
0.030-0.047 of Sharpe (the gap between the best and second-best candidate), about
a third of months are decided by less than 0.02, and the choice flips between
consecutive months 5.5%-7.2% of the time even though those two windows share
seven eighths of their data. Turnover is therefore unidentified twice over: the
candidate set is unpublished, and a Sharpe-ranked rule cannot pin down a
quantity that Table 3 shows moving from 8.5 to 2.0 shifts per year across the
same candidates.

**No set reproduces Table 4 in all three markets at once.** Scored on all eight
metrics rather than turnover alone, the best any of the eight achieves is 8/8
(us), 7/8 (de) and 7/8 (jp) — and by three different sets. Turnover also trades
against Sharpe: on the US, `dense_wide` reaches turnover 1.295 with Sharpe
0.598, `dense_small` reaches Sharpe 0.541 with turnover 1.501. There is a
frontier here, and the paper does not say where on it to stand.

---

## 4. Risk-free instrument for Germany and Japan — BOUNDED

The *risk-free rate* is the interest earned on cash when the strategy is out
of the market; it also sets the "excess" in excess return. The German and
Japanese cash rates in this project are each a *ladder*: several series spliced
end to end, each covering a stretch of the 1970-2023 window.

**What the paper says.**

> [line 155-157] "For the risk-free rates, we use the 3-month Treasury Bill Yield from each corresponding country, sourced from the Global Financial Data (GFD) database."

**What the paper does NOT say.** How GFD constructs those series back to 1970,
which matters because German Bubills and Japanese short bills did not trade
across the whole window. Their series is almost certainly itself a chain.

**What we chose.** Documented ladders: Germany OECD 3M interbank -> IMF IFS
T-bill -> ECB 3M AAA; Japan IMF IFS T-bill -> BoJ 3M call after 2017-06
(`scripts/data/build_external_sources.py`, splice deltas recorded in the config).

**Consequence, measured.** Swapping the US 1-month for the 3-month bill moves
features by 0.01 sigma (one hundredth of a standard deviation), flips the sign
of the signal on 0.57% of days, and shifts every Sharpe by 0.02-0.03 in the same
direction. A level effect, not an ordering effect: every Sharpe moves by a
similar amount in the same direction, so the comparison between models is
barely affected.

---

## 5. Comparison sample across models and delays — CLOSED in config, was open

**What the paper says.** Nothing about how rows are aligned across models and
delays when computing Table 4 — that is, which days are included when several
models and several signal delays are scored side by side.

**What we chose.** `comparison_sample =
per_market_all_delays_intersection_of_complete_metric_rows`
(the `comparison_sample` key, present in every sealed config; line 234 of the
comparator config). Read literally, the key name says: within each market, keep
only the rows whose metrics are complete across all delays.

**Consequence, measured.** The Japanese buy-and-hold Sharpe is 0.193 under this
frozen rule and 0.189 under a per-model sample. The audit ledger quoted 0.189,
i.e. a convention the run itself does not use. Any figure quoted from a run must
name its convention.

---

## 7. Turnover definition — CLOSED, the paper states it

Kept as a row so nobody re-opens it. The Table 4 caption (lines 747-753) names
"portfolio turnover" without defining it, and this project carried
`0.5 * sum|d weight|` annualised (half the sum of all absolute changes in
portfolio weight, scaled to a year) as an assumption for months. It is not an
assumption. One page later the paper gives the identity in words and numbers:

> [line 781-783] "turnover of the JM-guided 0/1 strategy applied to the S&P 500 is as low as 44%, meaning that on average, the portfolio manager buys and sells 44% of total allocation (a combined 88% trading) each year"

44% one way, 88% combined, denominator the entire allocation. `backtest.py:220-222`
computes exactly this. The phrase "of total allocation" on its own rules out
the readings that scale turnover by leverage.

Confirmed a second time, from four figure annotations that state a raw shift
count and a bear share for cells Table 4 also reports — lines 903, 829, 851,
873. Converting each count through the sample length and halving reproduces the
printed turnover to 0.002/0.001/0.007/0.013, and one minus the bear share
reproduces the printed leverage to within a point.

Those annotations are also **targets in their own right**, and counts are
sharper than ratios. Against v8.5, HMM: us 128 shifts against the published 96;
de 151 against 167 implied; jp 208 against 197 implied. The US bear share
(fraction of days labelled bear) is 29.1% against 27.8% — the same exposure
budget, a third more shifts inside it.

---

## 8. Drawdown basis — REOPENED 2026-07-29, the "pin" does not hold

A *drawdown* is how far a portfolio's value has fallen from its previous peak;
the *maximum drawdown* (MDD) is the worst such fall over the sample. The
*drawdown basis* is the question of which value path the drawdown is read
from: the whole portfolio including its cash earnings, or only the invested leg,
held flat while in cash. For a strategy that is sometimes fully in cash these
paths differ. Row 8a below once argued that two published facts "pinned" this
choice — fixed it without any fitting to Table 4. That argument is what this
row retracts.

> **This row was wrong and is retracted.** Fact 2 in row 8a misreads the caption it
> quotes. Figure 5's y-axis is *cumulative excess return* —
>
> > [line 786] "alongside the curves of cumulative excess returns from the three"
>
> — and a cumulative **excess** return curve is flat while in cash for the
> trivial reason that excess return is zero there. The flatness is implied by the
> axis label alone and carries no information about which path a drawdown is read
> from. Fact 1 stands but discriminates nothing relevant: buy-and-hold is never
> in cash, so `total_wealth`, `risky_leg_wealth_flat_in_cash` and its
> cost-retaining variant agree to every digit on all three control rows.
>
> With the pin gone, the only discriminating evidence is the four cells driven by
> Shu's own published positions — and there the two published rows disagree about
> the winner (by mean absolute error against the published cells, MDD prefers
> the cost-free flat path, 0.0072 against 0.0116, while Calmar prefers the
> cost-retaining one, 0.0030 against 0.0055). The selection
> in the since-deleted `scripts/probe_mdd_convention.py` was "whichever convention minimises error"
> against Table 4, which is exactly the search over an unspecified knob that
> `AGENTS.md` rule 5 forbids.
>
> A further objection to the adopted basis, independent of the fitting: it drops
> the 10bp trading cost from the drawdown path while the Return row charges it,
> so one Table 4 column would report return net of cost and drawdown gross of it.
>
> **What we do now.** `total_wealth` is the a-priori default again — the
> conventional reading of a portfolio drawdown, and what v8.x used. The
> flat-in-cash bases are reported as alternatives, not as the faithful choice.
>
> **What the retraction costs: nothing.** Rescored under both bases at the 0.05
> tolerance, every cell in all three markets gives the same verdict, and all
> three markets are 7/8 either way. See
> `artifacts/hmm-residual/01-status/hmm-vs-table4-v9-3.txt` and
> `docs/audit/2026-07-29-codex-review-verdicts.md` §2.

## 8a. The superseded argument, kept for the record

This is the argument row 8 retracts. It is kept so the reasoning can be
inspected; row 8 says which part of it fails.

**What the paper says.** Nothing directly. Table 4's caption defines the row as
"maximum drawdown ("MDD")" and stops there, and the return row above it is
labelled

> [line 747] "annualized performance metric: compound annual growth rate ("Return", including the risk-free rate),"

which tells us the *return* row credits the cash leg, and says nothing about
which path the drawdown is read from. For a 0/1 strategy (one that is either
fully invested or fully in cash) those are different paths, and the difference
is large: on the US HMM it is 5.9 percentage points.

**What settles it.** Two published facts, neither of which is a fit:

1. Table 4's buy-and-hold drawdowns (-55.2% / -72.7% / -79.1%) are reproduced to
   0.001 / 0.000 / 0.012 with the equity leg at total return, and missed by
   0.045 / 0.028 / 0.031 on any excess-return path. So the invested leg is total
   return.
2. The caption of Figure 5 says the shading marks days

   > [line 899-900] "when the JM-guided 0/1 strategy is fully invested in the risk-free asset, leading to a flat yellow curve."

   So the plotted strategy path is flat in cash: the cash leg contributes
   nothing.

Total return when invested plus nothing when in cash is a single basis, and it
is forced by those two statements rather than chosen to fit anything.

**What we did, v9.1 through v9.3** (superseded; v9.4 and v10 are back on
`total_wealth`): `[metrics] maximum_drawdown =
"risky_leg_wealth_flat_in_cash"`. Configs written before the field existed
default to `total_wealth`, so their sealed runs keep replaying to the numbers
they recorded.

**Why buy-and-hold could not settle it alone.** A portfolio that is never in
cash cannot be told apart by what the cash leg earns; its two columns agree to
every digit. The only cells that can decide are ones where the paper's own
positions are known, which is why Figures 5 and 6 were extracted.

**Consequence, measured.** Across ten cells — three buy-and-hold controls, our
three HMM paths, and four using Shu's own published positions — the mean
absolute drawdown error falls from 0.0330 to 0.0072 and the mean absolute Calmar
error (Calmar is annual return divided by maximum drawdown) from 0.0262 to
0.0055. The US HMM drawdown moves from -23.21% to -29.24% against the published
-28.9%, and its Calmar from 0.2666 to 0.2117 against 0.21. Full table in
docs/audit/2026-07-full-audit.md and artifacts/hmm-residual/06-mdd-convention/.

**Left unresolved.** Whether the drawdown path carries the 10bp trading cost.
Including it gives mean errors 0.0116 on MDD and 0.0030 on Calmar — better on
one row, worse on the other, and below what Table 4's printed precision can
separate. Recorded as unresolvable rather than decided.

---

## 9. The Japanese risk-free rate before 1990 — OPEN, measured, not acted on

**What the paper says.** The instrument is specified; the vendor's construction
is not:

> [line 155-157] "For the risk-free rates, we use the 3-month Treasury Bill Yield from each corresponding country, sourced from the Global Financial Data (GFD) database."

**The problem.** Japan had essentially no Treasury bill market before 1986, so
"the 3-month Treasury Bill Yield" for 1970-1986 is whatever the vendor decided
to splice. Ours is the IMF IFS Japan Treasury bill rate; the one independent
series in the repository, JST Macrohistory's `bill_rate`, sits systematically
above it. The table shows each series' level by period, in percent per year,
and the gap in percentage points (pp); how the period figure was computed is
not recorded here:

| period | ours | JST | gap |
|---|---|---|---|
| 1970-1979 | 5.25% | 7.27% | **-2.01pp** |
| 1980-1989 | 4.29% | 6.27% | **-1.98pp** |
| 1990-1999 | 2.05% | 2.74% | -0.70pp |
| 2000-2020 | 0.10% | 0.07% | +0.03pp |

Correlation 0.9723 — the shape agrees, the level does not. JST's 1974 peak of
12.5% matches the Japanese call rate (the overnight rate banks lend to each
other at); ours looks like an administered rate (one set by policy rather than
by trading).
Neither is wrong; they are different instruments, and the paper's source made a
third choice we cannot see.

**Consequence, measured — and NOT separately identified.** Our annualised mean
excess return for Japanese buy-and-hold is 0.0305 against the 0.0281 implied by
Table 4's Sharpe times its volatility: a gap of 0.245pp/year. Substituting JST's
rate removes 0.18pp of it and moves the buy-and-hold Sharpe from 0.1306 to
0.1228 against the published 0.12. But our equity CAGR (compound annual growth
rate of the index itself) is also 0.20pp above the published 0.8%, and the two
candidates sum to more than the gap, so neither can be named as the cause. An
earlier draft of this row called the rate "the leading explanation"; that is
withdrawn.

**Not acted on.** That number was obtained by comparing against the target, so
switching on the strength of it is fitting to the answer. The row is recorded as
open and bounded: the Japanese risk-free level carries about a 2pp ambiguity
before 1990 and 0.7pp through the 1990s, and Japanese Sharpe figures inherit
roughly 0.008 of uncertainty from it. Any future change needs a justification
that could have been written before the comparison was run.

**Germany is not exposed the same way.** Its first ladder segment is an interbank
rate (a rate banks charge each other), which carries a credit spread, but it
ends in 1975-06 and so only touches the warm-up, never a training window that
produces a reported signal.

---

## 10. hmmlearn estimation constants — BOUNDED by structural identity, spread unmeasured

`hmmlearn` is the software library that fits the HMM. Fitting starts from an
initial guess and improves it step by step; the library has several numerical
settings that control that process and that the paper never mentions.

**What the paper says.** The stack and the restart rule, and nothing finer:

> [line 371] "we execute the algorithm ten times from"

different k-means++-derived initial values, retaining the highest
log-likelihood (that is, ten starting guesses, keeping the fit that explains
the data best); and

> [line 382] "On the training window ending at day t, we use the Viterbi algorithm to decode the hidden"

state sequence (Viterbi is the standard method for reading the most likely
regime sequence out of a fitted HMM). It does not name min_covar, priors,
iteration cap or convergence tolerance.

**What we chose (sealed v9.4).** min_covar 1e-3 (the hmmlearn default),
covars_prior 0.0, transmat_prior 1.0, n_iter 1000, tol 1e-6 with a symmetric
strict-convergence gate. In plain terms: a floor on how small a variance may
get, no pull toward a prior guess on the variances or transition probabilities,
up to 1000 improvement steps, and a strict stopping test at tolerance 1e-6.

**The author-code point of comparison (not the paper).** Shu's 2023 simulation
codebase (`continuous-jump-model`, see the 2026-07-30 round-2 audit note) is
structurally identical — same init_params set, same 10× k-means++ restart rule,
same Viterbi `.predict()` decoding — and differs only in five constants:
min_covar 1e-6, covars_prior 1e-6, transmat_prior 1+1e-5, n_iter 500, tol 1e-4.
Both parameterizations are near-MLE (zero or ~1e-6 pseudo-counts, meaning
almost no pull toward a prior guess), so a priori they should reach the same
local optima under our stricter convergence gate. That is an expectation, not a
measurement.

**Not adopted, spread unmeasured.** These are example-code defaults from a
different study, exactly the class of artifact that must not be promoted into
claims about the paper (standing owner rule, see row 1's note), and switching to
them now — after knowing our turnover sits above the target — would be searching
a knob near the answer. The row exists so the axis is on the books: if a spread
measurement is ever wanted, it needs its own frozen question first. Until then
this row's honest status is: sensitivity unknown, prior expectation small.

---

## Do not report confidence intervals in this project

Standing instruction from the owner, and it is the right call. A confidence
interval is a range around an estimate that is meant to cover the true value
most of the time under repeated sampling. Intervals were used here as if
covering the paper's value were evidence of replication, which it never was:
the paper publishes one number per cell with no standard error, on licensed
data we do not hold, so there is no sampling distribution to test against and
no hypothesis to reject. On top of that, at this sample length an interval on a
Sharpe ratio is wide enough that the buy-and-hold cell covered the paper's
jump-model figure as well as its own — a test that cannot separate the three
models it is asked about is not a test.

The arithmetic that was published here to make that point was itself wrong: it
applied the Lo (2002) standard error with an annualised Sharpe and a sample size
counted in years, mixing two frequencies. It is retracted along with the rest.

Report instead:

- **Closeness of the point estimate** to the paper, against a tolerance fixed in
  advance. The owner's standing tolerance is 0.05 absolute Sharpe, tightening to
  0.03. Count model cells separately from buy-and-hold: buy-and-hold contains no
  model, so it measures the data, not the replication.
- **All eight rows of Table 4, not the Sharpe row alone.** Turnover is the
  paper's own headline property of the jump model ("as low as 44%"), and it is
  where the current run diverges most.
- **The spread across our own free choices**, which is what the rows above
  measure. That spread is the honest uncertainty statement for a replication: it
  says how much of the gap we could produce ourselves by setting an unspecified
  knob differently.

## Maintenance

Add a row whenever a decision is made that the paper does not force. Record the
quote that shows the paper is silent, the choice, and the measured spread. A row
without a measured spread is an admission that the sensitivity is unknown.

---

## 6. Sample start, and the Japanese Saturday gap — DEVIATION, measured

**What the paper says.** This one is specified, which is why the row is a
deviation rather than a free parameter:

> [line 157] "All data spans from the start of 1970 to the end of 2023."

**What we do.** `requested_sample_start = "1969-05-01"` (v8.4, v8.5) — eight
months earlier than the paper's stated start.

**Why.** Not fidelity. Compensation for a data gap. The Tokyo exchange traded
Saturdays until January 1989 and our `^N225` series contains zero Saturday
sessions, so our 3000-session training window spans about eighteen months more
calendar time than Shu's. Starting literally at 1970-01-01 pushes the realised
out-of-sample start (the first day on which a reported signal exists) to
1990-03-15 (us), 1990-06-19 (de) and 1990-09-17 (jp), discarding the first nine
months of 1990 in Japan.

Earlier config comments described this as restoring "the paper's 1990-01-02
anchor". The paper names no such date; every mention of 1990 in it is a year.
That description is withdrawn (docs/audit/2026-07-full-audit.md).

**Consequence, measured.** On the overlapping days, the HMM is exactly
invariant to this choice — 0 differing states out of 10,619 / 10,605 / 10,282
day-states in us / de / jp — because it fits the last 3000 log returns before
each day and that set does not depend on where the series began. The jump model
is not: 3.71% (us), 1.10% (de) and 15.84% (jp) of state cells differ, through
the expanding standardiser anchor of row 1 above (the standardiser's mean and
spread depend on where the history starts).

Against buy-and-hold, which contains no model and so tests the window itself:
us 0.486 against 0.497, de 0.298 against 0.305, jp **0.138 against 0.193**
(buy-and-hold Sharpe under the two sample starts), with Shu at
0.48 / 0.30 / 0.12. The backdated window reproduces the reported period; the
literal one does not.

**Open.** The choice is not free for the jump model. On the shared window it
costs the US JM 0.088 Sharpe and moves its turnover from 0.636 to 1.006 against
Shu's 0.44 — away from the paper on the row the paper treats as the jump model's
identifying property. Reopen before the next JM freeze; do not inherit silently.

---

## 11. Which two calendar months anchor the semiannual JM refit — OPEN, spread unmeasured

A *refit* is the moment the jump model's parameters are re-estimated on the
latest training window. The paper refits twice a year but never says in which
months.

**What the paper says.** The cadence, and only the cadence:

> [line 544] "In our JM implementation, the optimal model parameters Θ̂ are updated every six months by"

Figure 3's caption repeats it for the illustration:

> [line 612] "a 3000-day training window that moves forward every six months. Each date on the x-axis represents the"

**What the paper does NOT say.** Which two months. "Every six months" fixes the
interval, not the phase. Nothing in the paper names a refit date, and Figure 4's
in-sample window is described only as "ending at the end of 2020".

**What we chose.** `refit_months = [1, 7]` — January and July
(`config.py:_jm_protocol`, frozen to that literal in every contract). In the
sealed v10 run this lands on the first trading day of each January and July,
plus one initial fit on the first day that has enough history behind it.

**Consequence.** Unmeasured. Six phases are possible ([1,7] through [6,12]);
each shifts every refit date by up to five months, which moves the parameters
Θ̂ that every subsequent day's online inference is conditioned on. The
mechanism is the same one row 1 measures for standardization geometry, so a
material spread cannot be ruled out a priori.

**Not measured here on purpose.** Sweeping the phase means running the
walk-forward (the full day-by-day simulation) six times and comparing against
numbers we already know, which is exactly the search this file exists to
forbid. If the sensitivity is wanted it needs its own frozen question, written
before the six runs, that says what a large spread would mean.

---

## 12. Sharpe denominator — CLOSED by the paper's own caption, deviation measured and immaterial

**What the paper says.** Table 4's caption defines the reported statistic:

> [line 751] "Sharpe ratio (average excess return over volatility)"

and the selection objective is the same statistic:

> [line 710] "We then select the value λ̂ that yields the highest Sharpe ratio"

**What the paper does NOT say.** Whose volatility — the strategy's, or the
excess series'. For a 0/1 strategy that sits in cash part of the time these are
different series, so the caption admits two readings.

**What we chose.** `mean(strategy − cash) / std(strategy)`, i.e. excess return
in the numerator and **total strategy** volatility in the denominator
(`backtest.py:annualized_excess_sharpe`, pinned as
`sharpe_denominator = "strategy_return_volatility"`). The textbook Sharpe uses
`std(strategy − cash)` in both places. The caption's wording — "average excess
return over volatility", not "over excess volatility" — reads slightly toward
ours, but it does not settle it.

**Consequence, measured.** Recomputed both conventions on all nine delay-1 rows
of the sealed v10 baseline (`fixed-baselines-36ca1ace131c-…`): the two
definitions differ by at most **0.000037** of Sharpe and 0.000023 on average
(largest cell: jp fixed_jm, 0.290783 against 0.290746). That is three orders of
magnitude below the 0.05 reporting tolerance, because daily cash returns are
tiny and almost constant. The row is recorded for completeness, not as a live
uncertainty.


---

## 13. EWM warm-up rows inside the expanding standardiser — OPEN, measured, undisclosed until 2026-08-06

An *EWM* (exponentially weighted moving) statistic is an average that gives
recent days more weight than old ones; its *halflife* is how many days it takes
for a day's weight to fall by half. The first rows of such a series — the
*warm-up* — are built from only a handful of observations, so they are
unreliable until enough history has accumulated.

**What the paper says.** Nothing. The features are EWM statistics and the paper
never states a burn-in (a number of early rows to discard):

> [line 504] "expectation is based on exponentially decaying weights over historical periods"

**What we chose.** `make_features` emits features from the very first rows
(`min_periods=0`, `burn_in_observations = 0`), so a "60-day-halflife" Sortino
exists from four observations — US rows 3-7 read 2.6, 3.3, 2.7, 1.6, 2.1
against a mature p1/p99 of -0.32/+0.62 (the 1st and 99th percentiles once the
series has settled). `standardize_expanding` then drops the first 63 rows from
its *output* but keeps them in its *statistics* forever: the unreliable early
values never appear as features, but they stay inside the mean and standard
deviation used to scale every later row.

**Consequence, measured (2026-08-06 audit).** At US row 3063 (the audit
records only the row number; whether rows are counted from 0 or from 1 is not
recorded), the expanding standard deviation of `sortino_60` is 43.4% larger,
and its mean 8.9% larger, than they would be if the first 63 rows had been
discarded (a 63-row burn-in). In the
fit window ending 1990-01-04 the per-feature stds are [1.50, 0.79, 0.63]
(anisotropy 2.39x) against [1.50, 0.89, 0.86] (1.75x) with a burn-in — so part
of the anisotropy row 1 attributes to the expanding geometry is actually
warm-up contamination. Over the OOS (out-of-sample) sample the US `sortino_60`
z-score (the standardised feature value) moves by mean 0.109 sigma, max 0.612
sigma (jp 0.039/0.220, de 0.011/0.052).

**Bounded where tested.** Refitting the JM on that window under both variants
changes 0 of 3000 in-sample states (us, lambda 21.54) and 3 of 3000 (jp,
lambda 10); centroids and objective move (us 3097.5 -> 3821.6). A full
walk-forward under a feature burn-in has not been run and would need its own
frozen question; do not run it casually against known targets.

---

## 14. Daily risk-free conversion — OPEN, bounded, undisclosed until 2026-08-06

The risk-free rate is published as an annual percentage; the backtest needs a
daily amount. The paper does not say how to convert one into the other.

**What the paper says.** The instrument only:

> [line 155-157] "For the risk-free rates, we use the 3-month Treasury Bill Yield from each corresponding country, sourced from the Global Financial Data (GFD) database."

No day count, no compounding rule (`scripts/audit/check_paper_claims.py` machine-checks
that 252/365/360/day-count never appear in the body).

**What we chose.** `annual_percent / 100 / 252`, simple and uncompounded,
accruing on trading days only (`features.py:81-83`). That is, the annual rate is
divided evenly over 252 trading days and no interest is earned on interest.

**Bounds, measured.** Compounded daily conversion would credit cash ~13 bp/yr
(basis points per year; 100 bp = 1%) less at the sample-mean 4.47% yield.
Actual/365 accrual (counting every calendar day, including weekends) moves
Monday excess returns by ~2 bp (cancels over a year). Separately, the US source
DTB3 is a discount-basis quote while the paper says "Yield": a bond-equivalent
conversion would raise the mean risk-free by ~14.4 bp/yr and lower every excess
return by the same. All are level effects far below the 0.05 Sharpe tolerance;
recorded so the axis is on the books.

---

## 15. The paper's printed DD formula omits its square root — CLOSED against the printed text

**What the paper prints.** DD is downside deviation, the feature that measures
how large the negative excess returns have been.

> [line 501] "Downside deviation, calculated as E R2 1{R<0} where R denotes the excess return and the"

— literally the second lower partial moment, no radical. In plain terms, the
printed formula is the average of the squared negative returns, with no square
root taken, which would leave it in squared units.

**What the code does.** `features.py:100-107` takes the square root.

**Why the code is right and the printed formula is the typo.** Four independent
checks, none of them our fit:

1. The paper itself says scaling DD by sqrt(2) puts it on the volatility scale
   [line 614-615]. That is true only with the root; a second moment would need
   a factor of 2.
2. Measured on the sealed US frame, sqrt(2)*sqrt(252)*dd_10 has mean 15.1%
   against a realised annualised excess volatility of 18.1%, so the caption's
   claim holds numerically. The un-rooted version gives 1.7%.
3. Figure 3's DD panel is drawn on a 20%-80% axis, which fits the rooted
   centroids (the model's per-regime average feature values) and cannot fit
   1.7-5%.
4. Shu's dissertation states the root explicitly
   (docs/audit/2026-07-30-jm-deep-research.md:19).

**Do not "fix" the code to match line 501.**
