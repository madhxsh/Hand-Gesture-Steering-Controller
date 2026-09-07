import math


class PedalController:
    """
    Detects:
    - Acceleration using the 4 fingers
    - Brake using the physical right thumb
    - Boost using the physical left thumb
    """

    def __init__(self, smoothing=0.25, gesture_frames=3):
        self.smoothing = smoothing
        self.gesture_frames = gesture_frames

        self.acceleration = 0.0

        self.brake = False
        self.boost = False

        self.brake_counter = 0
        self.boost_counter = 0

    # --------------------------------------------------
    # Distance between two landmarks
    # --------------------------------------------------
    def distance(self, p1, p2):

        dx = p1.x - p2.x
        dy = p1.y - p2.y
        dz = p1.z - p2.z

        return math.sqrt(
            dx * dx +
            dy * dy +
            dz * dz
        )

    # --------------------------------------------------
    # Calculate angle between 3 points
    # --------------------------------------------------
    def angle(self, p1, p2, p3):
        """
        Calculate angle at p2.

        p1 ---- p2 ---- p3
        """

        v1 = (
            p1.x - p2.x,
            p1.y - p2.y,
            p1.z - p2.z
        )

        v2 = (
            p3.x - p2.x,
            p3.y - p2.y,
            p3.z - p2.z
        )

        dot = (
            v1[0] * v2[0] +
            v1[1] * v2[1] +
            v1[2] * v2[2]
        )

        mag1 = math.sqrt(
            v1[0] ** 2 +
            v1[1] ** 2 +
            v1[2] ** 2
        )

        mag2 = math.sqrt(
            v2[0] ** 2 +
            v2[1] ** 2 +
            v2[2] ** 2
        )

        if mag1 == 0 or mag2 == 0:
            return 180

        cosine = dot / (mag1 * mag2)

        cosine = max(
            -1.0,
            min(1.0, cosine)
        )

        return math.degrees(
            math.acos(cosine)
        )

    # --------------------------------------------------
    # Check whether a finger is closed
    # --------------------------------------------------
    def finger_closed(self, landmarks, tip, pip, mcp):

        tip_to_mcp = self.distance(
            landmarks[tip],
            landmarks[mcp]
        )

        pip_to_mcp = self.distance(
            landmarks[pip],
            landmarks[mcp]
        )

        return tip_to_mcp < pip_to_mcp * 1.25

    # --------------------------------------------------
    # Calculate acceleration
    # --------------------------------------------------
    def calculate_acceleration(self, landmarks):

        fingers = [
            (8, 6, 5),
            (12, 10, 9),
            (16, 14, 13),
            (20, 18, 17)
        ]

        closed_count = 0

        for tip, pip, mcp in fingers:

            if self.finger_closed(
                landmarks,
                tip,
                pip,
                mcp
            ):
                closed_count += 1

        target = closed_count / 4.0

        self.acceleration += (
            target - self.acceleration
        ) * self.smoothing

        return self.acceleration

    # --------------------------------------------------
    # Detect thumb closing
    # --------------------------------------------------
    def thumb_closed(self, landmarks):
        """
        Detect folded thumb using thumb bend angle.

        2 = Thumb MCP
        3 = Thumb IP
        4 = Thumb TIP
        """

        thumb_mcp = landmarks[2]
        thumb_ip = landmarks[3]
        thumb_tip = landmarks[4]

        # Angle at thumb IP joint
        thumb_angle = self.angle(
            thumb_mcp,
            thumb_ip,
            thumb_tip
        )

        # Distance from thumb tip to thumb MCP
        tip_to_mcp = self.distance(
            thumb_tip,
            thumb_mcp
        )

        # Distance from IP to MCP
        ip_to_mcp = self.distance(
            thumb_ip,
            thumb_mcp
        )

        # Debug information
        print(
            f"THUMB | "
            f"Angle={thumb_angle:.1f} | "
            f"Tip-MCP={tip_to_mcp:.3f}"
        )

        # ----------------------------------------------
        # THUMB CLOSED
        # ----------------------------------------------
        #
        # Straight thumb angle is approximately 160-180
        # Folded thumb angle becomes smaller.
        #
        # We use either angle OR distance.
        #

        angle_closed = thumb_angle < 140

        distance_closed = (
            tip_to_mcp <
            ip_to_mcp * 1.15
        )

        return (
            angle_closed or
            distance_closed
        )

    # --------------------------------------------------
    # Stable gesture detection
    # --------------------------------------------------
    def stable_gesture(
        self,
        detected,
        counter,
        current_state
    ):

        if detected:

            counter += 1

            if counter >= self.gesture_frames:

                current_state = True

                counter = self.gesture_frames

        else:

            counter -= 1

            if counter <= 0:

                current_state = False

                counter = 0

        return counter, current_state

    # --------------------------------------------------
    # Update all pedal controls
    # --------------------------------------------------
    def update(
        self,
        left_hand,
        right_hand
    ):

        # ----------------------------------------------
        # ACCELERATION
        # ----------------------------------------------

        if left_hand is not None:

            self.calculate_acceleration(
                left_hand
            )

        elif right_hand is not None:

            self.calculate_acceleration(
                right_hand
            )

        else:

            self.acceleration = 0.0

        # ----------------------------------------------
        # RIGHT THUMB = BRAKE
        # ----------------------------------------------

        if right_hand is not None:

            brake_detected = self.thumb_closed(
                right_hand
            )

        else:

            brake_detected = False

        (
            self.brake_counter,
            self.brake
        ) = self.stable_gesture(
            brake_detected,
            self.brake_counter,
            self.brake
        )

        # ----------------------------------------------
        # LEFT THUMB = BOOST
        # ----------------------------------------------

        if left_hand is not None:

            boost_detected = self.thumb_closed(
                left_hand
            )

        else:

            boost_detected = False

        (
            self.boost_counter,
            self.boost
        ) = self.stable_gesture(
            boost_detected,
            self.boost_counter,
            self.boost
        )

        return (
            self.acceleration,
            self.brake,
            self.boost
        )

    # --------------------------------------------------
    # Reset
    # --------------------------------------------------
    def reset(self):

        self.acceleration = 0.0

        self.brake = False
        self.boost = False

        self.brake_counter = 0
        self.boost_counter = 0