# Video Processor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/PySide6-Qt6-blue.svg)](https://doc.qt.io/qtforpython/)

A modern, cross-platform batch video optimization tool powered by FFmpeg with a beautiful PySide6 (Qt) GUI and CLI interface.

## Features

- Batch video compression with predictable quality using CRF-based encoding
- Support for H.264 (libx264) and H.265 (libx265) video codecs
- AAC and Opus audio encoding support
- Preserve input folder structure and original filenames in output
- Modern, responsive GUI with dark/light theme support
- Real-time batch progress tracking with per-file status
- Parallel processing with configurable worker count
- Comprehensive CSV logging with detailed statistics
- Safe processing: never modifies or deletes source files
- Works completely offline - no cloud or network dependencies
- CLI mode for automated workflows and scripts

## Screenshots

*(Add screenshots here once the GUI is ready)*

## Requirements

### System Requirements

- **OS:** Windows 10/11, Linux (Ubuntu 20.04+, Debian 11+, Fedora 36+), or macOS 12+ (Monterey)
- **Python:** 3.10 or higher (3.12+ recommended)
- **FFmpeg:** 7.0 or higher with `ffmpeg` and `ffprobe` in PATH
- **RAM:** 4 GB minimum, 8-16 GB recommended for large batches
- **CPU:** 2 cores minimum, 4+ cores recommended
- **Disk:** 10 GB free minimum (20+ GB recommended for large batches)

### Software Dependencies

- Python 3.10+
- PySide6 (Qt 6 for Python)
- FFmpeg 7.0+ with libx264 and libx265 encoders
- uv (recommended package manager)

## Installation

### Step 1: Install FFmpeg

#### Windows
```powershell
# Option 1: Winget (recommended)
winget install --id=Gyan.FFmpeg -e

# Option 2: Scoop
scoop install ffmpeg

# Option 3: Chocolatey
choco install ffmpeg
```

#### Linux
```bash
# Debian/Ubuntu
sudo apt update && sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

#### macOS
```bash
brew install ffmpeg
```

#### Verify Installation
```bash
ffmpeg -version
ffprobe -version
```

### Step 2: Install Python

#### Windows
```powershell
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

### Step 3: Install uv (Recommended)

```powershell
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Step 4: Install Video Processor

```bash
# Clone the repository
git clone https://github.com/yourusername/video-processor.git
cd video-processor

# Create virtual environment
uv venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install in development mode
uv pip install -e .
```

### Linux Only: Install Qt Runtime Libraries

If the GUI fails to start with a "xcb" error, install the required XCB libraries:

```bash
# Debian/Ubuntu
sudo apt install libxcb1 libxcb-xkb1 libxkbcommon-x11-0 libxcb-cursor0 \
  libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 \
  libxcb-render0 libxcb-shape0 libxcb-sync1 libxcb-xfixes0

# Fedora
sudo dnf install xcb-util-cursor xcb-util-wm xcb-util-keysyms \
  xcb-util-image libxkbcommon-x11
```

## Usage

### GUI Mode

```bash
video-processor-gui
```

1. Launch the application
2. Select your input folder (containing videos to optimize)
3. Select your output folder (where optimized videos will be saved)
4. Configure encoding settings (codec, quality, preset, etc.)
5. Select video extensions to process
6. Click "Start" to begin batch processing
7. Monitor progress in the Progress tab
8. Review logs and results when complete

### CLI Mode

```bash
# Basic usage
video-processor --input "C:\Videos" --output "C:\Optimized"

# With custom settings
video-processor \
  --input "C:\Videos" \
  --output "C:\Optimized" \
  --codec h264 \
  --crf 23 \
  --preset medium \
  --audio-codec aac \
  --audio-bitrate 128 \
  --extensions mp4,mkv,mov

# Enable parallel processing
video-processor \
  --input "C:\Videos" \
  --output "C:\Optimized" \
  --workers 4

# Dry run (preview without processing)
video-processor \
  --input "C:\Videos" \
  --output "C:\Optimized" \
  --dry-run
```

### CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input` | Input folder path | Required |
| `--output` | Output folder path | Required |
| `--codec` | Video codec (h264/h265) | h264 |
| `--crf` | Quality (0-51, lower is better) | 23 (h264) / 28 (h265) |
| `--preset` | Encoding preset | medium |
| `--audio-codec` | Audio codec (aac/opus) | aac |
| `--audio-bitrate` | Audio bitrate (kbps) | 128 |
| `--fps` | Target FPS (same/24/25/30/50/60) | same |
| `--extensions` | Video extensions to process | mp4,mkv,mov,avi,webm |
| `--workers` | Number of parallel workers | CPU count - 1 |
| `--collision` | Collision policy (skip/overwrite/suffix) | skip |
| `--dry-run` | Preview without processing | False |
| `--log-file` | Custom log file path | auto-generated |

## Encoding Settings Guide

### Video Codec

| Codec | Description | Best For | Compatibility |
|-------|-------------|----------|---------------|
| H.264 (libx264) | Standard encoder | Broad compatibility | Very high |
| H.265 (libx265) | Efficient encoder | Smaller files | Moderate |

### Quality (CRF)

CRF ranges from 0 to 51 (lower is higher quality). A change of ±6 is roughly half or double the file size.

**H.264 CRF:**
- Archival: 18-20
- General: 20-24
- Maximum compression: 24-28

**H.265 CRF:**
- Archival: 20-22
- General: 22-28
- Maximum compression: 26-30

### Encoding Preset

| Preset | Speed | Compression |
|--------|-------|-------------|
| ultrafast | Very fast | Low |
| fast | Fast | Moderate |
| medium | Balanced | Good |
| slow | Slow | Better |
| veryslow | Very slow | Best |

### Audio Codec and Bitrate

- AAC: 128-192 kbps recommended
- Opus: 96-160 kbps recommended (more efficient)

## File Structure Preservation

Video Processor preserves the complete input folder structure in the output folder:

```
Input Folder:                      Output Folder:
C:\Videos\                         C:\Optimized\
|-- movies\                        |-- movies\
|   |-- action\                    |   |-- action\
|   |   |-- movie1.mp4  --->       |   |   |-- movie1.mp4
|   |   |-- movie2.mp4             |   |   |-- movie2.mp4
|   |-- comedy\                    |   |-- comedy\
|       |-- funny.mp4  --->        |       |-- funny.mp4
|-- tutorials\                     |-- tutorials\
    |-- python\                    |   |-- python\
        |-- basics.mp4  --->       |       |-- basics.mp4
```

## Logging

Video Processor generates a detailed CSV log file with the following information:

- File paths and timestamps
- Original and output sizes
- Compression ratio and space saved
- Video and audio codec information
- Resolution, frame rate, and bitrate
- Processing time and status
- Error messages (if any)

Example log location: `temp/video_processing_log_20260208_100715.csv`

## Testing

```bash
# Run all tests
python -m unittest

# Run specific test file
python -m unittest tests.test_ffmpeg
python -m unittest tests.test_config
```

## Troubleshooting

### FFmpeg Not Found
```bash
# Verify FFmpeg is installed and in PATH
ffmpeg -version
ffprobe -version
```

### Missing Encoders
```bash
# Check available encoders
ffmpeg -hide_banner -encoders | grep -E "libx264|libx265"
```

### PySide6 Missing
```bash
# Install PySide6
uv pip install pyside6

# Verify installation
python -c "import PySide6; print(PySide6.__version__)"
```

### Qt Platform Plugin "xcb" Not Found (Linux)
Install XCB runtime libraries (see Linux installation section above).

### Processing is Slow
- Use a faster preset (fast or medium)
- Increase CRF for higher compression
- Reduce parallel workers

### Output Quality is Poor
- Lower CRF value (better quality)
- Use a slower preset (slow or veryslow)
- Increase audio bitrate if needed

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python -m unittest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/video-processor.git
cd video-processor

# Create virtual environment
uv venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS

# Install in development mode
uv pip install -e ".[dev]"

# Run tests
python -m unittest

# Run the GUI
video-processor-gui
```

### Project Structure

```
video-processor/
├── src/
│   └── video_processor/
│       ├── __init__.py
│       ├── cli.py              # Command-line interface
│       ├── config.py           # Configuration management
│       ├── engine.py           # Processing engine
│       ├── ffmpeg.py           # FFmpeg wrapper
│       ├── logging.py          # Logging utilities
│       └── gui/                # GUI components
│           ├── __init__.py
│           ├── app.py          # Main application
│           ├── theme.py        # Theme management
│           ├── settings_view.py
│           ├── extensions_view.py
│           ├── progress_view.py
│           └── models.py       # Data models
├── tests/
│   ├── test_ffmpeg.py
│   └── test_config.py
├── pyproject.toml
├── README.md
├── LICENSE
└── REQUIREMENTS.md             # Detailed requirements document
```

## Roadmap

- [ ] GPU-accelerated encoding (NVENC, QSV, AMF, VideoToolbox)
- [ ] Resume interrupted batches
- [ ] Two-pass encoding and target bitrate mode
- [ ] Watch folder mode for continuous processing
- [ ] Advanced filters (crop, scale, deinterlace)
- [ ] Subtitle passthrough and metadata preservation
- [ ] Configuration profiles (save/load JSON)
- [ ] Batch comparison tools

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FFmpeg](https://ffmpeg.org/) - The multimedia framework
- [PySide6](https://doc.qt.io/qtforpython/) - Qt for Python
- [PyQt-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets) - Fluent design components

## Support

- Documentation: See [REQUIREMENTS.md](REQUIREMENTS.md) for detailed requirements
- Issues: Report bugs and request features on GitHub Issues
- Discussions: Join discussions on GitHub Discussions

## Star History

*(Add star history badge once on GitHub)*

---

Made with ❤️ by the open source community
