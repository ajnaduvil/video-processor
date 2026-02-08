from __future__ import annotations

import argparse
import signal
import subprocess
import sys
import time

from .config import AppConfig, PRESETS, _normalize_extensions
from .engine import VideoProcessorEngine


class ConsoleProgress:
    def __init__(self) -> None:
        self._last_progress = {}
        self._last_status = {}

    def on_item_update(self, item) -> None:
        status = item.status
        last_status = self._last_status.get(item.id)
        if status != last_status:
            print(f"[{status}] {item.input_path}")
            self._last_status[item.id] = status
            return

        progress = item.progress
        if progress is None:
            return
        last = self._last_progress.get(item.id, -1)
        if progress >= last + 5:
            print(f"  {progress}% {item.input_path}")
            self._last_progress[item.id] = progress


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Video Processor CLI")
    parser.add_argument("--config", help="Load config JSON")
    parser.add_argument("--save-config", help="Save config JSON")
    parser.add_argument("--input", dest="input_dir", help="Input folder")
    parser.add_argument("--output", dest="output_dir", help="Output folder")
    parser.add_argument("--codec", choices=["h264", "h265"])
    parser.add_argument("--crf", type=int)
    parser.add_argument("--preset", choices=PRESETS)
    parser.add_argument("--audio", choices=["aac", "opus"])
    parser.add_argument("--audio-bitrate", type=int)
    parser.add_argument("--fps", type=int, help="Target FPS (omit to preserve)")
    parser.add_argument("--extensions", help="Comma-separated list, e.g. mp4,mkv")
    parser.add_argument("--parallel", action="store_true")
    parser.add_argument("--no-parallel", action="store_true")
    parser.add_argument("--workers", type=int)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--collision", choices=["skip", "overwrite", "suffix"])
    parser.add_argument("--csv-log", dest="csv_log_path")
    parser.add_argument("--json-log", dest="json_log_path")
    parser.add_argument("--no-csv-log", action="store_true")
    parser.add_argument("--json-log-enable", action="store_true")
    parser.add_argument("--gpu-type", choices=["none", "nvidia", "amd", "intel", "macos"],
                        help="GPU type for hardware acceleration")
    parser.add_argument("--no-gpu", action="store_true", help="Disable GPU acceleration")
    parser.add_argument("--no-hw-decode", action="store_true", help="Disable hardware decoding")
    parser.add_argument("--copy-audio", action="store_true", help="Copy audio stream without re-encoding")
    parser.add_argument("--skip-reencode", action="store_true", help="Skip re-encoding, just copy streams")
    return parser


def apply_args(config: AppConfig, args: argparse.Namespace) -> AppConfig:
    if args.input_dir:
        config.input_dir = args.input_dir
    if args.output_dir:
        config.output_dir = args.output_dir
    if args.codec:
        config.video_codec = args.codec
    if args.crf is not None:
        config.crf = args.crf
    if args.preset:
        config.preset = args.preset
    if args.audio:
        config.audio_codec = args.audio
    if args.audio_bitrate is not None:
        config.audio_bitrate_kbps = args.audio_bitrate
    if args.fps is not None:
        config.target_fps = args.fps
    if args.extensions:
        config.extensions = _normalize_extensions(args.extensions.split(","))
    if args.parallel:
        config.parallel = True
    if args.no_parallel:
        config.parallel = False
    if args.workers is not None:
        config.workers = args.workers
    if args.dry_run:
        config.dry_run = True
    if args.collision:
        config.collision_policy = args.collision
    if args.csv_log_path:
        config.csv_log_path = args.csv_log_path
    if args.json_log_path:
        config.json_log_path = args.json_log_path
    if args.no_csv_log:
        config.enable_csv_log = False
    if args.json_log_enable:
        config.enable_json_log = True
    if hasattr(args, 'gpu_type') and args.gpu_type:
        config.gpu_type = args.gpu_type
    if hasattr(args, 'no_gpu') and args.no_gpu:
        config.use_gpu = False
    if hasattr(args, 'no_hw_decode') and args.no_hw_decode:
        config.use_hw_decode = False
    if hasattr(args, 'copy_audio') and args.copy_audio:
        config.copy_audio = True
    if hasattr(args, 'skip_reencode') and args.skip_reencode:
        config.skip_reencode = True
    return config


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.config:
        config = AppConfig.load_profile(args.config)
    else:
        config = AppConfig()

    config = apply_args(config, args)
    config.validate()

    if args.save_config:
        config.save_profile(args.save_config)

    if not config.input_dir or not config.output_dir:
        print("Input and output folders are required.", file=sys.stderr)
        sys.exit(2)

    # Store handle reference for signal handler
    current_handle = None

    def cleanup():
        """Cleanup function to stop processing and kill ffmpeg processes."""
        nonlocal current_handle
        if current_handle and current_handle.is_running():
            print("\nStopping processing...", file=sys.stderr)
            current_handle.cancel()
            # Wait a bit for graceful shutdown
            deadline = time.time() + 3.0
            while current_handle.is_running() and time.time() < deadline:
                time.sleep(0.1)

        # Force kill any remaining ffmpeg processes
        force_kill_ffmpeg()

    def force_kill_ffmpeg():
        """Force kill ffmpeg processes."""
        try:
            if sys.platform == "win32":
                subprocess.run(
                    ["taskkill", "/F", "/IM", "ffmpeg.exe"],
                    capture_output=True,
                    timeout=3
                )
            else:
                subprocess.run(
                    ["pkill", "-9", "ffmpeg"],
                    capture_output=True,
                    timeout=3
                )
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

    def signal_handler(signum, frame):
        """Handle termination signals (Ctrl+C, etc.)"""
        cleanup()
        sys.exit(1)

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    if sys.platform != "win32":
        signal.signal(signal.SIGTERM, signal_handler)

    reporter = ConsoleProgress()
    engine = VideoProcessorEngine(config, on_item_update=reporter.on_item_update)
    items = engine.scan_inputs()
    if not items:
        print("No matching video files found.")
        return

    current_handle = engine.start_batch(items)
    try:
        while current_handle.is_running():
            time.sleep(0.5)
        current_handle.wait()
    except KeyboardInterrupt:
        cleanup()
        sys.exit(1)

    completed = len([i for i in items if i.status == "completed"])
    failed = len([i for i in items if i.status == "failed"])
    skipped = len([i for i in items if i.status == "skipped"])
    canceled = len([i for i in items if i.status == "canceled"])
    print(f"Completed: {completed}, Failed: {failed}, Skipped: {skipped}, Canceled: {canceled}")


if __name__ == "__main__":
    main()
