import cv2
import math


class Dashboard:

    def draw(
        self,
        frame,
        steering,
        acceleration,
        brake,
        boost,
        controller_active=True
    ):

        # ==============================================
        # SMALL DASHBOARD POSITION - LEFT SIDE
        # ==============================================

        x = 10
        y = 10

        panel_width = 190
        panel_height = 250

        # Background
        cv2.rectangle(
            frame,
            (x, y),
            (x + panel_width, y + panel_height),
            (35, 35, 35),
            -1
        )

        # Border
        cv2.rectangle(
            frame,
            (x, y),
            (x + panel_width, y + panel_height),
            (100, 100, 100),
            1
        )

        # ==============================================
        # TITLE
        # ==============================================

        cv2.putText(
            frame,
            "CONTROL",
            (x + 45, y + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )

        # ==============================================
        # SMALL STEERING WHEEL
        # ==============================================

        center_x = x + 95
        center_y = y + 75

        radius = 30

        cv2.circle(
            frame,
            (center_x, center_y),
            radius,
            (255, 255, 255),
            1
        )

        # Steering indicator
        angle = steering * 45
        radians = math.radians(angle)

        line_x = int(
            center_x + math.sin(radians) * radius
        )

        line_y = int(
            center_y - math.cos(radians) * radius
        )

        cv2.line(
            frame,
            (center_x, center_y),
            (line_x, line_y),
            (0, 255, 255),
            2
        )

        # ==============================================
        # STEERING
        # ==============================================

        cv2.putText(
            frame,
            f"STEER: {steering:+.2f}",
            (x + 25, y + 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (255, 255, 255),
            1
        )

        # ==============================================
        # ACCELERATION
        # ==============================================

        cv2.putText(
            frame,
            "ACC",
            (x + 10, y + 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (255, 255, 255),
            1
        )

        bar_x = x + 50
        bar_y = y + 138

        bar_width = 90
        bar_height = 12

        cv2.rectangle(
            frame,
            (bar_x, bar_y),
            (bar_x + bar_width, bar_y + bar_height),
            (255, 255, 255),
            1
        )

        fill_width = int(bar_width * acceleration)

        cv2.rectangle(
            frame,
            (bar_x, bar_y),
            (bar_x + fill_width, bar_y + bar_height),
            (0, 255, 0),
            -1
        )

        cv2.putText(
            frame,
            f"{acceleration * 100:.0f}%",
            (x + 145, y + 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (255, 255, 255),
            1
        )

        # ==============================================
        # BRAKE
        # ==============================================

        brake_color = (
            (0, 0, 255) if brake else (180, 180, 180)
        )

        cv2.putText(
            frame,
            f"BRAKE: {'ON' if brake else 'OFF'}",
            (x + 10, y + 180),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            brake_color,
            1
        )

        # ==============================================
        # BOOST
        # ==============================================

        boost_color = (
            (255, 0, 0) if boost else (180, 180, 180)
        )

        cv2.putText(
            frame,
            f"BOOST: {'ON' if boost else 'OFF'}",
            (x + 10, y + 205),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            boost_color,
            1
        )

        # ==============================================
        # CONTROLLER STATUS
        # ==============================================

        controller_color = (
            (0, 255, 0)
            if controller_active
            else (0, 0, 255)
        )

        cv2.putText(
            frame,
            "CONTROLLER ACTIVE",
            (x + 10, y + 235),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.38,
            controller_color,
            1
        )

        return frame