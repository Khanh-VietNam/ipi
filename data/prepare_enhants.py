"""Prepare a real CRAWDAD Columbia/EnHANTs eight-column irradiance trace.

Source: https://doi.org/10.15783/C77P47
Format: https://enhants.ee.columbia.edu/indoor-irradiance-meas

The official second column is measured *irradiance* in µW/cm²; it is NOT
harvested electrical power. The repository's legacy two-column loader calls
this field ``power_uw_cm2``; we keep that header for API compatibility.

No interpolation, forward filling, synthetic data, or timestamp renumbering.
Missing values in the measured-irradiance column are omitted and counted;
real timestamps are retained, so resulting spacing may exceed 30 seconds.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


def convert_enhants(input_path: str | Path, output_path: str | Path, report_path: str | Path | None = None) -> dict:
    """Convert native eight-column EnHANTs .txt into strict (N,2) CSV.

    Reject malformed rows, negative/nonfinite time, decreasing timestamps,
    negative/inf irradiance. Skip and count only NaN irradiance measurements.
    """
    src, out = Path(input_path), Path(output_path)
    if src.resolve() == out.resolve():
        raise ValueError("input_path and output_path must be different")
    if not src.is_file():
        raise FileNotFoundError(src)
    out.parent.mkdir(parents=True, exist_ok=True)
    total = kept = dropped_nan = 0
    first_time = prev_time = last_time = None
    prev_kept_time = None
    largest_output_gap_s = 0.0
    missing_runs = []
    run_first = run_last = run_len = None
    sum_irradiance = 0.0
    max_irradiance = -math.inf
    sha = hashlib.sha256()

    # Use a temporary file: never leave a partially written final CSV if invalid.
    tmp = out.with_name(out.name + '.tmp')
    try:
        with src.open('rb') as fin, tmp.open('w', encoding='utf-8', newline='') as fout:
            writer = csv.writer(fout, lineterminator='\n')
            writer.writerow(['time_s', 'power_uw_cm2'])
            for lineno, raw in enumerate(fin, start=1):
                sha.update(raw)
                if not raw.strip():
                    continue
                pieces = raw.decode('utf-8-sig').split()
                if len(pieces) != 8:
                    raise ValueError(f'Line {lineno}: expected 8 columns, got {len(pieces)}')
                try:
                    time_s, measured = float(pieces[0]), float(pieces[1])
                    date = [int(s) for s in pieces[2:]]
                except (ValueError, OverflowError) as exc:
                    raise ValueError(f'Line {lineno}: malformed numerical field') from exc
                if not math.isfinite(time_s) or time_s < 0:
                    raise ValueError(f'Line {lineno}: nonfinite or negative time')
                if prev_time is not None and time_s <= prev_time:
                    raise ValueError(f'Line {lineno}: time must increase strictly')
                year, month, day, hour, minute, second = date
                if not (1 <= month <= 12 and 1 <= day <= 31 and
                        0 <= hour < 24 and 0 <= minute < 60 and 0 <= second < 60):
                    raise ValueError(f'Line {lineno}: invalid wall-clock timestamp')
                total += 1
                if first_time is None:
                    first_time = time_s
                prev_time = last_time = time_s
                if math.isnan(measured):
                    dropped_nan += 1
                    if run_len is None:
                        run_first = time_s
                        run_len = 0
                    run_len += 1
                    run_last = time_s
                    continue
                if not math.isfinite(measured) or measured < 0:
                    raise ValueError(f'Line {lineno}: irradiance must be finite and nonnegative')
                if run_len is not None:
                    missing_runs.append({'first_missing_time_s': run_first,
                                         'last_missing_time_s': run_last,
                                         'missing_rows': run_len})
                    run_len = None
                if prev_kept_time is not None:
                    largest_output_gap_s = max(largest_output_gap_s, time_s - prev_kept_time)
                prev_kept_time = time_s
                writer.writerow([format(time_s, '.15g'), format(measured, '.15g')])
                kept += 1
                sum_irradiance += measured
                max_irradiance = max(max_irradiance, measured)
        if run_len is not None:
            missing_runs.append({'first_missing_time_s': run_first,
                                 'last_missing_time_s': run_last,
                                 'missing_rows': run_len})
        if not kept:
            raise ValueError('No valid data points')
        tmp.replace(out)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise

    result = {
        'source_name': src.name,
        'source_sha256': sha.hexdigest(),
        'source_doi': '10.15783/C77P47',
        'source_dataset': 'CRAWDAD columbia/enhants — stationary Setup A',
        'source_measurement': 'irradiance_uw_cm2',
        'output_header': 'time_s,power_uw_cm2 (historical loader naming; physical measurement is irradiance)',
        'output_file': out.name,
        'rows_in': total,
        'rows_out': kept,
        'nan_measurements_dropped': dropped_nan,
        'dropped_percent': 100 * dropped_nan / total,
        'nan_runs': missing_runs,
        'first_time_s': first_time,
        'last_time_s': last_time,
        'largest_output_gap_s': largest_output_gap_s,
        'mean_valid_irradiance_uw_cm2': sum_irradiance / kept,
        'max_valid_irradiance_uw_cm2': max_irradiance,
        'filled_or_interpolated': False,
        'synthetic_data_used': False,
    }
    if report_path is not None:
        report = Path(report_path)
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, help='Original EnHANTs eight-column TXT')
    parser.add_argument('--output', default='data/traces_setupA.csv', help='Two-column CSV for EnhantsLoader')
    parser.add_argument('--report', default='data/traces_setupA_report.json', help='JSON provenance/quality report')
    args = parser.parse_args()
    print(json.dumps(convert_enhants(args.input, args.output, args.report), indent=2, ensure_ascii=False))
