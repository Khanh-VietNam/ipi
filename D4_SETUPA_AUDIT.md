# D4 — CRAWDAD Columbia/EnHANTs: real Setup A data validation (2026-11-23)

## Dataset and provenance

- Dataset: **columbia/enhants** (indoor radiant light-energy measurements; **Setup A**, stationary student office).
- Original public source: https://ieee-dataport.org/open-access/crawdad-columbiaenhants
- DOI: https://doi.org/10.15783/C77P47
- Format and units documentation (original project): https://enhants.ee.columbia.edu/indoor-irradiance-meas
- Source publication attribution: Maria Gorlatova, Michael Zapas, Enlin Xu, Matthias Bahlke, Ioannis (John) Kymissis, Gil Zussman. Dataset distributed under Creative Commons Attribution as shown on IEEE DataPort.
- Original file: `SetupA_merged_2009_8_15_2010_9_13.txt`
- Original file SHA-256: `eab71ae0f0003cee18870e384eb980f9ad4ab0cf2be94fabd139c4c6a261916b`

## Understanding the raw eight-column file

`time_s  irradiance_uw_cm2  year  month  day  hour  minute  second`

- Column 1: seconds since experiment start.
- Column 2: **measured *optical irradiance*** in **µW/cm²**. This is **not** electrical power harvested by a device. Do not treat it as energy or watts without an area, optical-to-electrical efficiency, and unit conversion.
- Columns 3–8: wall-clock date and time.
- Native cadence: one row every **30 seconds** in this source file. Some measured irradiance values are `NaN` due to missing data.
- The earlier, general introductory paragraph on the project page expresses irradiance in `W/cm²`, but its *trace format* section explicitly states the data column uses **µW/cm²**. This distinction is crucial; the conversion script preserves native numerical values (no ×1,000,000 multiplication).

## Full-file audit

| Check | Result |
|---|---:|
| Raw rows | 1,133,636 |
| Raw columns | 8 |
| Valid irradiance rows | 1,107,796 |
| `NaN` irradiance values | 25,840 (2.2794%) |
| Missing-value runs | 2 |
| Missing run 1 | 14,400 measurements (120 hours) |
| Missing run 2 | 11,440 measurements (95 hours 20 minutes) |
| Invalid/NaN timestamp values | 0 |
| Duplicate or non-increasing native `time_s` | 0 |
| Negative measured irradiance | 0 |
| Minimum valid irradiance | 0 µW/cm² |
| Maximum valid irradiance | 1,117.48 µW/cm² |
| Mean valid irradiance | approx. 15.21168645 µW/cm² |
| First native `time_s` | 0 |
| Last native `time_s` | 34,009,050 |
| Largest interval **after dropping NaN measurements** | 432,030 seconds |
| Synthetic fallback used | **No** |
| Interpolation or gap filling | **No** |

## Reproducible conversion (run at repository root)

Place the raw TXT downloaded from IEEE DataPort somewhere locally, then run:

```bash
python data/prepare_enhants.py \
    --input "SetupA_merged_2009_8_15_2010_9_13.txt" \
    --output "data/traces_setupA.csv" \
    --report "data/traces_setupA_report.json"
```

This generates `data/traces_setupA.csv` in the **exact two-column format** expected by the existing `EnhantsLoader.load('setupA', data_dir='./data')`:

```csv
time_s,power_uw_cm2
0,0.02
30,0.02
60,0.02
```

The header `power_uw_cm2` is **historical loader API terminology**. The source measurement is *irradiance*, and the physics model must convert using an assumed conversion efficiency and area, e.g. `P_harvest_W(t) = eta * area_cm2 * irradiance_uw_cm2(t) * 1e-6` (idealized relation; device calibration must be specified separately).

**Cleaning policy:** Only rows with NaN measured irradiance are omitted. Original `time_s` values are retained. The gaps must remain gaps: no invented irradiance values, no resetting timestamps, no assumption of uninterrupted 30-second sampling after cleaning.

To verify the cleaned full file locally:

```bash
python -c "from data.traces import EnhantsLoader; import numpy as np; x=EnhantsLoader.load('setupA'); assert x.shape == (1107796,2) and np.isfinite(x).all() and np.all(np.diff(x[:,0])>0) and np.all(x[:,1]>=0); print('REAL SetupA trace PASS',x.shape)"
python -m pytest -q tests/test_prepare_enhants.py
```

## Evidence, GitHub checklist, and remaining caveats

**Verified with real data:** Source identity, raw eight-column structure, native units, NaN count, cleaning policy, output shape, valid increasing timestamps, and compatibility with `data/traces.py`. Six converter unit tests passed, and the full cleaned file was loaded successfully by the existing `EnhantsLoader` without NaN/Inf.

**Still not established:** A complete energy-harvesting or intermittent-inference simulation, device-specific electrical conversion efficiency/area/capacitor parameters, or successful loading of **all** Setup B–F and mobile traces. Claims about any of those require separate evidence.

**Checklist guidance:** D4 source investigation can be marked done after reviewing this report and making files available; the `data/traces.py` real-data and no-NaN checks can be marked done if the converted CSV and evidence are committed or reproducibly documented. A combined checkbox including *all* GSC + EnHANTs data ingestion should only be marked done when both are addressed. Do not check Simulation 'run' tasks on the strength of this file alone.
