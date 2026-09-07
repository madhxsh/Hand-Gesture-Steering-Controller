import vgamepad as vg


class VirtualController:
    """
    Controls a virtual Xbox 360-style controller.

    Mapping:
        Steering     -> Left Stick X
        Acceleration -> Right Trigger (RT)
        Brake        -> Left Trigger (LT)
        Boost        -> A button
    """

    def __init__(self):
        print("Creating virtual Xbox-style controller...")

        self.gamepad = vg.VX360Gamepad()

        print("Virtual controller created!")

    def set_steering(self, value):
        """
        Steering value:
            -1.0 = full left
             0.0 = center
            +1.0 = full right
        """

        value = max(-1.0, min(1.0, value))

        self.gamepad.left_joystick_float(
            x_value_float=value,
            y_value_float=0.0
        )

    def set_acceleration(self, value):
        """
        Acceleration:
            0.0 = 0%
            1.0 = 100%

        Sent to RT trigger.
        """

        value = max(0.0, min(1.0, value))

        self.gamepad.right_trigger_float(
            value_float=value
        )

    def set_brake(self, pressed):
        """
        Brake:
            True  = pressed
            False = released

        Sent to LT trigger.
        """

        if pressed:
            self.gamepad.left_trigger_float(
                value_float=1.0
            )
        else:
            self.gamepad.left_trigger_float(
                value_float=0.0
            )

    def set_boost(self, pressed):
        """
        Boost:
            True  = A button pressed
            False = A button released
        """

        if pressed:
            self.gamepad.press_button(
                button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A
            )
        else:
            self.gamepad.release_button(
                button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A
            )

    def update(self):
        """
        Send the current controller state to Windows.
        """

        self.gamepad.update()

    def reset(self):
        """
        Return the controller to a neutral state.
        """

        self.gamepad.reset()

        self.gamepad.update()

    def disconnect(self):
        """
        Disconnect the virtual controller.
        """

        self.gamepad.reset()
        self.gamepad.update()

        print("Virtual controller reset.")