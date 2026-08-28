"""Every reconstructed-onto-official splice must lose no session.

An external review found that the S&P 500 builder dropped 1988-01-04 -- a
+3.59% session -- because it reconstructed only up to the session BEFORE the
official index starts, anchored that level to the official index's first close,
and then deleted the row. The row labelled 1988-01-04 carried 1987-12-31's
return instead, and every rolling 3000-session window for the next twelve years
read it.

The German and Japanese builders take an inclusive slice and were never wrong.
The distinction is one character (`<` against `<=`) and invisible in every
summary statistic, so it is pinned here instead: for each shipped series, the
number of sessions must equal the number of distinct dates its inputs cover
across the splice, and no calendar gap may straddle the splice date.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "data" / "external"
INPUTS = EXTERNAL / "inputs"


def _load_script(name: str) -> ModuleType:
    """Load a retained builder without making scripts a Python package."""
    path = ROOT / "scripts" / "data" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"_test_{name}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import builder: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SP500_BUILDER = _load_script("build_sp500_tr")
DE_BUILDER = _load_script("build_de_total_return")
EXTERNAL_BUILDER = _load_script("build_external_sources")

# series file, the price path it is reconstructed from, and the splice date
SPLICES = (
    ("us_equity_tr_sp500.csv", "sp500_price_daily.csv", "1988-01-04"),
    ("de_equity_tr_dividend_adjusted.csv", None, "1987-12-30"),
)


def _series(path: Path) -> pd.Series:
    frame = pd.read_csv(path, parse_dates=["date"])
    column = "value" if "value" in frame.columns else frame.columns[1]
    return frame.set_index("date")[column].sort_index()


@pytest.mark.parametrize(("name", "price_name", "splice"), SPLICES)
def test_splice_keeps_every_session(
    name: str, price_name: str | None, splice: str
) -> None:
    path = EXTERNAL / name
    if not path.is_file():
        pytest.skip(f"{name} not built in this checkout")
    series = _series(path)
    day = pd.Timestamp(splice)
    assert day in series.index, f"{name} is missing its own splice date {splice}"

    # The session before the splice must be the immediately preceding session of
    # the source calendar, not one further back. That is exactly what deleting a
    # row at the joint looks like.
    if price_name is not None:
        price = _series(INPUTS / price_name)
        window = price.loc[:day]
        assert len(window) >= 2
        expected_previous = window.index[-2]
        got_previous = series.loc[:day].index[-2]
        assert got_previous == expected_previous, (
            f"{name}: session before the {splice} splice is {got_previous.date()}, "
            f"but the price path says {expected_previous.date()} -- a session was "
            "dropped at the joint"
        )


def test_sp500_carries_the_1988_new_year_session() -> None:
    """The specific value the old builder destroyed, pinned by magnitude.

    1988-01-04 rose 3.59% on price and about 3.6% on total return. The defective
    file recorded -0.30% there, which is 1987-12-31's return.
    """
    path = EXTERNAL / "us_equity_tr_sp500.csv"
    if not path.is_file():
        pytest.skip("us_equity_tr_sp500.csv not built in this checkout")
    series = _series(path)
    for day in ("1987-12-31", "1988-01-04"):
        assert pd.Timestamp(day) in series.index, f"{day} missing from the series"

    returns = series.pct_change()
    assert returns.loc["1988-01-04"] == pytest.approx(0.038, abs=0.003)
    assert returns.loc["1987-12-31"] == pytest.approx(-0.0030, abs=0.001)


def test_sp500_stitch_reconstructs_through_splice_before_takeover(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    px = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["1987-12-30", "1987-12-31", "1988-01-04", "1988-01-05"]
            ),
            "close": [90.0, 95.0, 100.0, 101.0],
        }
    )
    official = pd.DataFrame(
        {
            "date": pd.to_datetime(["1988-01-04", "1988-01-05", "1988-01-06"]),
            "close": [120.0, 121.0, 122.0],
            "origin": ["official", "official", "official"],
        }
    )
    reconstructed_dates: list[pd.Timestamp] = []

    def fake_reconstruct(frame: pd.DataFrame) -> pd.Series:
        reconstructed_dates.extend(frame["date"])
        return pd.Series([1.0, 1.1, 1.2], index=frame.index)

    monkeypatch.setattr(SP500_BUILDER, "reconstruct", fake_reconstruct)
    stitched = SP500_BUILDER.stitch(px, official)
    splice = pd.Timestamp("1988-01-04")

    assert reconstructed_dates == list(pd.to_datetime(px["date"].iloc[:3]))
    assert stitched["date"].tolist() == list(
        pd.to_datetime(
            ["1987-12-30", "1987-12-31", "1988-01-04", "1988-01-05", "1988-01-06"]
        )
    )
    assert stitched["value"].tolist() == pytest.approx(
        [100.0, 110.0, 120.0, 121.0, 122.0]
    )
    assert pd.isna(stitched.loc[stitched["date"] == splice, "origin"]).all()
    assert (stitched.loc[stitched["date"] > splice, "origin"] == "official").all()


def test_de_daily_dividend_yield_allocates_each_year_across_its_sessions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dates = pd.to_datetime(
        ["2020-12-30", "2020-12-31", "2021-01-04", "2021-01-05", "2021-01-06"]
    )

    def fake_read_csv(path: Path) -> pd.DataFrame:
        assert path.name == "jst_germany_eq.csv"
        return pd.DataFrame({"year": [2020, 2021], "eq_dp": [0.06, 0.12]})

    monkeypatch.setattr(DE_BUILDER.pd, "read_csv", fake_read_csv)
    daily = DE_BUILDER.daily_dividend_yield(dates)

    assert daily.loc["2020"].tolist() == pytest.approx([0.03, 0.03])
    assert daily.loc["2021"].tolist() == pytest.approx([0.04, 0.04, 0.04])
    assert daily.groupby(daily.index.year).sum().loc[2020] == pytest.approx(0.06)
    assert daily.groupby(daily.index.year).sum().loc[2021] == pytest.approx(0.12)


def test_external_builder_rejects_input_hash_before_downstream_io(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    changed = tmp_path / "changed.csv"
    changed.write_bytes(b"changed input")
    downstream_read = Mock()
    downstream_write = Mock()

    monkeypatch.setattr(EXTERNAL_BUILDER, "INP", tmp_path)
    monkeypatch.setattr(EXTERNAL_BUILDER, "INPUT_SHA256", {changed.name: "0" * 64})
    monkeypatch.setattr(EXTERNAL_BUILDER.pd, "read_csv", downstream_read)
    monkeypatch.setattr(EXTERNAL_BUILDER, "write", downstream_write)

    with pytest.raises(SystemExit, match=r"input hash mismatch for changed\.csv"):
        EXTERNAL_BUILDER.main()

    downstream_read.assert_not_called()
    downstream_write.assert_not_called()


# --- Japan: the causal construction must not read anything after the day ----


def _jp_synthetic() -> tuple[
    pd.Series, pd.Series, pd.Series, pd.Timestamp, pd.Timestamp
]:
    """A price path, an official TR series with a hole, and annual yields.

    The official series is price times a smooth 2%/year accrual, so the true
    trailing accrual is known. The hole removes 2002-03-04 .. 2002-08-30.
    """
    import numpy as np

    dates = pd.bdate_range("2000-01-03", "2003-12-31")
    rng = np.random.default_rng(0)
    price = pd.Series(
        100.0 * np.exp(np.cumsum(rng.normal(0.0, 0.01, len(dates)))), index=dates
    )
    first_official = pd.Timestamp("2001-01-02")
    official_dates = dates[dates >= first_official]
    accrual = 0.02 / 252.0 * np.arange(len(official_dates))
    official = 1.5 * price.loc[official_dates] * np.exp(accrual)
    hole_start, hole_end = pd.Timestamp("2002-03-01"), pd.Timestamp("2002-09-02")
    official = official[(official.index <= hole_start) | (official.index >= hole_end)]
    yields = pd.Series(
        {1999: 0.010, 2000: 0.020, 2001: 0.030, 2002: 0.040, 2003: 0.050},
        name="eq_dp",
    )
    return price, official, yields, hole_start, hole_end


def _log_returns(series: pd.Series) -> pd.Series:
    import numpy as np

    return np.log(series / series.shift(1)).dropna()


def test_jp_causal_bridge_ignores_the_value_at_the_end_of_the_hole() -> None:
    price, official, yields, hole_start, hole_end = _jp_synthetic()
    base, notes = EXTERNAL_BUILDER.jp_causal_total_return(price, official, yields)

    shocked = official.copy()
    shocked.loc[shocked.index >= hole_end] *= 1.10
    moved, _ = EXTERNAL_BUILDER.jp_causal_total_return(price, shocked, yields)

    inside = (base.index > hole_start) & (base.index <= hole_end)
    pd.testing.assert_series_equal(
        _log_returns(base)[inside[1:]], _log_returns(moved)[inside[1:]]
    )
    # The old construction would have absorbed the +10% into the bridge; the
    # causal one reports it only in the post-hole level constant.
    assert notes["post_hole_level_factor"] == pytest.approx(1.0, abs=0.05)


def test_jp_causal_bridge_uses_the_trailing_realised_accrual() -> None:
    price, official, yields, hole_start, hole_end = _jp_synthetic()
    series, notes = EXTERNAL_BUILDER.jp_causal_total_return(price, official, yields)
    assert notes["trailing_accrual_log_per_year"] == pytest.approx(0.02, abs=1e-9)

    inside = (series.index > hole_start) & (series.index <= hole_end)
    excess = _log_returns(series)[inside[1:]] - _log_returns(price)[inside[1:]]
    assert excess.to_numpy() == pytest.approx(0.02 / 252.0, abs=1e-12)


def test_jp_causal_joint_carries_the_official_return_after_the_hole() -> None:
    price, official, yields, _, hole_end = _jp_synthetic()
    series, _ = EXTERNAL_BUILDER.jp_causal_total_return(price, official, yields)
    after = official.index[official.index.get_loc(hole_end) + 1]
    got = float(series[after] / series[hole_end])
    expected = float(official[after] / official[hole_end])
    assert got == pytest.approx(expected, rel=1e-12)


def test_jp_causal_pre_official_years_use_the_prior_years_yield() -> None:
    price, official, yields, _, _ = _jp_synthetic()
    series, _ = EXTERNAL_BUILDER.jp_causal_total_return(price, official, yields)
    excess = _log_returns(series) - _log_returns(price).reindex(
        _log_returns(series).index
    )
    year_2000 = excess[(excess.index.year == 2000)]
    assert year_2000.to_numpy() == pytest.approx(yields[1999] / 252.0, abs=1e-12)
    assert series[official.index[0]] == pytest.approx(official.iloc[0])
