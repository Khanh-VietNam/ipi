"""Integration tests for the committed real CRAWDAD Columbia/EnHANTs Setup A trace.

Source: https://doi.org/10.15783/C77P47
Input:  data/traces_setupA.csv (produced by data/prepare_enhants.py)

Unlike converter unit tests that use tiny synthetic fixtures, these tests load
all 1,107,796 cleaned rows of the *real* Setup A recording.

Run from the repository root:
    python -m pytest -q tests/test_enhants_real_setupA.py
"""

from pathlib import Path
import warnings

import numpy as np
import pytest

from data.traces import EnhantsLoader


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
TRACE_PATH = DATA_DIR / "traces_setupA.csv"
EXPECTED_ROWS = 1_107_796


@pytest.fixture(scope="module")
def real_setupA():
    """Load the actual committed CSV exactly once per test session."""
    assert TRACE_PATH.is_file(), (
        "Real EnHANTs data file is missing: data/traces_setupA.csv. "
        "Make sure the file has exactly this name in the GitHub repository."
    )
    with TRACE_PATH.open(encoding="utf-8-sig") as f:
        assert f.readline().strip() == "time_s,power_uw_cm2"

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        trace = EnhantsLoader.load("setupA", data_dir=DATA_DIR)
    assert not any("SYNTHETIC" in str(w.message) for w in caught)
    return trace


def test_real_setupA_loader_shape_and_finite_values(real_setupA):
    assert real_setupA.shape == (EXPECTED_ROWS, 2)
    assert real_setupA.dtype == np.float64
    assert np.isfinite(real_setupA).all(), "Real cleaned trace has NaN or Inf"
    assert np.all(real_setupA[:, 1] >= 0), "Irradiance cannot be negative"


def test_real_setupA_keeps_original_timestamps(real_setupA):
    timestamps = real_setupA[:, 0]
    assert timestamps[0] == 0.0
    assert timestamps[-1] == 34_009_050.0
    assert np.all(np.diff(timestamps) > 0), "Timestamps must strictly increase"
    # Removing NaNs must not squeeze time: the two real gaps remain visible.
    gaps = np.diff(timestamps)
    np.testing.assert_array_equal(
        np.sort(gaps[gaps > 30]), [343_230.0, 432_030.0]
    )


def test_real_setupA_expected_measurement_range(real_setupA):
    # This field is measured optical irradiance (µW/cm²), NOT harvested W.
    irradiance = real_setupA[:, 1]
    assert irradiance[0] == pytest.approx(0.02)
    assert irradiance.min() == pytest.approx(0.0)
    assert irradiance.max() == pytest.approx(1117.48)
    assert irradiance.mean() == pytest.approx(15.2116864477, abs=1e-6)
