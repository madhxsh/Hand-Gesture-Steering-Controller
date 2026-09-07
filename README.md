# Hand Gesture Steering Controller

A computer vision-based project that allows users to control a virtual Xbox 360 controller using real-time hand gestures captured through a webcam.

## Overview

The Hand Gesture Steering Controller uses hand movements and gestures as an alternative to a traditional gaming controller. The webcam captures hand movements, MediaPipe detects hand landmarks, and Python processes the gestures into controller inputs.

The processed values are sent to a virtual Xbox 360 controller using the `vgamepad` library, allowing compatible racing games to receive smooth controller inputs.

## Features

-  Real-time hand detection and tracking
-  Two-hand analog steering
-  Finger gesture-based acceleration
-  Right thumb gesture for braking
-  Left thumb gesture for boost
-  Virtual Xbox 360 controller integration
-  Real-time control dashboard
-  Gesture smoothing and stability detection

## Controller Mapping

| Hand Control | Virtual Xbox Control |
|---|---|
| Steering | Left Stick X |
| Acceleration | Right Trigger (RT) |
| Brake | Left Trigger (LT) |
| Boost | A Button |

## How It Works

```text
Webcam
  ↓
OpenCV
  ↓
MediaPipe Hand Detection
  ↓
Hand Landmarks
  ↓
Gesture Processing
  ↓
Steering & Pedal Controllers
  ↓
vgamepad
  ↓
Virtual Xbox Controller
  ↓
Racing Game




HandGestureSteeringController/
│
|--detection/
|   |--hand_landmarker.py
│
├── control/
│   ├── steering.py
│   ├── pedals.py
│   └── controller.py
|
|-- models/
|   |--mediapipe/
|      |-- hand_landmarker.task
│   
├── visualization/
│   └── dashboard.py
│
├── requirements.txt
└── README.md

# Future Improvements
Convert the project into a desktop application
Improve hand detection accuracy
Add customizable gesture controls
Add user settings
Improve the control dashboard
Add game-specific controller profiles


Author
MADHESH G
