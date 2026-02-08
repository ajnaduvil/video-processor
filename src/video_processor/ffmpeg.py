from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import math
import shutil
import subprocess
from typing import Any


@dataclass
class MediaInfo:
    duration: float | None = None
    width: int | None = None
    height: int | None = None
    video_codec: str | None = None
    audio_codec: str | None = None
    fps: float | None = None
    rotation: int | None = None


class FFmpegNotFound(RuntimeError):
    pass


def find_executable(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise FFmpegNotFound(f"{name} not found in PATH")
    return path


def check_ffmpeg() -> tuple[str, str]:
    return find_executable("ffmpeg"), find_executable("ffprobe")


def _parse_fraction(value: str | None) -> float | None:
    if not value:
        return None
    if value == "0/0":
        return None
    if "/" in value:
        num, denom = value.split("/", 1)
        try:
            num_f = float(num)
            denom_f = float(denom)
            if denom_f == 0:
                return None
            return num_f / denom_f
        except ValueError:
            return None
    try:
        return float(value)
    except ValueError:
        return None


def probe_media(path: str | Path, ffprobe_path: str | None = None) -> MediaInfo:
    ffprobe = ffprobe_path or find_executable("ffprobe")
    cmd = [
        ffprobe,
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=index,codec_type,codec_name,width,height,avg_frame_rate,r_frame_rate,channels,sample_rate,bit_rate:stream_tags=rotate",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffprobe failed")
    data: dict[str, Any] = json.loads(result.stdout)
    info = MediaInfo()

    duration_str = data.get("format", {}).get("duration")
    try:
        info.duration = float(duration_str) if duration_str else None
    except ValueError:
        info.duration = None

    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video" and info.video_codec is None:
            info.video_codec = stream.get("codec_name")
            info.width = stream.get("width")
            info.height = stream.get("height")
            info.fps = _parse_fraction(stream.get("avg_frame_rate")) or _parse_fraction(
                stream.get("r_frame_rate")
            )
            rotate = stream.get("tags", {}).get("rotate")
            if rotate is not None:
                try:
                    info.rotation = int(rotate)
                except ValueError:
                    info.rotation = None
        if stream.get("codec_type") == "audio" and info.audio_codec is None:
            info.audio_codec = stream.get("codec_name")
    return info


def build_ffmpeg_command(
    input_path: str | Path,
    output_path: str | Path,
    *,
    video_codec: str,
    crf: int,
    preset: str,
    audio_codec: str,
    audio_bitrate_kbps: int,
    target_fps: int | None,
    overwrite: bool,
    gpu_type: str = "none",
    use_gpu: bool = True,
    use_hw_decode: bool = True,
    copy_audio: bool = False,
    skip_reencode: bool = False,
) -> list[str]:
    # If skip reencode is enabled, just copy the streams
    if skip_reencode:
        return [
            "ffmpeg",
            "-hide_banner",
            "-nostats",
            "-y" if overwrite else "-n",
            "-i",
            str(input_path),
            "-c",
            "copy",
            "-map_metadata",
            "0",
            str(output_path)
        ]

    codec_map = {"h264": "libx264", "h265": "libx265"}
    audio_map = {"aac": "aac", "opus": "libopus"}

    # Use GPU-accelerated codecs if GPU is enabled and available
    hwaccel = None
    if use_gpu and gpu_type != "none":
        if gpu_type == "nvidia":
            codec_map = {"h264": "h264_nvenc", "h265": "hevc_nvenc"}
            hwaccel = "cuda"
        elif gpu_type == "amd":
            codec_map = {"h264": "h264_amf", "h265": "hevc_amf"}
            hwaccel = "d3d11va"
        elif gpu_type == "intel":
            codec_map = {"h264": "h264_qsv", "h265": "hevc_qsv"}
            hwaccel = "qsv"
        elif gpu_type == "macos":
            codec_map = {"h264": "h264_videotoolbox", "h265": "hevc_videotoolbox"}
            hwaccel = "videotoolbox"

    vcodec = codec_map[video_codec]

    # Audio handling: copy or re-encode
    if copy_audio:
        acodec = "copy"
    else:
        acodec = audio_map[audio_codec]

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-nostats",
        "-y" if overwrite else "-n",
    ]

    # Add hardware acceleration for decoding
    if hwaccel and use_hw_decode:
        cmd.extend(["-hwaccel", hwaccel])

    cmd.extend([
        "-i",
        str(input_path),
        "-map_metadata",
        "0",
        "-map",
        "0:v:0?",
        "-map",
        "0:a:0?",
        "-c:v",
        vcodec,
    ])

    # Only add audio bitrate if re-encoding
    if not copy_audio:
        cmd.extend([
            "-preset",
            preset,
            "-crf",
            str(crf),
            "-b:a",
            f"{audio_bitrate_kbps}k",
        ])
    else:
        # For GPU encoders, still need preset and crf for video
        cmd.extend([
            "-preset",
            preset,
            "-crf",
            str(crf),
        ])

    if target_fps:
        cmd += ["-r", str(target_fps)]

    # Add audio codec (copy or specific codec)
    cmd.extend(["-c:a", acodec])

    # Add -strict experimental flag for opus codec (required for MP4/MOV containers)
    if audio_codec == "opus" and not copy_audio:
        cmd.append("-strict")
        cmd.append("experimental")

    # Add movflags for fast streaming
    if str(output_path).lower().endswith(('.mp4', '.mov')):
        cmd.extend(["-movflags", "+faststart"])

    cmd.append(str(output_path))
    return cmd


def progress_from_out_time(out_time_us: int, duration: float | None) -> int | None:
    if duration is None or duration <= 0:
        return None
    total_us = duration * 1_000_000.0
    if total_us <= 0:
        return None
    return max(0, min(100, int(math.floor((out_time_us / total_us) * 100))))
