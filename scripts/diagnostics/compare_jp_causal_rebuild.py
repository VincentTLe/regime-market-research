"""How much did the causal Nikkei series move the sealed baseline?

Compares two completed fixed-baselines runs that differ only in the Japanese
equity input: the sealed v11-ninit60 run and the calibrated-reconstruction-v11
rerun (registry jp-causal-rebuild-001, frozen before this was executed).
Reports every quantity the FROZEN row lists, as measured, with no threshold.

Diagnostic only. Adopts nothing, reranks nothing, changes no config.

    python scripts/diagnostics/compare_jp_causal_rebuild.py OLD_RUN NEW_RUN
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts" / "jp-causal-rebuild"
DELAYS = (1, 5, 10)
METRICS = ("sharpe", "maximum_drawdown", "turnover")
MODELS = ("fixed_jm", "hmm", "buy_and_hold")


def _states(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["date"]).set_index("date")


def _differing_days(old: pd.Series, new: pd.Series) -> tuple[int, int]:
    """(days where both are defined and differ, days where both are defined)."""
    both = old.notna() & new.notna()
    if not (old.isna() == new.isna()).all():
        raise SystemExit(
            "coverage differs between runs; not a like-for-like comparison"
        )
    return int((old[both] != new[both]).sum()), int(both.sum())


def compare(old_run: Path, new_run: Path) -> tuple[list[dict], list[str]]:
    rows: list[dict] = []
    lines: list[str] = []

    # (a) US and DE must be byte-identical: only the jp input changed.
    old_inv = json.loads((old_run / "inventory.json").read_text())["files"]
    new_inv = json.loads((new_run / "inventory.json").read_text())["files"]
    for market in ("us", "de"):
        keys = sorted(k for k in old_inv if k.startswith(f"{market}/"))
        same = sum(1 for k in keys if new_inv.get(k) == old_inv[k])
        rows.append(
            {
                "item": f"{market} inventory files identical",
                "old": len(keys),
                "new": same,
            }
        )
        lines.append(f"(a) {market}: {same} of {len(keys)} files hash-identical")

    # (b) jp HMM states, (c) jp JM states per lambda.
    old_h, new_h = (
        _states(old_run / "jp/hmm-states.csv"),
        _states(new_run / "jp/hmm-states.csv"),
    )
    diff, total = _differing_days(old_h["hmm_state"], new_h["hmm_state"])
    rows.append({"item": "jp hmm-states differing days", "old": total, "new": diff})
    lines.append(f"(b) jp HMM state differs on {diff} of {total} defined days")
    old_j, new_j = (
        _states(old_run / "jp/jm-states.csv"),
        _states(new_run / "jp/jm-states.csv"),
    )
    if list(old_j.columns) != list(new_j.columns):
        raise SystemExit("jp lambda grids differ between runs")
    for lam in old_j.columns:
        diff, total = _differing_days(old_j[lam], new_j[lam])
        rows.append(
            {
                "item": f"jp jm-states lambda={lam} differing days",
                "old": total,
                "new": diff,
            }
        )
        lines.append(f"(c) jp JM state at lambda {lam}: {diff} of {total} days differ")

    # (d) selected lambda per month, (e) traded position per day, per delay.
    for delay in DELAYS:
        sub = f"jp/fixed_jm-delay-{delay}"
        old_c = pd.read_csv(old_run / sub / "choices.csv").set_index("decision_date")[
            "selected"
        ]
        new_c = pd.read_csv(new_run / sub / "choices.csv").set_index("decision_date")[
            "selected"
        ]
        if not old_c.index.equals(new_c.index):
            raise SystemExit(f"decision dates differ at delay {delay}")
        months = int((old_c != new_c).sum())
        rows.append(
            {
                "item": f"jp delay-{delay} months with different lambda",
                "old": len(old_c),
                "new": months,
            }
        )
        lines.append(
            f"(d) jp delay {delay}: selected lambda differs in {months} of "
            f"{len(old_c)} months"
        )
        old_s = _states(old_run / sub / "selected-signal.csv")["selected_signal"]
        new_s = _states(new_run / sub / "selected-signal.csv")["selected_signal"]
        diff, total = _differing_days(old_s, new_s)
        rows.append(
            {
                "item": f"jp delay-{delay} fixed_jm signal differing days",
                "old": total,
                "new": diff,
            }
        )
        lines.append(
            f"(e) jp delay {delay}: fixed-JM signal differs on {diff} of {total} days"
        )
        old_s = _states(old_run / f"jp/hmm-delay-{delay}/selected-signal.csv")[
            "selected_signal"
        ]
        new_s = _states(new_run / f"jp/hmm-delay-{delay}/selected-signal.csv")[
            "selected_signal"
        ]
        diff, total = _differing_days(old_s, new_s)
        rows.append(
            {
                "item": f"jp delay-{delay} hmm signal differing days",
                "old": total,
                "new": diff,
            }
        )
        lines.append(
            f"(e) jp delay {delay}: HMM signal differs on {diff} of {total} days"
        )

    # (f) jp metrics.
    old_m = pd.read_csv(old_run / "metrics.csv")
    new_m = pd.read_csv(new_run / "metrics.csv")
    key = ["market", "model", "delay"]
    merged = old_m.merge(new_m, on=key, suffixes=("_old", "_new"))
    jp = merged[merged["market"] == "jp"]
    for model in MODELS:
        for delay in DELAYS:
            cell = jp[(jp["model"] == model) & (jp["delay"] == delay)]
            if cell.empty:
                continue
            for metric in METRICS:
                o, n = (
                    float(cell[f"{metric}_old"].iloc[0]),
                    float(cell[f"{metric}_new"].iloc[0]),
                )
                rows.append(
                    {"item": f"jp {model} delay-{delay} {metric}", "old": o, "new": n}
                )
                lines.append(
                    f"(f) jp {model} delay {delay} {metric}: "
                    f"{o:.6f} -> {n:.6f} ({n - o:+.6f})"
                )
    others = merged[merged["market"] != "jp"]
    moved = int(sum((others[f"{m}_old"] != others[f"{m}_new"]).sum() for m in METRICS))
    rows.append(
        {
            "item": "us/de metric cells that moved",
            "old": int(len(others) * len(METRICS)),
            "new": moved,
        }
    )
    lines.append(
        f"(f) us/de: {moved} of {len(others) * len(METRICS)} metric cells moved"
    )

    # (g) the directional gate.
    for label, run in (("old", old_run), ("new", new_run)):
        claim = json.loads((run / "claim.json").read_text())
        jp_gate = next(m for m in claim["markets"] if m["market"] == "jp")
        lines.append(
            f"(g) {label} claim.json: overall passed={claim['passed']}, "
            f"jp passed={jp_gate['passed']}"
        )
    return rows, lines


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    old_run, new_run = Path(argv[1]).resolve(), Path(argv[2]).resolve()
    rows, lines = compare(old_run, new_run)
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / "summary.csv", index=False)
    header = [f"old run: {old_run.name}", f"new run: {new_run.name}", ""]
    (OUT / "summary.md").write_text("\n".join(header + lines) + "\n")
    print("\n".join(header + lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
