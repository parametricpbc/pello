#!/usr/bin/env python3
"""Bimanual teleoperation: two GELLO uarm leaders → two i2rt YAM followers.

Leader ports (Feetech STS3215 GELLO):
  Left:  /dev/cu.usbmodemXXXX
  Right: /dev/cu.usbmodemYYYY

Follower ports (YAM arms configured as SO-100):
  Set FOLLOWER_PORT_LEFT and FOLLOWER_PORT_RIGHT below.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__),
    "../../../../Uarm_teleop/Feetech_servo"))

from feetech_reader import FeetechServoReader

from lerobot.teleoperators.keyboard.teleop_keyboard import KeyboardTeleop, KeyboardTeleopConfig
from lerobot.robots.so100_follower import SO100Follower, SO100FollowerConfig
from lerobot.utils.robot_utils import busy_wait
from lerobot.utils.visualization_utils import init_rerun, log_rerun_data

# --- Configure follower serial ports here ---
FOLLOWER_PORT_LEFT  = "/dev/ttyACM0"   # YAM left  — update as needed
FOLLOWER_PORT_RIGHT = "/dev/ttyACM1"   # YAM right — update as needed

FPS = 30


def make_arm_action(offset, prefix):
    """Map 7 GELLO servo offsets to SO-100 / YAM joint names."""
    return {
        f"{prefix}shoulder_pan.pos":  -offset[0] * 1.5,
        f"{prefix}shoulder_lift.pos":  offset[1] * 1.5,
        f"{prefix}elbow_flex.pos":     offset[2] * 1.5,
        f"{prefix}wrist_flex.pos":    -offset[4] * 1.5,
        f"{prefix}wrist_roll.pos":    -offset[5] * 1.5 - offset[3] * 1.5,
        f"{prefix}gripper.pos":        offset[6] * 1.5,
    }


def main():
    reader_left  = FeetechServoReader(port='/dev/cu.usbmodemXXXX', label='left')
    reader_right = FeetechServoReader(port='/dev/cu.usbmodemYYYY', label='right')

    robot_left  = SO100Follower(SO100FollowerConfig(port=FOLLOWER_PORT_LEFT,  id="yam_left"))
    robot_right = SO100Follower(SO100FollowerConfig(port=FOLLOWER_PORT_RIGHT, id="yam_right"))
    keyboard    = KeyboardTeleop(KeyboardTeleopConfig(id="keyboard"))

    robot_left.connect()
    robot_right.connect()
    keyboard.connect()

    init_rerun(session_name="dual_uarm_yam_teleop")

    print("Dual-arm teleop running — press Q to quit.")
    try:
        while True:
            t0 = time.perf_counter()

            obs_left  = robot_left.get_observation()
            obs_right = robot_right.get_observation()

            action_left  = make_arm_action(reader_left.get_action_offset(),  prefix="")
            action_right = make_arm_action(reader_right.get_action_offset(), prefix="")

            keys = keyboard.get_action()
            if "q" in keys:
                print("Quitting.")
                break

            robot_left.send_action(action_left)
            robot_right.send_action(action_right)

            log_rerun_data(observation={**obs_left,  **obs_right},
                           action={**action_left, **action_right})

            busy_wait(max(1.0 / FPS - (time.perf_counter() - t0), 0.0))

    finally:
        robot_left.disconnect()
        robot_right.disconnect()
        keyboard.disconnect()
        reader_left.close()
        reader_right.close()


if __name__ == "__main__":
    main()
