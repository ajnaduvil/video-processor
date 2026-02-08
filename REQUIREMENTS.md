# Video Processor - Requirements (Planned)

## Overview

The Video Processor is a planned Python-based batch video optimization tool
powered by FFmpeg with a PySide6 (Qt) user interface. This document defines
the requirements and expected behavior. No features are implemented yet.

## Goals and Scope

- Provide safe, repeatable batch compression with predictable quality.
- Preserve input folder structure and filenames in the output.
- Support both GUI and CLI workflows for casual and automated use.
- Provide a modern, dynamic UI with dark mode as the default theme.
- Keep the UI well organized and clean with clear navigation.
- Provide a dedicated batch-progress view with per-file status and controls.
- Keep all processing local and offline by default.

---

## System Requirements

### Operating System (64-bit)

- Windows 10 or 11
- Linux: modern distribution (Ubuntu 20.04+, Debian 11+, Fedora 36+)
- macOS 12+ (Monterey or later)

### Hardware

#### Minimum
- CPU: 2 cores
- RAM: 4 GB
- Disk: 10 GB free (input + output + temp)

#### Recommended
- CPU: 4+ cores
- RAM: 8-16 GB
- Disk: SSD with 20 GB+ free for larger batches

### Software

#### Python
- Minimum: 3.10 (3.9 is end-of-life)
- Recommended: 3.12 or 3.13

#### PySide6 (Qt for Python)
- Required GUI toolkit: `PySide6`
- Qt 6 runtime is bundled with PySide6 wheels (no separate Qt install required)
- Linux requires X11/XCB runtime libraries (see installation notes)

#### FFmpeg
- Minimum: 7.0
- Recommended: 8.0.1 or newer stable
- Required binaries: `ffmpeg`, `ffprobe` in PATH
- Required video encoders: `libx264`, `libx265`
- Required audio encoders: `aac` and/or `libopus`

#### Optional GPU Acceleration
- NVIDIA NVENC: `h264_nvenc`, `hevc_nvenc`
- Intel Quick Sync: `h264_qsv`, `hevc_qsv`
- AMD AMF: `h264_amf`, `hevc_amf`
- macOS VideoToolbox: `h264_videotoolbox`, `hevc_videotoolbox`
- Linux VAAPI: `h264_vaapi`, `hevc_vaapi`
- Requires compatible GPU drivers and FFmpeg builds with these encoders enabled.

---

## Installation Requirements (Planned)

### Step 1: Install FFmpeg

#### Windows
```powershell
# Option 1: Winget (recommended)
winget install --id=Gyan.FFmpeg -e

# Option 2: Download prebuilt binaries
# https://www.gyan.dev/ffmpeg/builds/
# Extract to C:\ffmpeg and add C:\ffmpeg\bin to PATH

# Option 3: Scoop
scoop install ffmpeg

# Option 4: Chocolatey
choco install ffmpeg
```

#### Linux
```bash
# Debian/Ubuntu
sudo apt update
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch
sudo pacman -S ffmpeg
```

#### macOS
```bash
# Homebrew
brew install ffmpeg
```

#### Verify FFmpeg
```bash
ffmpeg -version
ffprobe -version
```

Optional encoder check:
```bash
ffmpeg -hide_banner -encoders
```
Look for `libx264`, `libx265`, and any optional GPU encoders.

### Step 2: Install Python

#### Windows
```powershell
# From python.org or winget
winget install --id=Python.Python.3.12 -e
python --version
```

#### Linux
```bash
# Debian/Ubuntu
sudo apt install python3 python3-venv

# Fedora
sudo dnf install python3

# Arch
sudo pacman -S python
```

#### macOS
```bash
brew install python@3.12
python3 --version
```

#### Verify Python
```bash
python --version
```

### Step 2b: Linux Qt Runtime Libraries (Linux only)

PySide6 relies on Qt's XCB platform plugin. Install XCB runtime libraries
if the GUI fails to start.

#### Debian/Ubuntu (example)
```bash
sudo apt install \
  libxcb1 libxcb-xkb1 libxkbcommon-x11-0 libxcb-cursor0 \
  libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 \
  libxcb-render0 libxcb-shape0 libxcb-sync1 libxcb-xfixes0
```

#### Fedora (example)
```bash
sudo dnf install xcb-util-cursor xcb-util-wm xcb-util-keysyms xcb-util-image \
  libxkbcommon-x11
```

Package names vary by distro. See Qt Linux requirements if in doubt.

### Step 3: Install uv (recommended)
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Alternative package managers:
- Windows: `winget install --id=astral-sh.uv -e`
- macOS: `brew install uv`

### Step 4: Project Setup (planned)
```bash
cd c:\MyDrive\Projects\Misc\video-processor
uv venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install UI dependency (planned)
uv pip install pyside6

# Verify PySide6
python -c "import PySide6; print(PySide6.__version__)"
```

When implemented:
```bash
uv run python video_processor.py
```

---

## Functional Requirements (Planned)

### MUST
- Allow users to select input and output folders.
- Recursively scan input for supported video extensions.
- Allow enabling/disabling extensions to process.
- Use FFmpeg CRF-based encoding with selectable codec and preset.
- Support H.264 (libx264) and H.265 (libx265).
- Support AAC and Opus audio encoding.
- Preserve folder structure and original filenames in output.
- Provide a safe collision policy (skip, overwrite, or suffix).
- Provide progress feedback and per-file status.
- Allow canceling processing without corrupting output.
- Generate CSV log with per-file details and summary stats.
- Use PySide6 for the GUI with a modern, dynamic layout.
- Default to a dark theme and persist the last-selected theme.
- Keep the UI well organized with clear grouping and navigation.
- Provide a batch-progress view that lists each file with status and progress.
- Show overall batch progress and per-file progress as determinate indicators
  whenever possible.

### SHOULD
- Provide both GUI and CLI (headless) interfaces.
- Support parallel processing with configurable worker count.
- Validate FFmpeg/ffprobe availability at startup.
- Provide configuration profiles (save/load JSON).
- Allow dry-run to preview target files.
- Preserve key metadata (rotation, color space, audio channels) when possible.
- Provide optional JSON log output for automation.
- Provide a light theme option that can be toggled in settings.
- Support HiDPI scaling and responsive layout at common resolutions.
- Allow users to manage the batch from the progress view (pause, resume,
  cancel, retry failed items).
- Provide filters for status (queued, running, completed, failed, skipped).
- Provide status text that explains current work without relying on color only.

### COULD
- GPU-accelerated encoding when supported.
- Resume interrupted batches.
- Two-pass or target-bitrate mode.
- Subtitle passthrough and metadata preservation options.
- Auto-crop/scale and deinterlace options.
- Watch folder mode for continuous processing.

---

## Non-Functional Requirements (Planned)

- Performance: reasonable throughput on 4-core CPU with optional parallelism.
- Reliability: never modify or delete source files; failures must not stop
  the entire batch.
- Usability: sensible defaults, clear validation errors, minimal required inputs.
- UI: non-blocking interface during processing; consistent spacing and typography.
- Observability: human-readable logs plus machine-readable summaries.
- Privacy: all processing local; no telemetry or network use by default.
- Compatibility: handle common containers (MP4, MKV, MOV, AVI, WebM).
- Maintainability: configuration and logs should be forward compatible.
- UI feedback: progress updates must be visible and timely for long-running
  operations to reduce uncertainty.

---

## UI/UX Requirements (Planned)

### Batch Progress View

- Provide a dedicated "Progress" tab or panel focused on batch status.
- Show a list or table of files with key columns:
  - File name (or relative path)
  - Status (queued, processing, completed, failed, skipped)
  - Progress percent (if available) or indeterminate indicator
  - Elapsed time and optional remaining estimate
  - Output size and size saved (when complete)
- Provide a summary header with overall progress, counts, and total time.
- Keep progress indicators determinate when possible; use indeterminate only
  for short or unknown-duration operations.
- Avoid progress bars that reset or move backward.
- Provide quick actions: pause/resume batch, cancel batch, retry failed items,
  open output folder, and copy log path.

### Visual and Interaction Style

- Dark mode is default; allow light mode toggle.
- Use consistent spacing and typography; avoid visual clutter.
- Keep progress status readable (text labels + icons, not color alone).
- Place progress indicators near the content they represent.

---

## Target Workflow (Planned)

1. Launch the application (GUI or CLI).
2. Select input folder and output folder.
3. Choose codecs, quality (CRF), preset, audio bitrate, and FPS mode.
4. Select file extensions to include.
5. Optionally enable dry-run, logging, and parallel processing.
6. Scan folders to preview candidates.
7. Start processing; monitor progress in the Progress tab.
8. Review logs and output results.

---

## Configuration Options Explained

### Video Codec

| Codec | Description | Best For | Compatibility |
|-------|-------------|----------|---------------|
| H.264 (libx264) | Standard encoder | Broad compatibility | Very high |
| H.265 (libx265) | Efficient encoder | Smaller files | Moderate |

### Quality (CRF)

CRF ranges from 0 to 51 (lower is higher quality). A change of plus or minus
6 is roughly half or double the file size.

**x264 guidance**
- Default: 23
- Recommended range: 18-28

**x265 guidance**
- Default: 28
- Recommended range: 20-30

Suggested starting points:
- Archival: 18-20 (x264), 20-22 (x265)
- General: 20-24 (x264), 22-28 (x265)
- Maximum compression: 24-28 (x264), 26-30 (x265)

### Encoding Preset

| Preset | Speed | Compression |
|--------|-------|-------------|
| ultrafast | very fast | low |
| fast | fast | moderate |
| medium | balanced | good |
| slow | slow | better |
| veryslow | very slow | best |

### Audio Codec and Bitrate

- AAC: 128-192 kbps recommended
- Opus: 96-160 kbps recommended (more efficient)

### Target FPS

| Setting | Description |
|---------|-------------|
| same | Preserve original frame rate (recommended) |
| 24, 25, 30, 50, 60 | Encode output at specified FPS |

### Parallel Processing

- Configurable worker count
- Default should be conservative (for example, min(2, cores-1))

---

## Logging Requirements (Planned)

### CSV Columns

| Column | Description |
|--------|-------------|
| Timestamp | Processing timestamp (ISO format) |
| Input Path | Full path to source video |
| Output Path | Full path to processed video |
| Original Size (MB) | Source file size in megabytes |
| Output Size (MB) | Processed file size in megabytes |
| Size Saved (MB) | Actual space saved in megabytes |
| Compression Ratio (%) | Percentage reduction in file size |
| Duration (s) | Video duration in seconds |
| Original Resolution | Source video resolution (e.g., 1920x1080) |
| Output Resolution | Output video resolution |
| Original Video Codec | Source video codec |
| Output Video Codec | Output video codec |
| Original Audio Codec | Source audio codec |
| Output Audio Codec | Output audio codec |
| Original Video Bitrate (kbps) | Source video stream bitrate |
| Output Video Bitrate (kbps) | Output video stream bitrate |
| Original Audio Bitrate (kbps) | Source audio stream bitrate |
| Output Audio Bitrate (kbps) | Output audio stream bitrate |
| Frame Rate (fps) | Video frame rate |
| Processing Time (s) | Time taken to process video |
| Status | Success / Failed / Skipped |
| Error Message | Details if processing failed |

### Summary Statistics

- Total videos processed
- Successful vs. failed count
- Total original and output sizes
- Overall compression ratio
- Total processing time

---

## File System Behavior (Planned)

The application must preserve the complete input folder structure in the
output folder.

Example:

```
Input Folder:                      Output Folder:
C:\Videos\                         C:\Optimized\
|-- movies\                        |-- movies\
|   |-- action\                    |   |-- action\
|   |   |-- movie1.mp4  --->       |   |   |-- movie1.mp4
|   |   |-- movie2.mp4             |   |   |-- movie2.mp4
|   |-- comedy\                    |   |-- comedy\
|   |   |-- funny.mp4  --->        |   |   |-- funny.mp4
|   |-- drama\                     |   |-- drama\
|       |-- sad.mp4  --->          |       |-- sad.mp4
|       |-- happy.mp4              |       |-- happy.mp4
|-- tutorials\                     |-- tutorials\
    |-- python\                    |   |-- python\
        |-- basics.mp4  --->       |       |-- basics.mp4
        |-- advanced.mp4           |       |-- advanced.mp4
```

Important notes:
- All subdirectories must be created automatically
- Original filenames must be preserved
- File extensions must be preserved (unless output format changes)
- Empty folders do not need to be created

---

## Network and Storage Considerations

### Local Processing
- All video processing happens locally on the machine
- No files are uploaded to external servers
- No internet connection required for processing

### Storage Requirements

| Scenario | Input Size | Output Size | Temporary Space Needed |
|----------|------------|-------------|------------------------|
| Small batch (5-10 videos) | 5 GB | 2-5 GB | 10 GB |
| Medium batch (20-50 videos) | 20 GB | 8-12 GB | 30 GB |
| Large batch (50-100 videos) | 50 GB | 20-30 GB | 80 GB |

Recommendation: ensure adequate free disk space before starting large batches.

---

## Troubleshooting (Expected)

### Issue: FFmpeg Not Found
Symptoms:
- Application reports that `ffmpeg` or `ffprobe` is missing

Solutions:
1. Verify installation:
   - `ffmpeg -version`
   - `ffprobe -version`
2. Ensure FFmpeg is in PATH
3. Restart the application

### Issue: Missing Encoders
Symptoms:
- Encoding fails with "Unknown encoder" (libx264/libx265)

Solutions:
1. Run `ffmpeg -hide_banner -encoders`
2. Install a full FFmpeg build that includes libx264/libx265

### Issue: PySide6 Missing (GUI)
Symptoms:
- Application fails to start GUI or reports missing PySide6

Solutions:
1. Install PySide6 in the active environment: `uv pip install pyside6`
2. Verify with: `python -c "import PySide6; print(PySide6.__version__)"`

### Issue: Qt Platform Plugin "xcb" Not Found (Linux)
Symptoms:
- GUI fails to start with a message about missing "xcb"

Solutions:
1. Install XCB runtime libraries (package names vary by distro)
2. Reinstall PySide6 after system libraries are installed

### Issue: No Video Files Found
Symptoms:
- Scan returns zero files

Solutions:
1. Verify input folder path
2. Ensure extension filters include your formats
3. Confirm files are not hidden or encrypted

### Issue: Processing is Slow
Symptoms:
- Encoding takes very long time

Solutions:
1. Use a faster preset (fast or medium)
2. Increase CRF for higher compression
3. Reduce parallel workers or disable parallel processing

### Issue: Output Quality is Poor
Symptoms:
- Videos look blurry or blocky

Solutions:
1. Lower CRF value (better quality)
2. Use a slower preset (slow or veryslow)
3. Increase audio bitrate if needed

### Issue: Hardware Encoder Not Available
Symptoms:
- FFmpeg reports missing NVENC/QSV/AMF/VideoToolbox

Solutions:
1. Update GPU drivers
2. Use a build of FFmpeg that includes the encoder
3. Fall back to software encoding

---

## Out of Scope (v1)

- DRM or protected content handling
- Automatic content-aware cropping or upscaling
- Cloud processing or remote queues
- Advanced color grading pipelines

---

## Quick Reference

### Minimum Viable Setup
- OS: Windows 10/11, modern Linux, macOS 12+
- Python: 3.10+ with PySide6
- FFmpeg: 7.0+ with ffmpeg and ffprobe in PATH
- RAM: 4 GB
- CPU: 2 cores
- Disk: 10 GB free

### Recommended Setup
- OS: Windows 11, Ubuntu 22.04+, macOS 13+
- Python: 3.12 or 3.13 with PySide6
- FFmpeg: 8.0.1+ stable
- RAM: 8-16 GB
- CPU: 4+ cores
- Disk: 20+ GB free on SSD

### Installation Commands Summary
```bash
# 1. Install FFmpeg
# Windows:
winget install --id=Gyan.FFmpeg -e
# Linux:
sudo apt install ffmpeg
# macOS:
brew install ffmpeg

# 2. Install uv (recommended)
# Windows:
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# Linux/macOS:
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. Project setup (planned)
cd c:\MyDrive\Projects\Misc\video-processor
uv venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install UI dependency (planned)
uv pip install pyside6
```

---

## Sources

- FFmpeg downloads and releases: https://ffmpeg.org/download.html
- Python version lifecycle: https://devguide.python.org/versions/
- uv installation docs: https://docs.astral.sh/uv/getting-started/installation/
- Qt for Python (PySide6) docs: https://doc.qt.io/qtforpython-6/gettingstarted/index.html
- Qt Linux requirements (XCB): https://doc.qt.io/qt-6/linux-requirements.html
- PySide6 palette/theming: https://doc.qt.io/qtforpython-6/PySide6/QtGui/QPalette.html
- Progress indicators guidance (NNGroup): https://www.nngroup.com/articles/progress-indicators/
- Progress bar guidance (Fluent UI): https://fluent2.microsoft.design/components/web/react/core/progressbar/usage
- CRF guide for x264/x265: https://slhck.info/video/2017/02/24/crf-guide.html

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.2.0 | 2026-02-07 | Requirements refresh and planned features |

---

Document Version: 1.1
Last Updated: February 7, 2026
Application Version: 0.0.0 (planned)
