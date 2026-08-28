"""Every published data snapshot must match what it claims to be a copy of.

`data/snapshots/<id>/` is archival evidence: the exact bytes one sealed run
read. The live inputs stay at their ignored paths (`data/external/`,
`data/raw/`, `data/processed/`) and nothing in the research code reads a
snapshot. Four checks, in order of what a checkout can see:

1. every file listed in the snapshot's `SHA256SUMS` hashes to that value;
2. the `external/` series hash to the `sha256` pins of the config the
   snapshot names (the config is tracked, so this runs on a clean checkout);
3. the `raw/` and `processed/` copies hash to what the snapshot's own
   acquisition manifest recorded;
4. where a live input exists at the corresponding ignored path, its bytes
   equal the snapshot's -- otherwise that comparison is skipped and says so.

A pass proves the snapshot is a faithful copy. It does not prove the data is
right, and it does not prove the sealed run's results.
"""

from __future__ import annotations

import hashlib
import json
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = ROOT / "data" / "snapshots"
SNAPSHOT_DIRS = (
    sorted(p for p in SNAPSHOTS.iterdir() if p.is_dir()) if SNAPSHOTS.is_dir() else []
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sums(snapshot: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in (snapshot / "SHA256SUMS").read_text().splitlines():
        digest, _, name = line.partition("  ")
        entries[name] = digest
    return entries


def _meta(snapshot: Path) -> dict:
    return json.loads((snapshot / "snapshot.json").read_text())


def _manifest(snapshot: Path) -> dict:
    meta = _meta(snapshot)
    path = snapshot / "raw" / meta["acquisition_run_id"] / "manifest.json"
    return json.loads(path.read_text())


@pytest.mark.parametrize("snapshot", SNAPSHOT_DIRS, ids=lambda p: p.name)
def test_snapshot_files_match_their_checksums(snapshot: Path) -> None:
    sums = _sums(snapshot)
    listed = set(sums)
    present = {
        str(p.relative_to(snapshot))
        for p in snapshot.rglob("*")
        if p.is_file() and p.name not in {"SHA256SUMS", "README.md", "snapshot.json"}
    }
    assert listed == present, f"SHA256SUMS and directory disagree: {listed ^ present}"
    for name, digest in sums.items():
        assert _sha256(snapshot / name) == digest, f"{snapshot.name}/{name} changed"


@pytest.mark.parametrize("snapshot", SNAPSHOT_DIRS, ids=lambda p: p.name)
def test_snapshot_external_series_match_config_pins(snapshot: Path) -> None:
    meta = _meta(snapshot)
    config_path = ROOT / meta["config_path"]
    assert _sha256(config_path) == meta["config_sha256"], "named config changed"
    document = tomllib.loads(config_path.read_text())
    pinned: dict[str, str] = {}
    for market in document["markets"]:
        for kind in ("equity", "cash"):
            source = market[kind]
            if source.get("provider") == "localfile":
                pinned[Path(source["file_path"]).name] = source["sha256"]
    external = {p.name: _sha256(p) for p in (snapshot / "external").iterdir()}
    assert external == pinned, "external/ does not match the config's localfile pins"


@pytest.mark.parametrize("snapshot", SNAPSHOT_DIRS, ids=lambda p: p.name)
def test_snapshot_run_copies_match_their_manifest(snapshot: Path) -> None:
    meta = _meta(snapshot)
    manifest = _manifest(snapshot)
    assert manifest["run_id"] == meta["acquisition_run_id"]
    assert manifest["config_sha256"] == meta["config_sha256"]
    raw_manifest = snapshot / "raw" / meta["acquisition_run_id"] / "manifest.json"
    assert _sha256(raw_manifest) == meta["manifest_sha256"]
    for source in manifest["sources"]:
        for record in (source["raw"], source["canonical"]):
            # e.g. data/processed/<run>/jp_equity.csv
            live_relative = Path(record["path"])
            copy = snapshot / Path(*live_relative.parts[1:])
            assert copy.is_file(), f"snapshot is missing {live_relative}"
            assert _sha256(copy) == record["sha256"], (
                f"{live_relative} differs from manifest"
            )
            assert copy.stat().st_size == record["bytes"]


@pytest.mark.parametrize("snapshot", SNAPSHOT_DIRS, ids=lambda p: p.name)
def test_snapshot_equals_live_inputs_where_present(snapshot: Path) -> None:
    meta = _meta(snapshot)
    compared = 0
    for name in _sums(snapshot):
        parts = Path(name).parts  # ("external", file) or ("raw"/"processed", run, file)
        live = ROOT / meta["live_paths"][parts[0]] / Path(*parts[1:])
        if not live.is_file():
            continue
        compared += 1
        assert live.read_bytes() == (snapshot / name).read_bytes(), (
            f"live {live.relative_to(ROOT)} differs from snapshot "
            f"{snapshot.name}/{name}; the local input is not the sealed one -- "
            "compare before replacing either"
        )
    if compared == 0:
        pytest.skip(
            f"{snapshot.name}: no live inputs present in this checkout to compare"
        )
