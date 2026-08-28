# How to read the receipts in this folder

These files are historical records. Per `AGENTS.md`, they are not rewritten to
look current; this note is the only thing added on 2026-08-28. Read a receipt
only to check the specific old claim it covers, and read it with these four
facts in hand.

**1. "Independent" in a receipt means a different AI agent, not independent
validation.** Nine receipts call themselves "independent verification
receipts", and many say "independent auditor" or "adversarial verification".
In every case the checker was another AI session (a separate Claude or Codex
agent that had not written the code). `AGENTS.md` rules 8 and 11 now say that
AI review is not independent scientific validation. Read those words as "a
second pass by a different agent".

**2. Most paths have moved.** The receipts cite files where they lived in
July–August 2026. Today:

| cited as | now at |
|---|---|
| `research/<name>.toml` | `research/contracts/<name>.toml` |
| `scripts/build_*.py`, `scripts/fetch_*.py` | `scripts/data/` |
| `scripts/probe_*.py`, `scripts/run_*.py`, `scripts/diagnose_*.py`, `scripts/optimizer_fidelity_l4.py`, `scripts/studentized_sharpe_difference.py` | `scripts/experiments/` or `scripts/diagnostics/` |
| `scripts/gate_v10_reseal.py`, `scripts/audit_heldout_recompute.py`, `scripts/verify_replication_atlas.py`, `scripts/render_replication_atlas.py` | `archive/scripts/` |
| `scripts/check_paper_claims.py` | `scripts/audit/check_paper_claims.py` |
| `artifacts/hmm-residual/v9-*-hmm/` | `artifacts/hmm-residual/superseded-caches/` |
| `configs/baselines/research-calibrated-v11.toml` | `configs/baselines/legacy/` |

**3. Some evidence is gone.** These cited files exist nowhere in the tree:
`scripts/probe_mdd_convention.py`, `scripts/validate_jm_headline_grids.py`,
`scripts/audit_data_1970.py`, `scripts/cache_v9_3_us_hmm.py`,
`src/adaptive_jump/holdout_runner.py`, `data/vintage`. And these cited
artifacts are gitignored and no longer on the owner's machine either:
`artifacts/data-audit/`, `artifacts/data-verification/`,
`artifacts/heldout-delay/`, `artifacts/dense-menu/`, `docs/atlas/` (the
replication atlas itself), the v8.x/v9.x run directories, and
`data/raw/shu-replication-expanding-v9-3-…`. A number that rests only on one
of those is a recorded value, not a re-checkable one.

**4. Several receipts describe a baseline that has since been replaced.**
`2026-07-31-baseline-reseal-v10.md` → replaced by v11 (2026-08-08);
`2026-08-08-baseline-reseal-v11-receipt.md` (first v11 seal, n_init=10) →
replaced the same day by v11-ninit60; both → replaced on 2026-08-28 by
`calibrated-reconstruction-v11` (`2026-08-28-jp-causal-rebuild-receipt.md`).
`2026-08-07-grid-selection-rule-001-receipt.md` (n_init=10) is qualified by
`2026-08-08-grid-selection-rule-001-ninit60-receipt.md`. `CURRENT.md` says
which baseline is current.

Which receipts still carry weight today: the claim checker
(`scripts/audit/check_paper_claims.py`) verifies 21 of its 43 paper
quotations from six of these files (`2026-07-full-audit.md`,
`2026-08-07-jm-replication-atlas.md`, `2026-07-29-codex-review-verdicts.md`,
`2026-07-30-deep-research-round2.md`, `2026-07-30-self-audit.md`,
`2026-07-31-jm-effective-lambda-inversion.md`); `CURRENT.md` cites the
ninit60 grid receipt and the 2026-08-28 receipt; `docs/unspecified-choices.md`
and `docs/data-provenance.md` cite the full audit, the two deep-research
notes and the Codex verdicts. The other receipts are history only.
