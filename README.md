# Speccle

A lightweight desktop utility that detects and displays your system's hardware and OS specifications.

![Speccle Screenshot](screenshot.png)

## Features

- **Automatic Detection**: Gathers system specs on launch
- **One-Click Copy**: Copy all specs to clipboard instantly
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Privacy-First**: No network calls, no telemetry, no persistent storage
- **Fast**: Startup target under 500ms
- **Non-Privileged**: No admin/root required

## Detected Specifications

| Category | Details |
|----------|---------|
| **OS** | Name, version, build number, architecture |
| **CPU** | Model, manufacturer, cores, threads, clock speed |
| **RAM** | Total installed, available memory |
| **GPU** | Name, vendor, VRAM |
| **Storage** | Drive type (SSD/HDD/NVMe), size, free space |
| **Motherboard** | Manufacturer, model |
| **System** | Hostname |

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone or download this repository:
   ```bash
   cd Speccle
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python speccle.py
   ```

## Build Standalone Executable

To create a standalone `.exe` (Windows) or app bundle (macOS):

```bash
# Install PyInstaller
pip install pyinstaller

# Build single executable
pyinstaller --onefile --windowed --name Speccle speccle.py
```

The executable will be in the `dist/` folder.

### Build Options

| Flag | Description |
|------|-------------|
| `--onefile` | Single executable file |
| `--windowed` | No console window (GUI only) |
| `--icon=icon.ico` | Custom application icon |
| `--name Speccle` | Output filename |

## Technical Details

### How System Info is Gathered

| Component | Method |
|-----------|--------|
| **OS** | `platform` module (cross-platform) |
| **CPU** | `platform.processor()` + `psutil.cpu_count()` + WMI (Windows) |
| **RAM** | `psutil.virtual_memory()` |
| **GPU** | WMI `Win32_VideoController` (Windows) |
| **Storage** | `psutil.disk_partitions()` + WMI for drive type |
| **Motherboard** | WMI `Win32_BaseBoard` (Windows) |
| **Hostname** | `socket.gethostname()` |

### How Clipboard Copying Works

The application uses tkinter's built-in clipboard functionality:

```python
root.clipboard_clear()
root.clipboard_append(text)
```

This is native OS integration - no external dependencies required.

### Architecture

```
┌─────────────────────────────────────────┐
│              SpeccleApp                 │
│  ┌─────────────────────────────────┐    │
│  │         tkinter Window          │    │
│  │  ┌───────────────────────────┐  │    │
│  │  │     Text Area (specs)     │  │    │
│  │  └───────────────────────────┘  │    │
│  │  ┌───────────────────────────┐  │    │
│  │  │   Copy to Clipboard Btn   │  │    │
│  │  └───────────────────────────┘  │    │
│  └─────────────────────────────────┘    │
│                  │                      │
│                  ▼                      │
│       SystemInfoCollector               │
│  ┌─────────┬─────────┬─────────┐        │
│  │ psutil  │   WMI   │platform │        │
│  └─────────┴─────────┴─────────┘        │
└─────────────────────────────────────────┘
```

## Dependencies

| Package | Purpose | Platform |
|---------|---------|----------|
| `psutil` | CPU, RAM, disk info | All |
| `WMI` | Detailed hardware info | Windows |
| `pywin32` | WMI dependency | Windows |
| `tkinter` | GUI (included with Python) | All |

## Example Output

```
OS: Windows 11 Pro 23H2 (Build 22631)
Architecture: AMD64

CPU: AMD Ryzen 9 7950X 16-Core Processor
Cores: 16 / Threads: 32 @ 4.50 GHz

RAM: 64 GB
     (48.2 GB available)

GPU: NVIDIA GeForce RTX 4090 (24 GB VRAM)

Storage:
  - C:\ NVMe SSD – 2.0 TB (1.3 TB free)
  - D:\ HDD – 4.0 TB (2.8 TB free)

Motherboard: ASUS ROG STRIX X670E-E GAMING WIFI
Hostname: DESKTOP-ALPHA
```

## License

MIT License - Use freely, modify freely, no attribution required.

## Troubleshooting

### "WMI module not found"

This is normal on macOS/Linux. The app will still work, but some details (GPU VRAM, motherboard) may be limited.

### "psutil not found"

Run: `pip install psutil`

### GUI doesn't appear

Ensure you have tkinter installed. On Linux:
```bash
sudo apt-get install python3-tk
```

### Missing GPU information

GPU detection relies on WMI on Windows. Ensure your graphics drivers are installed.

---

*Built for sysadmins who appreciate boring, reliable tools.*
