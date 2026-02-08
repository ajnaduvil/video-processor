from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import csv
import json
from typing import Any

from .ffmpeg import MediaInfo


@dataclass
class SummaryStats:
    total: int = 0
    completed: int = 0
    failed: int = 0
    skipped: int = 0
    canceled: int = 0
    total_input_bytes: int = 0
    total_output_bytes: int = 0
    total_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "completed": self.completed,
            "failed": self.failed,
            "skipped": self.skipped,
            "canceled": self.canceled,
            "total_input_bytes": self.total_input_bytes,
            "total_output_bytes": self.total_output_bytes,
            "total_saved_bytes": max(0, self.total_input_bytes - self.total_output_bytes),
            "compression_ratio_percent": self.compression_ratio_percent(),
            "total_seconds": self.total_seconds,
        }

    def compression_ratio_percent(self) -> float:
        if self.total_input_bytes <= 0:
            return 0.0
        saved = max(0, self.total_input_bytes - self.total_output_bytes)
        return (saved / self.total_input_bytes) * 100.0


class BatchLogger:
    def __init__(
        self,
        *,
        output_dir: str | Path,
        enable_csv: bool,
        enable_json: bool,
        csv_path: str | Path | None = None,
        json_path: str | Path | None = None,
    ) -> None:
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_path = (
            Path(csv_path)
            if csv_path
            else self.output_dir / f"video_processing_log_{timestamp}.csv"
        )
        self.json_path = (
            Path(json_path)
            if json_path
            else self.output_dir / f"video_processing_log_{timestamp}.jsonl"
        )
        self.enable_csv = enable_csv
        self.enable_json = enable_json
        self.summary = SummaryStats()
        self._csv_file = None
        self._json_file = None

        if self.enable_csv:
            self.csv_path.parent.mkdir(parents=True, exist_ok=True)
            self._csv_file = self.csv_path.open("w", newline="", encoding="utf-8")
            self._csv_writer = csv.writer(self._csv_file)
            self._csv_writer.writerow(
                [
                    "Timestamp",
                    "Input Path",
                    "Output Path",
                    "Original Size (MB)",
                    "Output Size (MB)",
                    "Size Saved (MB)",
                    "Compression Ratio (%)",
                    "Duration (s)",
                    "Original Resolution",
                    "Output Resolution",
                    "Original Video Codec",
                    "Output Video Codec",
                    "Original Audio Codec",
                    "Output Audio Codec",
                    "Original Video Bitrate (kbps)",
                    "Output Video Bitrate (kbps)",
                    "Original Audio Bitrate (kbps)",
                    "Output Audio Bitrate (kbps)",
                    "Frame Rate (fps)",
                    "Processing Time (s)",
                    "Status",
                    "Error Message",
                ]
            )

        if self.enable_json:
            self.json_path.parent.mkdir(parents=True, exist_ok=True)
            self._json_file = self.json_path.open("w", encoding="utf-8")

    def close(self) -> None:
        if self._csv_file:
            self._csv_file.close()
        if self._json_file:
            self._json_file.close()

    def record_item(
        self,
        *,
        timestamp: str,
        input_path: str,
        output_path: str,
        status: str,
        error_message: str,
        media: MediaInfo | None,
        output_media: MediaInfo | None,
        input_bytes: int | None,
        output_bytes: int | None,
        processing_seconds: float | None,
    ) -> None:
        input_mb = (input_bytes or 0) / (1024 * 1024)
        output_mb = (output_bytes or 0) / (1024 * 1024)
        saved_mb = max(0.0, input_mb - output_mb)
        ratio = 0.0
        if input_mb > 0:
            ratio = (saved_mb / input_mb) * 100.0

        if self.enable_csv and self._csv_file:
            self._csv_writer.writerow(
                [
                    timestamp,
                    input_path,
                    output_path,
                    f"{input_mb:.3f}",
                    f"{output_mb:.3f}",
                    f"{saved_mb:.3f}",
                    f"{ratio:.2f}",
                    f"{media.duration:.2f}" if media and media.duration else "",
                    _resolution(media),
                    _resolution(output_media),
                    media.video_codec if media else "",
                    output_media.video_codec if output_media else "",
                    media.audio_codec if media else "",
                    output_media.audio_codec if output_media else "",
                    "",
                    "",
                    "",
                    "",
                    f"{media.fps:.2f}" if media and media.fps else "",
                    f"{processing_seconds:.2f}" if processing_seconds else "",
                    status,
                    error_message,
                ]
            )

        if self.enable_json and self._json_file:
            record = {
                "timestamp": timestamp,
                "input_path": input_path,
                "output_path": output_path,
                "status": status,
                "error_message": error_message,
                "input_bytes": input_bytes,
                "output_bytes": output_bytes,
                "processing_seconds": processing_seconds,
                "media": media.__dict__ if media else None,
                "output_media": output_media.__dict__ if output_media else None,
            }
            self._json_file.write(json.dumps(record) + "\n")

        self._update_summary(status, input_bytes, output_bytes, processing_seconds)

    def _update_summary(
        self,
        status: str,
        input_bytes: int | None,
        output_bytes: int | None,
        processing_seconds: float | None,
    ) -> None:
        self.summary.total += 1
        if status == "completed":
            self.summary.completed += 1
        elif status == "failed":
            self.summary.failed += 1
        elif status == "skipped":
            self.summary.skipped += 1
        elif status == "canceled":
            self.summary.canceled += 1
        if input_bytes:
            self.summary.total_input_bytes += input_bytes
        if output_bytes:
            self.summary.total_output_bytes += output_bytes
        if processing_seconds:
            self.summary.total_seconds += processing_seconds


def _resolution(info: MediaInfo | None) -> str:
    if not info or not info.width or not info.height:
        return ""
    return f"{info.width}x{info.height}"
