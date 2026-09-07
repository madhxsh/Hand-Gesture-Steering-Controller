import math


class SteeringController:
    """
    Converts the angle between the two hands
    into a steering value from -1.0 to +1.0.
    """

    def __init__(self, max_angle=45.0, smoothing=0.25):
        self.max_angle = max_angle
        self.smoothing = smoothing

        self.center_angle = None
        self.current_value = 0.0

    def calculate_angle(self, left_hand, right_hand):
        """
        Calculate the angle of the line connecting
        the left hand and right hand.

        Coordinates are normalized:
        x = 0 to 1
        y = 0 to 1
        """

        dx = right_hand.x - left_hand.x
        dy = right_hand.y - left_hand.y

        angle = math.degrees(math.atan2(dy, dx))

        return angle

    def calibrate(self, left_hand, right_hand):
        """
        Save the current hand position as the
        straight/center steering position.
        """

        self.center_angle = self.calculate_angle(
            left_hand,
            right_hand
        )

        self.current_value = 0.0

        print(
            f"Steering calibrated at "
            f"{self.center_angle:.2f} degrees"
        )

    def update(self, left_hand, right_hand):
        """
        Calculate steering value.

        Returns:
            -1.0 = full left
             0.0 = center
            +1.0 = full right
        """

        if self.center_angle is None:
            self.calibrate(left_hand, right_hand)

        angle = self.calculate_angle(
            left_hand,
            right_hand
        )

        # Difference from center
        difference = angle - self.center_angle

        # Keep angle inside -180 to +180
        if difference > 180:
            difference -= 360

        if difference < -180:
            difference += 360

        # Convert angle to -1 ... +1
        target = difference / self.max_angle

        # Limit range
        target = max(-1.0, min(1.0, target))

        # Smooth steering
        self.current_value += (
            target - self.current_value
        ) * self.smoothing

        return self.current_value

    def reset(self):
        """
        Reset calibration.
        """

        self.center_angle = None
        self.current_value = 0.0