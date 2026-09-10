# CS 4900 Mini Project 1 — Camera App for Visually Impaired

A speech-controlled desktop application that guides visually impaired users to photograph an object and place it in a specific region of the frame. The user interacts entirely via voice; the app responds with spoken guidance and triggers the capture automatically.

## Documentation

| Document                     | Link                                                |
| ---------------------------- | --------------------------------------------------- |
| Project description          | [cs4900_project_01.md](./docs/cs4900_project_01.md) |
| Object detection information | [object_detection.md](./docs/object_detection.md)   |
| Pipeline flowchart           | [pipeline.md](./docs/pipeline.md)                   |

## Requirements

- Python 3.10+
- Working microphone and speakers
- `ffmpeg` available on the system `PATH` (used by OpenAI Whisper)
- Internet connection for the first run only (downloads the Whisper `base` model,
  ~140 MB, and the YOLOv8 model). Speech recognition then runs fully offline.

## System dependencies (ffmpeg)

OpenAI's Whisper requires the `ffmpeg` binary on your `PATH`.

### Windows

```powershell
winget install --id=Gyan.FFmpeg -e
```

### macOS

```bash
brew install ffmpeg
```

### Linux (Debian / Ubuntu)

```bash
sudo apt install ffmpeg
```

Verify installation with `ffmpeg -version`

## Installation

### Windows

```powershell
# Initialize virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\activate

# Update Python package manager
python -m pip install --upgrade pip

# Install PyTorch (CPU build) for Whisper and Ultralytics
python -m pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining requirements
python -m pip install -r requirements.txt
```

### macOS / Linux

```bash
# Initialize virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Update Python package manager
python3 -m pip install --upgrade pip

# Install PyTorch (CPU build) for Whisper and Ultralytics
python3 -m pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining requirements
python3 -m pip install -r requirements.txt
```

The explicit `torch` line installs the smaller size CPU-only PyTorch build, which is plenty for the Whisper `base` model on short voice commands.

## Usage

```bash
python3 main.py
```

| Mode              | Description                                                                         | Argument | Full Command           |
| ----------------- | ----------------------------------------------------------------------------------- | -------- | ---------------------- |
| Headless (no GUI) | Run the program with in default speech interaction mode                             | —        | `python main.py`       |
| Live camera view  | Run the program with speech interaction + live camera and capture view side-by-side | `--gui`  | `python main.py --gui` |
| Select TTS voice  | Pick the pyttsx3 voice by index (see `--voices`); combines with any mode; default `0` | `--voice N` | `python main.py --voice 1` |

The first launch pauses briefly to download (first run only) and load the Whisper `base` model. When prompted, speak the name of an object (e.g. "bottle", "cup", "laptop") and a target zone ("top left", "top right", "bottom left", "bottom right", or "center"). The app will guide you with spoken directions until the object is positioned correctly, then take the photo automatically. Captures are saved to `captures/`.

## Debug Modes

Test individual components in isolation:

| Component             | Description                           | Argument   | Full Command              |
| --------------------- | ------------------------------------- | ---------- | ------------------------- |
| Text-to-speech        | Type text to hear it spoken           | `--tts`    | `python main.py --tts`    |
| Text-to-speech voices | List and hear available TTS voices    | `--voices` | `python main.py --voices` |
| Speech-to-text        | Speak in microphone to see transcript | `--stt`    | `python main.py --stt`    |
| Object detection      | YOLO-annotated detection feed         | `--detect` | `python main.py --detect` |
