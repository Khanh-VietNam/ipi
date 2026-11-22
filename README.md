# Intermittent TinyML Research

**Project:** State-Preserving Intermittent Deep Learning via Dynamic Early-Exit and Non-Volatile Memory Mapping on Micro-Watt IoT Nodes

**Institution:** International University — Vietnam National University Ho Chi Minh City

**Research area:** Intermittent Computing, TinyML, Energy Harvesting, Deep Learning

## 1. Project Overview

Batteryless IoT devices operate using harvested energy and may experience frequent power interruptions. Running deep neural networks on these devices is challenging because intermediate computational states must be preserved across power failures.

Saving these states to non-volatile memory (NVM), such as FRAM, introduces additional energy consumption and execution overhead.

This research investigates energy-aware intermittent deep learning with an emphasis on state preservation and adaptive inference.

The project is simulation-based and does not require physical hardware deployment.

## 2. Research Objectives

The research roadmap investigates the following directions:

- **Persistent-State Bottleneck (PSB):** Learn compressed representations of intermediate neural network states to reduce NVM storage overhead.
- **Energy-Trace-Conditioned Training (ETCT):** Adapt training to energy availability and power-interruption patterns.
- **Dynamic Early-Exit Policy:** Investigate Exit/Persist/Skip decisions under intermittent energy constraints using a Markov Decision Process (MDP).

These are planned research directions, not completed implementations.

## 3. Repository Structure

Current S01 files:

- `data/gsc.py` — Google Speech Commands dataset loader.
- `data/traces.py` — Energy trace loader with optional synthetic fallback.
- `tests/test_gsc.py` — Speech Commands loader tests.
- `tests/test_traces.py` — Energy trace loader tests.
- `lit_table_v0.csv` — Preliminary literature review table.
- `problem_formulation.md` — Initial problem formulation.
- `compute_inventory.md` — Computing environment inventory.
- `.github/workflows/pytest.yml` — Automated pytest workflow.
- `.github/workflows/gsc_real_check.yml` — Real Speech Commands dataset verification workflow.

## 4. Software Requirements

The tested GitHub Actions environment uses:

- Python 3.11
- PyTorch 2.5.1 (CPU)
- TorchAudio 2.5.1 (CPU)
- NumPy 1.26.4
- pytest
- SoundFile

Install the compatible CPU versions of PyTorch and TorchAudio:

`python -m pip install torch==2.5.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cpu`

Install the remaining dependencies:

`python -m pip install numpy==1.26.4 pytest soundfile`

These versions describe the tested CI environment, not necessarily the GPU environment listed in the computing inventory.

## 5. Google Speech Commands Dataset

The project uses Google Speech Commands v0.02.

Official dataset:

https://storage.googleapis.com/download.tensorflow.org/data/speech_commands_v0.02.tar.gz

The extracted dataset should contain:

- `validation_list.txt`
- `testing_list.txt`
- WAV files organized into word-label directories.

By default, the GSC loader expects the dataset under `./data/gsc_data`.

Example:

`from data.gsc import GSCDataset`

`train_dataset = GSCDataset(split="train", root="./data/gsc_data")`

The loader supports `train`, `validation`, and `test` splits using the official dataset lists.

### MFCC Configuration

- Sampling rate: 16,000 Hz
- Input length: 16,000 samples
- FFT size: 400
- Hop length: 320
- Mel filters: 23
- MFCC coefficients: 10
- Center padding
