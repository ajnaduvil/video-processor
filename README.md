# Video Processor

Batch video optimizer using FFmpeg with a PySide6 GUI and CLI.

## Requirements

- Python 3.10+
- FFmpeg 7.0+ (`ffmpeg` and `ffprobe` in PATH)

## Install (uv)

```bash
uv venv
.venv\Scripts\activate
uv pip install -e .
```

## Run GUI

```bash
video-processor-gui
```

## Run CLI

```bash
video-processor --input "C:\Videos" --output "C:\Optimized"
```

## Tests

```bash
python -m unittest
```
