import cv2
import mediapipe as mp
import os
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from control.steering import SteeringController
from control.pedals import PedalController
from control.controllers import VirtualController
from visualization.dashboard import Dashboard

# ============================================================
# PATHS
# ============================================================

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "mediapipe"
    / "hand_landmarker.task"
)


# ============================================================
# MEDIAPIPE
# ============================================================

base_options = python.BaseOptions(
    model_asset_path=str(MODEL_PATH)
)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.7,
    min_tracking_confidence=0.7
)


detector = vision.HandLandmarker.create_from_options(
    options
)


# ============================================================
# STEERING CONTROLLER
# ============================================================

steering = SteeringController(
    max_angle=45.0,
    smoothing=0.25
)


# ============================================================
# PEDAL CONTROLLER
# ============================================================

pedals = PedalController(
    smoothing=0.25
)


# ============================================================
# VIRTUAL XBOX CONTROLLER
# ============================================================

controller = VirtualController()

dashboard = Dashboard()

# ============================================================
# CAMERA
# ============================================================

camera_index = int(os.getenv("CAMERA_INDEX", "0"))
camera_backends = (
    ("MSMF", cv2.CAP_MSMF),
    ("DSHOW", cv2.CAP_DSHOW),
    ("ANY", cv2.CAP_ANY),
)

cap = None
selected_backend = None

for backend_name, backend in camera_backends:
    candidate = cv2.VideoCapture(camera_index, backend)
    if candidate.isOpened():
        cap = candidate
        selected_backend = backend_name
        break
    candidate.release()


if cap is None:
    print(f"ERROR: Could not open camera index {camera_index}.")
    print("Check Windows camera permissions and confirm another app is not using the camera.")
    print("For another camera, run with CAMERA_INDEX=1 (or another index).")
    sys.exit(1)



print(f"Camera opened: index {camera_index}, backend {selected_backend}")


print("===================================")
print(" VR HAND STEERING - HAND TRACKING")
print("===================================")
print("Show your hands to the camera.")
print("Press Q to quit.")


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    success, frame = cap.read()

    if not success:
        print("ERROR: Could not read webcam.")
        break

    # Mirror camera
    frame = cv2.flip(frame, 1)

    height, width, _ = frame.shape

    # --------------------------------------------------------
    # Convert BGR -> RGB
    # --------------------------------------------------------

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    # --------------------------------------------------------
    # Create MediaPipe image
    # --------------------------------------------------------

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    # --------------------------------------------------------
    # Detect hands
    # --------------------------------------------------------

    result = detector.detect(mp_image)

    # --------------------------------------------------------
    # Reset hand positions every frame
    # --------------------------------------------------------

    left_hand = None
    right_hand = None

    left_landmarks = None
    right_landmarks = None

    # ========================================================
    # PROCESS DETECTED HANDS
    # ========================================================

    number_of_hands = len(result.hand_landmarks)


    for hand_index, hand_landmarks in enumerate(
        result.hand_landmarks
    ):

        # ----------------------------------------------------
        # LEFT / RIGHT
        # ----------------------------------------------------

        handedness = result.handedness[hand_index][0]

        hand_label = handedness.category_name

        # ----------------------------------------------------
        # Get wrist
        # Landmark 0 = wrist
        # ----------------------------------------------------

        wrist = hand_landmarks[0]

        # Save hand information
        # Save hand information
        # MediaPipe is reversed because the camera image is mirrored.
        if hand_label == "Left":
            right_hand = wrist
            right_landmarks = hand_landmarks

            display_hand_label = "RIGHT"

        elif hand_label == "Right":
            left_hand = wrist
            left_landmarks = hand_landmarks

            display_hand_label = "LEFT"

        else:
            display_hand_label = hand_label

        wrist_x = int(
            wrist.x * width
        )

        wrist_y = int(
            wrist.y * height
        )

        # ====================================================
        # DRAW 21 LANDMARKS
        # ====================================================

        for landmark_index, landmark in enumerate(
            hand_landmarks
        ):

            x = int(
                landmark.x * width
            )

            y = int(
                landmark.y * height
            )

            # Draw landmark
            cv2.circle(
                frame,
                (x, y),
                5,
                (0, 255, 0),
                -1
            )

            # Display landmark number
            cv2.putText(
                frame,
                str(landmark_index),
                (x + 5, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.35,
                (255, 255, 255),
                1
            )

        # ====================================================
        # DISPLAY LEFT / RIGHT
        # ====================================================

        cv2.putText(
            frame,
            display_hand_label,
            (wrist_x - 30, wrist_y - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

        # ====================================================
        # IMPORTANT FINGER COORDINATES
        # ====================================================

        index_tip = hand_landmarks[8]

        thumb_tip = hand_landmarks[4]

        print(
            f"{hand_label}: "
            f"Wrist=({wrist.x:.2f},{wrist.y:.2f}) "
            f"Index=({index_tip.x:.2f},{index_tip.y:.2f}) "
            f"Thumb=({thumb_tip.x:.2f},{thumb_tip.y:.2f})"
        )

    # ========================================================
    # STEERING
    # ========================================================

    steering_value = 0.0

    if left_hand is not None and right_hand is not None:

        steering_value = steering.update(
            left_hand,
            right_hand
        )

        steering_angle = steering_value * 45.0

       

    # ========================================================
    # PEDAL / GESTURE CONTROL
    # ========================================================

    acceleration, brake, boost = pedals.update(
        left_landmarks,
        right_landmarks
    )

    acceleration_percent = acceleration * 100

    # ========================================================
    # SEND TO VIRTUAL XBOX CONTROLLER
    # ========================================================

    controller.set_steering(steering_value)
    controller.set_acceleration(acceleration)
    controller.set_brake(brake)
    controller.set_boost(boost)
    controller.update()

    

    # ========================================================
    # DRAW DASHBOARD
    # ========================================================

    frame = dashboard.draw(
    frame,
    steering_value,
    acceleration,
    brake,
    boost,
    controller_active=True
    )

    # ========================================================
    # SHOW CAMERA
    # ========================================================

    cv2.imshow(
        "VR Hand Steering - Tracking",
        frame
    )

    # Q = quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()

cv2.destroyAllWindows()

controller.reset()

detector.close()