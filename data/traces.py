"""Load two-column energy traces for intermittent TinyML.

Expected CSV columns (with optional header):
    time_s,power_uw_cm2

Time is in seconds; power density is in microwatts per square centimetre
(µW/cm²). Input files must already be converted to these units.
"""

from pathlib import Path
import warnings

import numpy as np


class EnhantsLoader:
    @staticmethod
    def load(
        location_id: str,
        use_synthetic_fallback: bool = False,
        *,
        data_dir: str | Path = "./data",
    ) -> np.ndarray:
        """Return an (N, 2) array with [time_s, power_uw_cm2].

        Real traces are preferred. Synthetic data are generated only when
        explicitly requested via ``use_synthetic_fallback=True``.
        """
        if not location_id or "/" in location_id or "\\" in location_id or ".." in location_id:
            raise ValueError("location_id must be a simple, non-empty identifier")

        file_path = Path(data_dir) / f"traces_{location_id}.csv"
        if file_path.is_file():
            with file_path.open("r", encoding="utf-8-sig") as f:
                first_line = f.readline().strip()
            # Detect an optional header without silently skipping a data row.
            try:
                [float(cell.strip()) for cell in first_line.split(",")]
                skiprows = 0
            except ValueError:
                skiprows = 1

            data = np.loadtxt(file_path, delimiter=",", skiprows=skiprows, ndmin=2)
            return EnhantsLoader._validate(data)

        if not use_synthetic_fallback:
            raise FileNotFoundError(f"Real energy trace not found: {file_path}")

        warnings.warn(
            f"SYNTHETIC trace generated for {location_id!r}; do not mix with real traces.",
            UserWarning,
            stacklevel=2,
        )
        time_s = np.arange(0, 1000 * 30, 30, dtype=np.float64)
        power_uw_cm2 = np.abs(np.sin(time_s / 3600.0) * 45 + 15)
        return EnhantsLoader._validate(np.column_stack((time_s, power_uw_cm2)))

    @staticmethod
    def _validate(data: np.ndarray) -> np.ndarray:
        data = np.asarray(data, dtype=np.float64)
        if data.ndim != 2 or data.shape[1] != 2 or data.shape[0] == 0:
            raise ValueError("Trace must have shape (N, 2): [time_s, power_uw_cm2]")
        if not np.isfinite(data).all():
            raise ValueError("Trace must not contain NaN or Inf")
        if np.any(data[:, 0] < 0) or np.any(np.diff(data[:, 0]) <= 0):
            raise ValueError("Time must be nonnegative and strictly increasing")
        if np.any(data[:, 1] < 0):
            raise ValueError("Power density must be nonnegative (µW/cm²)")
        return data

