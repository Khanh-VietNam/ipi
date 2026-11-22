
from pathlib import Path

import torch
import torchaudio
from torch.utils.data import Dataset


class GSCDataset(Dataset):
    SAMPLE_RATE = 16000
    MFCC_SHAPE = (49, 10)

    def __init__(
        self,
        split="train",
        root="./data/gsc_data",
        target_length=16000
    ):
        if split not in ("train", "validation", "test"):
            raise ValueError(
                "split must be train, validation or test"
            )

        if target_length != 16000:
            raise ValueError(
                "49x10 MFCC requires target_length=16000"
            )

        self.split = split
        self.root = Path(root)
        self.target_length = target_length

        if not self.root.is_dir():
            raise FileNotFoundError(
                f"Dataset folder not found: {self.root}"
            )

        validation_files = self._read_list(
            "validation_list.txt"
        )
        testing_files = self._read_list(
            "testing_list.txt"
        )

        if validation_files & testing_files:
            raise ValueError(
                "Validation and test lists overlap"
            )

        self.labels = sorted(
            p.name for p in self.root.iterdir()
            if p.is_dir()
            and p.name != "_background_noise_"
        )

        self.label_to_idx = {
            label: idx
            for idx, label in enumerate(self.labels)
        }

        all_files = {}

        for label in self.labels:
            label_dir = self.root / label

            for path in sorted(label_dir.glob("*.wav")):
                relative_path = path.relative_to(
                    self.root
                ).as_posix()

                all_files[relative_path] = path

        missing = (
            validation_files | testing_files
        ) - all_files.keys()

        if missing:
            raise FileNotFoundError(
                f"Missing {len(missing)} official files: "
                f"{sorted(missing)[:5]}"
            )

        if split == "validation":
            selected = validation_files

        elif split == "test":
            selected = testing_files

        else:
            selected = (
                all_files.keys()
                - validation_files
                - testing_files
            )

        self.samples = []

        for relative_path in sorted(selected):
            path = all_files[relative_path]
            label = relative_path.split("/")[0]

            self.samples.append(
                (str(path), self.label_to_idx[label])
            )

        self.mfcc_transform = torchaudio.transforms.MFCC(
            sample_rate=16000,
            n_mfcc=10,
            melkwargs={
                "n_fft": 400,
                "hop_length": 320,
                "n_mels": 23,
                "center": False
            }
        )

    def _read_list(self, filename):
        path = self.root / filename

        if not path.is_file():
            raise FileNotFoundError(
                f"Official split file not found: {path}"
            )

        with path.open("r", encoding="utf-8") as f:
            entries = {
                line.strip().replace("\\", "/")
                for line in f
                if line.strip()
            }

        if any(
            p.startswith("/") or ".." in p.split("/")
            for p in entries
        ):
            raise ValueError(
                f"Invalid path in {filename}"
            )

        return entries

    def __len__(self):
        return len(self.samples)

    def _to_mfcc(self, waveform, sample_rate):
        if sample_rate != self.SAMPLE_RATE:
            waveform = torchaudio.functional.resample(
                waveform,
                orig_freq=sample_rate,
                new_freq=self.SAMPLE_RATE
            )

        length = waveform.shape[1]

        if length < self.target_length:
            waveform = torch.nn.functional.pad(
                waveform,
                (0, self.target_length - length)
            )

        elif length > self.target_length:
            waveform = waveform[:, :self.target_length]

        mfcc = self.mfcc_transform(waveform)

        mfcc = mfcc.squeeze(0).transpose(0, 1)
        mfcc = mfcc.contiguous()

        assert mfcc.shape == self.MFCC_SHAPE, (
            f"Expected {self.MFCC_SHAPE}, "
            f"got {tuple(mfcc.shape)}"
        )

        assert torch.isfinite(mfcc).all().item(), (
            "MFCC contains NaN or Inf"
        )

        return mfcc

    def __getitem__(self, idx):
        file_path, label = self.samples[idx]

        waveform, sample_rate = torchaudio.load(
            file_path
        )

        if waveform.shape[0] > 1:
            waveform = waveform.mean(
                dim=0,
                keepdim=True
            )

        mfcc = self._to_mfcc(
            waveform,
            sample_rate
        )

        return mfcc, label
