"""Unit tests and optional real-data split verification for GSCDataset."""

import os
import struct
import wave
from pathlib import Path

import pytest
import torch

from data.gsc import GSCDataset


def _make_wav(path: Path, sample_rate: int = 16_000) -> None:
    """Write a valid one-second mono PCM WAV without audio-encoder dependencies."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # Constant, low-amplitude signal; MFCC need only be finite and correctly shaped.
    samples = struct.pack("<" + "h" * sample_rate, *([1000] * sample_rate))
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(samples)


@pytest.fixture
def small_gsc(tmp_path: Path) -> Path:
    root = tmp_path / "speech_commands_v0.02"
    for name in ["yes/train.wav", "yes/val.wav", "yes/test.wav",
                 "no/train.wav", "no/val.wav", "no/test.wav"]:
        _make_wav(root / name, sample_rate=8_000 if name == "yes/train.wav" else 16_000)
    _make_wav(root / "_background_noise_" / "noise.wav")
    (root / "validation_list.txt").write_text("yes/val.wav\nno/val.wav\n", encoding="utf-8")
    (root / "testing_list.txt").write_text("yes/test.wav\nno/test.wav\n", encoding="utf-8")
    return root


def _relative_names(dataset: GSCDataset) -> set[str]:
    return {Path(path).relative_to(dataset.root).as_posix() for path, _ in dataset.samples}


def test_official_split_counts_and_no_leakage(small_gsc: Path) -> None:
    train = GSCDataset(split="train", root=small_gsc)
    validation = GSCDataset(split="validation", root=small_gsc)
    test = GSCDataset(split="test", root=small_gsc)

    assert (len(train), len(validation), len(test)) == (2, 2, 2)
    assert _relative_names(validation) == {"yes/val.wav", "no/val.wav"}
    assert _relative_names(test) == {"yes/test.wav", "no/test.wav"}
    assert _relative_names(train) == {"yes/train.wav", "no/train.wav"}
    assert not (_relative_names(train) & _relative_names(validation))
    assert not (_relative_names(train) & _relative_names(test))
    assert not (_relative_names(validation) & _relative_names(test))
    # Stable label encoding regardless of split.
    assert train.label_to_idx == validation.label_to_idx == test.label_to_idx
    assert "_background_noise_" not in train.labels


@pytest.mark.parametrize("split", ["train", "validation", "test"])
def test_mfcc_shape_is_49x10_and_finite(small_gsc: Path, split: str) -> None:
    dataset = GSCDataset(split=split, root=small_gsc)
    for i in range(len(dataset)):
        features, label = dataset[i]
        assert features.shape == (49, 10)
        assert torch.isfinite(features).all()
        assert features.dtype == torch.float32
        assert 0 <= label < len(dataset.labels)


def test_wrong_split_rejected(small_gsc: Path) -> None:
    with pytest.raises(ValueError):
        GSCDataset(split="anything", root=small_gsc)


def test_missing_official_list_rejected(small_gsc: Path) -> None:
    (small_gsc / "validation_list.txt").unlink()
    with pytest.raises(FileNotFoundError, match="validation_list.txt"):
        GSCDataset(root=small_gsc)


def test_missing_listed_wav_rejected(small_gsc: Path) -> None:
    (small_gsc / "yes" / "test.wav").unlink()
    with pytest.raises(FileNotFoundError):
        GSCDataset(root=small_gsc)


def test_real_dataset_matches_official_lists_if_available() -> None:
    """Set GSC_ROOT to the full extracted GSC directory to verify real counts."""
    root_env = os.getenv("GSC_ROOT")
    if not root_env:
        pytest.skip("Set GSC_ROOT to run verification on the actual Speech Commands WAVs")
    root = Path(root_env)
    train = GSCDataset("train", root=root)
    validation = GSCDataset("validation", root=root)
    test = GSCDataset("test", root=root)

    expected_val = set((root / "validation_list.txt").read_text().splitlines())
    expected_test = set((root / "testing_list.txt").read_text().splitlines())
    all_wavs = {
        p.relative_to(root).as_posix()
        for p in root.glob("*/*.wav")
        if p.parent.name != "_background_noise_"
    }
    assert _relative_names(validation) == expected_val
    assert _relative_names(test) == expected_test
    assert _relative_names(train) == all_wavs - expected_val - expected_test
    assert len(validation) == len(expected_val)
    assert len(test) == len(expected_test)
    assert len(train) + len(validation) + len(test) == len(all_wavs)
