"""Tests for the EnHANTs energy-trace CSV loader.

Run from the repository root with: python -m pytest -q
All tests use temporary CSV files; real EnHANTs data is not required.
"""

import warnings

import numpy as np
import pytest

from data.traces import EnhantsLoader


def _csv(tmp_path, content, location="lab"):
    path = tmp_path / f"traces_{location}.csv"
    path.write_text(content, encoding="utf-8")
    return path


@pytest.mark.parametrize("with_header", [True, False])
def test_real_trace_shape_finite_and_units_order(tmp_path, with_header):
    content = "0,10\n30,20\n60,5\n"
    if with_header:
        content = "time_s,power_uw_cm2\n" + content
    _csv(tmp_path, content)

    trace = EnhantsLoader.load("lab", data_dir=tmp_path)

    assert trace.shape == (3, 2)
    assert trace.dtype == np.float64
    assert np.isfinite(trace).all()
    np.testing.assert_array_equal(trace[:, 0], [0, 30, 60])
    np.testing.assert_array_equal(trace[:, 1], [10, 20, 5])


def test_missing_real_trace_raises_by_default(tmp_path):
    with pytest.raises(FileNotFoundError, match="Real energy trace not found"):
        EnhantsLoader.load("missing", data_dir=tmp_path)


def test_synthetic_requires_opt_in_and_emits_warning(tmp_path):
    with pytest.warns(UserWarning, match="SYNTHETIC"):
        trace = EnhantsLoader.load(
            "missing", use_synthetic_fallback=True, data_dir=tmp_path
        )
    assert trace.shape == (1000, 2)
    assert np.isfinite(trace).all()
    assert np.all(np.diff(trace[:, 0]) > 0)
    assert np.all(trace[:, 1] >= 0)


def test_real_trace_takes_priority_over_synthetic(tmp_path):
    _csv(tmp_path, "time_s,power_uw_cm2\n0,1\n30,2\n")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        trace = EnhantsLoader.load(
            "lab", use_synthetic_fallback=True, data_dir=tmp_path
        )
    assert trace.shape == (2, 2)
    assert not any("SYNTHETIC" in str(w.message) for w in caught)


@pytest.mark.parametrize(
    "csv_content, expected_message",
    [
        ("time_s,power_uw_cm2\n0,nan\n30,2\n", "NaN or Inf"),
        ("time_s,power_uw_cm2\n0,inf\n30,2\n", "NaN or Inf"),
        ("time_s,power_uw_cm2\n0,-1\n30,2\n", "nonnegative"),
        ("time_s,power_uw_cm2\n-1,5\n30,2\n", "nonnegative"),
        ("time_s,power_uw_cm2\n0,1\n0,2\n", "strictly increasing"),
        ("time_s,power_uw_cm2\n30,1\n0,2\n", "strictly increasing"),
        ("time_s,power_uw_cm2\n0,1,3\n", "shape"),
    ],
)
def test_invalid_real_trace_is_rejected(tmp_path, csv_content, expected_message):
    _csv(tmp_path, csv_content)
    with pytest.raises(ValueError, match=expected_message):
        EnhantsLoader.load("lab", data_dir=tmp_path)


@pytest.mark.parametrize("location", ["", "../bad", "a/b", "a\\b"])
def test_invalid_location_id_is_rejected(tmp_path, location):
    with pytest.raises(ValueError, match="location_id"):
        EnhantsLoader.load(location, data_dir=tmp_path)
