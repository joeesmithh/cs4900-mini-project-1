# CS 4900 Mini Project 1 — Camera App for Visually Impaired

A speech-controlled desktop application that guides visually impaired users to photograph an object and place it in a specific region of the frame. The user interacts entirely via voice; the app responds with spoken guidance and triggers the capture automatically.

## Documentation

| Document                     | Link                                                |
| ---------------------------- | --------------------------------------------------- |
| Project description          | [cs4900_project_01.md](./docs/cs4900_project_01.md) |
| Object detection information | [object_detection.md](./docs/object_detection.md)   |

## Requirements

- Python 3.10+
- Working microphone and speakers
- Internet connection (Google Speech API + first-run YOLOv8 model download)

## Installation

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

## Usage

```bash
python3 main.py
```

When prompted, speak the name of an object (e.g. `bottle`, `cup`, `laptop`) and a target zone (`top left`, `top right`, `bottom left`, `bottom right`, or `center`). The app will guide you with spoken directions until the object is positioned correctly, then take the photo automatically. Captures are saved to `captures/`.

## Debug Modes

Test individual components in isolation:

| Component      | Description                           | Argument      | Full Command                 |
| -------------- | ------------------------------------- | ------------- | ---------------------------- |
| Text-to-speech | Type text to hear it spoken           | `--tts` | `python main.py --tts` |
| Speech-to-text | Speak in microphone to see transcript | `--stt` | `python main.py --stt` |
