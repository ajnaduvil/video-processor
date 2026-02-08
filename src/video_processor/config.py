from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
import json
import os
import sys
import subprocess
import shutil
from typing import Any, Iterable


PRESETS = [
    "ultrafast",
    "superfast",
    "veryfast",
    "faster",
    "fast",
    "medium",
    "slow",
    "slower",
    "veryslow",
    "placebo",
]

GPU_TYPES = [
    "none",
    "nvidia",
    "amd",
    "intel",
    "macos",
]


def detect_gpu_type() -> str:
    """Detect available GPU type for hardware acceleration."""
    try:
        # Check for NVIDIA GPU
        if sys.platform == "win32":
            try:
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                    capture_output=True,
                    timeout=3
                )
                if result.returncode == 0 and result.stdout.strip():
                    return "nvidia"
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
        elif sys.platform == "darwin":  # macOS
            # macOS uses VideoToolbox for hardware encoding
            return "macos"
        else:
            # Linux - check for NVIDIA
            try:
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                    capture_output=True,
                    timeout=3
                )
                if result.returncode == 0 and result.stdout.strip():
                    return "nvidia"
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

        # Check for Intel Quick Sync
        if sys.platform == "win32":
            # On Windows, check for Intel Graphics
            try:
                result = subprocess.run(
                    ["wmic", "path", "win32_VideoController", "get", "name"],
                    capture_output=True,
                    timeout=3,
                    text=True
                )
                if result.returncode == 0 and "intel" in result.stdout.lower():
                    return "intel"
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

        # Check for AMD GPU
        if sys.platform == "win32":
            try:
                result = subprocess.run(
                    ["wmic", "path", "win32_VideoController", "get", "name"],
                    capture_output=True,
                    timeout=3,
                    text=True
                )
                if result.returncode == 0 and "amd" in result.stdout.lower() or "radeon" in result.stdout.lower():
                    return "amd"
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

    except Exception:
        pass

    return "none"


def default_extensions() -> list[str]:
    return [
        ".mp4",
        ".mkv",
        ".mov",
        ".avi",
        ".webm",
        ".wmv",
        ".m4v",
        ".mpg",
        ".mpeg",
        ".flv",
        ".3gp",
        ".ogv",
    ]


def default_workers() -> int:
    cpu = os.cpu_count() or 2
    return max(1, min(2, cpu - 1))


def _normalize_extensions(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    for val in values:
        if not val:
            continue
        ext = val.strip().lower()
        if not ext:
            continue
        if not ext.startswith("."):
            ext = f".{ext}"
        if ext not in result:
            result.append(ext)
    return result


@dataclass
class AppConfig:
    input_dir: str = ""
    output_dir: str = ""
    video_codec: str = "h265"
    crf: int = 23
    preset: str = "medium"
    audio_codec: str = "aac"
    audio_bitrate_kbps: int = 128
    target_fps: int | None = 30
    extensions: list[str] = field(default_factory=default_extensions)
    parallel: bool = True
    workers: int = field(default_factory=default_workers)
    dry_run: bool = False
    collision_policy: str = "skip"
    enable_csv_log: bool = True
    csv_log_path: str = ""
    enable_json_log: bool = False
    json_log_path: str = ""
    theme: str = "dark"
    gpu_type: str = field(default_factory=detect_gpu_type)
    use_gpu: bool = True
    use_hw_decode: bool = True
    copy_audio: bool = False
    skip_reencode: bool = False

    def normalize(self) -> None:
        self.video_codec = self.video_codec.lower().strip()
        self.audio_codec = self.audio_codec.lower().strip()
        self.preset = self.preset.lower().strip()
        self.collision_policy = self.collision_policy.lower().strip()
        self.extensions = _normalize_extensions(self.extensions)

    def validate(self) -> None:
        self.normalize()
        if self.video_codec not in {"h264", "h265"}:
            raise ValueError("video_codec must be 'h264' or 'h265'")
        if self.audio_codec not in {"aac", "opus"}:
            raise ValueError("audio_codec must be 'aac' or 'opus'")
        if not (0 <= self.crf <= 51):
            raise ValueError("crf must be between 0 and 51")
        if self.preset not in PRESETS:
            raise ValueError(f"preset must be one of: {', '.join(PRESETS)}")
        if self.audio_bitrate_kbps <= 0:
            raise ValueError("audio_bitrate_kbps must be positive")
        if self.target_fps is not None and self.target_fps <= 0:
            raise ValueError("target_fps must be positive or None")
        if self.workers < 1:
            raise ValueError("workers must be >= 1")
        if self.collision_policy not in {"skip", "overwrite", "suffix"}:
            raise ValueError("collision_policy must be skip/overwrite/suffix")
        if self.theme not in {"dark", "light"}:
            raise ValueError("theme must be 'dark' or 'light'")

    def to_dict(self) -> dict[str, Any]:
        self.normalize()
        return asdict(self)

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "AppConfig":
        config = AppConfig(**data)
        config.normalize()
        return config

    def save_profile(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8") as handle:
            json.dump(self.to_dict(), handle, indent=2, sort_keys=True)

    @staticmethod
    def load_profile(path: str | Path) -> "AppConfig":
        source = Path(path)
        with source.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return AppConfig.from_dict(data)


def user_settings_path() -> Path:
    root = Path.home() / ".video_processor"
    root.mkdir(parents=True, exist_ok=True)
    return root / "ui_settings.json"


def load_ui_settings() -> dict[str, Any]:
    path = user_settings_path()
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}


def save_ui_settings(data: dict[str, Any]) -> None:
    path = user_settings_path()
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
