---
name: claim-check
description: Build a claim ledger for changed research claims before a research PR or a durable-document update. Manually invoked only.
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash
---

# /claim-check — find the evidence boundary before the claim ships

This pass is read-only. Produce a ledger. Do not rewrite research claims, run
experiments, refit anything, or touch data.

Governing rule (`CLAUDE.md`, Evidence ceiling): a written claim may be weaker
than the evidence, never stronger.

## What to inspect

Default target: claims changed on this branch.

```bash
git diff main...HEAD -- '*.md'
```

If the user names files or a revision range in the arguments, use that instead.
Durable documents are `README.md`, `CURRENT.md`, `SUMMER_2026.md`, `AGENTS.md`,
`CLAUDE.md` and everything under `docs/`. A claim sentence is any added or
modified line that asserts something about the research: a number, a
comparison, a state of the repository, a property of a result, or a check.

## Procedure

1. **List the changed claim sentences.** Quote each one with `file:line`.
2. **Find the evidence for each.** Open the artifact, script, test, receipt or
   paper line it rests on. A claim's own wording is not evidence for itself,
   and neither is another document repeating it.
3. **Test reproducibility from a fresh checkout** for every evidence path:
   ```bash
   git ls-files --error-unmatch <path>   # tracked?
   git check-ignore -v <path>            # ignored?
   ```
   Untracked or ignored evidence is local-only.
4. **Write one ledger entry per claim** in the format below.
5. **Stop.** Report which claims sit above their evidence ceiling and wait for
   the owner to decide what to do. Do not edit them in this pass.

## Ledger entry format

```
CLAIM:        "<quoted sentence>"  (file:line)
EVIDENCE:     <exact path / command / receipt> — what it actually shows
TYPE:         direct fact | derived fact | inference | unknown
UNIT + SCOPE: what is counted, its unit, its denominator, and the market,
              sample, model, settings and run it applies to
REPRODUCIBLE FROM FRESH CHECKOUT?  yes | no (local-only: <path>)
SAFE WORDING: the strongest sentence the evidence supports
              (or: already at ceiling)
```

## Always challenge these

- **Every important number.** 11 of what, out of how many, in what unit, from
  which run? Is the counted object the one the sentence names — days, or
  (lambda, day) pairs?
- **Superlatives and absolutes**: all, only, none, never, always, largest,
  best, first, every. Was the whole scope enumerated, or only the part that was
  searched?
- **Causal, intentional and optimality language**: caused, because,
  attributable, drives, wants, prefers, optimal, converged. A measurement alone
  supports none of these.
- **Behaviour outside the tested range.** "The largest tested value won" says
  nothing about untested larger values.
- **Comparisons and ratios across different footing.** Before "N times larger"
  or "the largest in the project", state both sides' market, sample, model,
  settings and run — and whether either side is the maximum of a set or one
  result out of many.
- **Negative claims**: "nothing else", "no other", "none remain", "and only".
  Enumerate the full scope, or narrow the sentence to what was enumerated.
- **Claims sourced only from ignored or local artifacts.** Exact numbers quoted
  from a gitignored file cannot silently support a durable verified claim; they
  must be labelled local-only, or the artifact must be committed.
- **"verified / validated / correct / independent / reproduced / proven".**
  Name the exact check that ran and what it leaves unchecked (`AGENTS.md` 7 and
  11). A passing test suite is not proof of a research conclusion
  (`AGENTS.md` 9), and a second Claude pass is not an independent check
  (`AGENTS.md` 8).
- **Vague summaries that replaced exact evidence.** If the source has an exact
  count, the document should carry it or say why it does not.

## Output

A ledger, then a short list under two headings: **claims to narrow** and
**claims that are already at their ceiling**. Nothing else changes in this pass.
