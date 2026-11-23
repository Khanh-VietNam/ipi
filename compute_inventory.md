# Compute Inventory: Hardware and Software Environment

_Last checked: 2026-11-23 (Windows local machine and GitHub Actions CI)_

## 1. Local Hardware

| Component | Recorded specification | Evidence / status |
|---|---|---|
| CPU | Intel(R) Core(TM) 5 210H | Verified using `Get-CimInstance Win32_Processor` |
| Discrete GPU | NVIDIA GeForce RTX 4050 Laptop GPU | Verified using `nvidia-smi` |
| GPU memory | 6141 MiB (approximately 6 GiB) | Reported by `nvidia-smi` |
| Integrated GPU | Intel(R) Graphics | Verified using `Get-CimInstance Win32_VideoController` |
| System RAM | 16 GB | Recorded in earlier inventory; not independently rechecked in this update |
| Operating system | Windows 11 | Recorded in earlier inventory; exact build not independently rechecked |

## 2. GPU Drivers and CUDA

| Component | Version / status | Evidence / interpretation |
|---|---|---|
| NVIDIA driver | 561.00 | `nvidia-smi` |
| NVIDIA Windows driver version | 32.0.15.6100 | `Win32_VideoController.DriverVersion` |
| Intel graphics driver | 32.0.101.7076 | `Win32_VideoController.DriverVersion` |
| NVIDIA-SMI | 561.00 | `nvidia-smi` |
| CUDA version displayed by NVIDIA-SMI | 12.6 | Driver-supported CUDA version; **not** confirmation of a CUDA Toolkit installation |
| CUDA Toolkit / `nvcc` | Not verified | `nvcc --version` returned `CommandNotFoundException`; Toolkit may be absent or `nvcc` may not be on PATH |

## 3. Local Python and Machine Learning Libraries

| Component | Version / status | Evidence / interpretation |
|---|---|---|
| Python | 3.13.14 | `python --version` |
| PyTorch (`torch`) | Not installed in the tested Python environment | `import torch` raised `ModuleNotFoundError: No module named 'torch'` |
| TorchAudio | Not separately checked in the local environment | Do not infer its presence from CI |
| PyTorch CUDA runtime | Not measurable locally yet | `torch` import failed, so `torch.version.cuda` and `torch.cuda.is_available()` could not run |
| Local pytest | Not separately checked | Automated tests are run in GitHub Actions |

This section describes the interpreter invoked by `python` in the Windows PowerShell session, not every possible Python environment on the computer. The absence of `torch` in this environment does not mean that the GPU or its NVIDIA driver is faulty.

## 4. GitHub Actions CI Environment

The repository's `pytest` workflow uses a separate CPU-oriented environment. The dependencies previously configured for CI are:

- PyTorch (`torch`): 2.5.1
- TorchAudio: 2.5.1
- NumPy: 1.26.4
- Pytest: installed; exact version not recorded here

Latest observed workflow result on 2026-11-23: **40 passed, 1 skipped, 0 failed**.

Evidence: https://github.com/stevenhuynh87/baokhanh-TinyML/actions/runs/45164199546

The skipped test belongs to the standard CI workflow; Speech Commands v0.02 was also checked separately using the real-data workflow:
https://github.com/stevenhuynh87/baokhanh-TinyML/actions/runs/45056285634

**Important:** Successful CPU-based CI tests do not establish that GPU acceleration works in the local Windows Python environment.

## 5. Commands Used for Verification

```powershell
Get-CimInstance Win32_Processor | Select-Object -ExpandProperty Name
Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion
nvidia-smi
python --version
nvcc --version
python -c "import torch; print('PyTorch:', torch.__version__); print('PyTorch CUDA:', torch.version.cuda); print('GPU available:', torch.cuda.is_available())"
```

## 6. Remaining Checks

- Verify local memory capacity and exact Windows build if required for reproduction.
- Confirm whether CUDA Toolkit is installed and whether `nvcc` is on PATH before reporting a Toolkit version.
- Set up an isolated Python environment with a mutually compatible Python/PyTorch/TorchAudio combination before local model training; do not assume the CI-pinned package versions support local Python 3.13.14.
- Record exact local PyTorch, TorchAudio, and CUDA runtime versions once a local environment is set up, together with GPU availability and the environment name.

**Status:** Hardware identity, NVIDIA driver, driver-supported CUDA version, and local Python version are verified. Local GPU-enabled PyTorch setup remains pending.
