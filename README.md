# AI Physical Controller

Control your mouse with hand gestures using a webcam, OpenCV, MediaPipe, and PyAutoGUI.

This project turns your hand into a virtual input device for:
- Cursor movement
- Left click
- Right click
- Scroll mode (in the controller version)

It is lightweight, runs locally, and is great for learning computer vision + human-computer interaction.

## Features

- Real-time hand landmark tracking
- Smooth cursor movement using weighted averaging
- Gesture-based left and right click
- Gesture-based vertical scrolling (in `vision_controller.py`)
- On-screen hand skeleton and gesture feedback
- Emergency mouse failsafe via PyAutoGUI

## Project Files

- `vision_controller.py`:
	Main, cleaner controller implementation with class-based structure and scroll support.
- `vision_test.py`:
	Earlier prototype script focused on basic movement and click gestures.

## How It Works

MediaPipe detects 21 hand landmarks per frame. The app maps landmark positions from camera space to screen space and triggers mouse actions based on distances between fingertips.

Gesture mapping used in this project:
- Move cursor: index finger tip position
- Left click: thumb + index finger pinch
- Right click: thumb + middle finger pinch
- Scroll mode (`vision_controller.py`): index + middle finger pinch, then move vertically

## Requirements

- Python 3.10+
- Webcam
- Windows/macOS/Linux

Python packages:
- `opencv-python`
- `mediapipe`
- `pyautogui`

## Quick Start (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install opencv-python pyautogui "mediapipe==0.10.14"
```

Then run:

```powershell
python vision_controller.py
```

Press `q` in the OpenCV window to quit.

## MediaPipe Version Note

This code uses the legacy API `mp.solutions.hands`.

If you see this error:

```text
AttributeError: module 'mediapipe' has no attribute 'solutions'
```

install a compatible version:

```powershell
pip install --force-reinstall "mediapipe==0.10.14"
```

## Controls

| Action | Gesture | Script |
|---|---|---|
| Move cursor | Point with index finger | Both |
| Left click | Thumb and index pinch | Both |
| Right click | Thumb and middle pinch | Both |
| Scroll | Pinch index and middle, move hand up/down | `vision_controller.py` |
| Exit app | Press `q` key in preview window | Both |

## Tuning Guide

You can quickly adjust behavior by changing threshold values:

- Smoothing:
	`closeness` in both scripts.
	Higher value = smoother but slower cursor.
- Left click threshold:
	`dist < 40` in `vision_controller.py`
	(`distance < 35` in `vision_test.py`).
- Right click threshold:
	`dist_right < 30` in `vision_controller.py`
	(`distance_R < 35` in `vision_test.py`).
- Scroll speed:
	`pyautogui.scroll(-int(delta_y*2))` multiplier in `vision_controller.py`.

## Troubleshooting

- Camera window does not open:
	Close apps that may already use the webcam (Zoom, Teams, browser tabs), then rerun.
- Mouse feels shaky:
	Increase `closeness` and improve lighting/background contrast.
- Too many accidental clicks:
	Reduce pinch sensitivity by lowering click thresholds or adding a slightly longer cooldown.
- Mouse moves out of control:
	Move the cursor to a screen corner to trigger PyAutoGUI failsafe and stop movement.

## Safety Notes

- Keep `pyautogui.FAILSAFE = True` enabled.
- Test in a low-risk environment before using it for daily workflow control.
- Good lighting and a plain background significantly improve detection quality.

## Future Improvements

- Drag-and-drop gesture
- Double-click gesture
- Handedness filter (left vs right hand)
- Gesture calibration mode
- FPS counter and performance tuning

## Acknowledgements

- [MediaPipe](https://github.com/google/mediapipe)
- [OpenCV](https://opencv.org/)
- [PyAutoGUI](https://pyautogui.readthedocs.io/)

