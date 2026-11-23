"""Unit tests for data/prepare_enhants.py (CRAWDAD EnHANTs conversion).

These tests use tiny synthetic *fixtures* only to validate the converter;
production EnHANTs measurements are never generated or replaced by them.
Run from repository root: python -m pytest -q tests/test_prepare_enhants.py
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest


# Load from its repository path; this works even if data/ lacks __init__.py.
SCRIPT = Path(__file__).resolve().parents[1] / "data" / "prepare_enhants.py"
spec = importlib.util.spec_from_file_location("prepare_enhants", SCRIPT)
assert spec is not None and spec.loader is not None
prepare_enhants = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare_enhants)
convert_enhants = prepare_enhants.convert_enhants


def _row(t: int, irradiance: str) -> str:
    """One correctly shaped native EnHANTs row: 8 whitespace-separated fields."""
    return f"{t} {irradiance} 2009 8 15 0 {t // 60} {t % 60}\n"


def _write_source(tmp_path: Path, content: str) -> Path:
    source = tmp_path / "SetupA_example.txt"
    source.write_text(content, encoding="utf-8")
    return source


def test_valid_input_creates_exactly_two_columns_and_report(tmp_path: Path) -> None:
    raw = _row(0, "0.02") + _row(30, "1.25") + _row(60, "0")
    source = _write_source(tmp_path, raw)
    output = tmp_path / "traces_setupA.csv"
    report = tmp_path / "report.json"

    stats = convert_enhants(source, output, report)

    with output.open(encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    assert rows == [
        ["time_s", "power_uw_cm2"],
        ["0", "0.02"],
        ["30", "1.25"],
        ["60", "0"],
    ]
    assert stats["rows_in"] == 3
    assert stats["rows_out"] == 3
    assert stats["nan_measurements_dropped"] == 0
    assert stats["source_sha256"] == hashlib.sha256(raw.encode()).hexdigest()
    assert stats["source_doi"] == "10.15783/C77P47"
    assert stats["source_measurement"] == "irradiance_uw_cm2"
    assert stats["synthetic_data_used"] is False
    assert stats["filled_or_interpolated"] is False
    assert json.loads(report.read_text(encoding="utf-8")) == stats


def test_nan_is_dropped_without_interpolating_or_renumbering_time(tmp_path: Path) -> None:
    source = _write_source(
        tmp_path,
        _row(0, "0.02") + _row(30, "NaN") + _row(60, "nan") + _row(90, "4.0"),
    )
    output = tmp_path / "traces_setupA.csv"
    stats = convert_enhants(source, output)

    with output.open(encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    assert rows[1:] == [["0", "0.02"], ["90", "4"]]
    assert stats["rows_in"] == 4
    assert stats["rows_out"] == 2
    assert stats["nan_measurements_dropped"] == 2
    assert stats["nan_runs"] == [
        {"first_missing_time_s": 30.0, "last_missing_time_s": 60.0, "missing_rows": 2}
    ]
    assert stats["largest_output_gap_s"] == 90.0
    assert stats["filled_or_interpolated"] is False


@pytest.mark.parametrize(
    ("content", "error"),
    [
        (_row(0, "-0.1"), "irradiance must be finite and nonnegative"),
        (_row(0, "inf"), "irradiance must be finite and nonnegative"),
        (_row(-30, "0.1"), "nonfinite or negative time"),
        (_row(0, "0.1") + _row(0, "0.2"), "time must increase strictly"),
        (_row(30, "0.1") + _row(0, "0.2"), "time must increase strictly"),
        ("0 0.1 2009 8 15\n", "expected 8 columns"),
        ("0 wrong 2009 8 15 0 0 0\n", "malformed numerical field"),
        ("0 0.1 2009 13 15 0 0 0\n", "invalid wall-clock timestamp"),
    ],
)
def test_bad_native_data_is_rejected_without_leaving_temp_file(
    tmp_path: Path, content: str, error: str
) -> None:
    source = _write_source(tmp_path, content)
    output = tmp_path / "traces_setupA.csv"
    with pytest.raises(ValueError, match=error):
        convert_enhants(source, output)
    assert not output.exists()
    assert not output.with_name(output.name + ".tmp").exists()


def test_all_missing_measurements_are_rejected(tmp_path: Path) -> None:
    source = _write_source(tmp_path, _row(0, "nan") + _row(30, "nan"))
    with pytest.raises(ValueError, match="No valid data points"):
        convert_enhants(source, tmp_path / "output.csv")


def test_missing_input_raises_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        convert_enhants(tmp_path / "absent.txt", tmp_path / "out.csv")


def test_cannot_overwrite_native_source(tmp_path: Path) -> None:
    source = _write_source(tmp_path, _row(0, "0.02"))
    before = source.read_bytes()
    with pytest.raises(ValueError, match="must be different"):
        convert_enhants(source, source)
    assert source.read_bytes() == before


def test_bad_input_preserves_existing_output(tmp_path: Path) -> None:
    source = _write_source(tmp_path, _row(0, "1") + _row(0, "2"))
    output = tmp_path / "out.csv"
    output.write_text("previous-good-output\n", encoding="utf-8")
    with pytest.raises(ValueError, match="time must increase strictly"):
        convert_enhants(source, output)
    assert output.read_text(encoding="utf-8") == "previous-good-output\n"
