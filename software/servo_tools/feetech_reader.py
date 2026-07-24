#!/usr/bin/env python3
"""Reusable FeetechServoReader class for STS3215 arms.

Drop-in replacement for the Zhonglin ServoReader in uarm.py — same
get_action_offset() interface, Feetech scservo_sdk internals.
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scservo_sdk import (
    PortHandler, sms_sts, GroupSyncRead,
    SMS_STS_PRESENT_POSITION_L, COMM_SUCCESS,
)

SYNC_START = SMS_STS_PRESENT_POSITION_L  # reg 56
SYNC_LEN = 4                             # pos_L, pos_H, speed_L, speed_H


def _pos_to_degrees(pos, center=2047, span=4095):
    return (pos - center) / span * 360.0


class FeetechServoReader:
    """Reads 7 STS3215 servos and returns joint offsets in degrees.

    Args:
        port: Serial device path (e.g. '/dev/cu.usbmodemXXXX').
        baudrate: Bus baudrate — must match servo config (default 1 Mbit/s).
        servo_ids: Iterable of servo IDs to read (default 0–6).
        label: Human-readable name used in error messages (e.g. 'left').
    """

    def __init__(self, port: str, baudrate: int = 1_000_000,
                 servo_ids=range(0, 7), label: str = ""):
        self.label = label or port
        self.servo_ids = list(servo_ids)

        self._port = PortHandler(port)
        self._pkt = sms_sts(self._port)

        if not self._port.openPort():
            raise RuntimeError(f"[{self.label}] Failed to open {port}")
        if not self._port.setBaudRate(baudrate):
            raise RuntimeError(f"[{self.label}] Failed to set baudrate {baudrate}")

        time.sleep(0.2)

        self._sync = GroupSyncRead(self._pkt, SYNC_START, SYNC_LEN)
        for sid in self.servo_ids:
            self._sync.addParam(sid)

        self._zero = self._snapshot()
        print(f"[{self.label}] Zero positions (°): "
              f"{[round(d, 1) for d in self._zero]}")

    def _snapshot(self) -> list:
        """Read current positions as degrees (used to record zero pose)."""
        for attempt in range(5):
            result = self._sync.txRxPacket()
            if result == COMM_SUCCESS:
                break
            time.sleep(0.05)
        else:
            print(f"[{self.label}] Warning: zero calibration read failed; using 0°")
            self._sync.clearParam()
            for sid in self.servo_ids:
                self._sync.addParam(sid)
            return [0.0] * len(self.servo_ids)

        angles = []
        for sid in self.servo_ids:
            ok, _ = self._sync.isAvailable(sid, SYNC_START, 2)
            if ok:
                pos = self._sync.getData(sid, SYNC_START, 2)
                angles.append(_pos_to_degrees(pos))
            else:
                angles.append(0.0)
                print(f"[{self.label}] Warning: ID {sid} not available at zero capture")

        self._sync.clearParam()
        for sid in self.servo_ids:
            self._sync.addParam(sid)
        return angles

    def get_action_offset(self) -> list:
        """Return current joint positions as degree offsets from zero.

        Returns a list of 7 floats. Returns the last good reading on
        a comm failure rather than raising so the control loop stays alive.
        """
        result = self._sync.txRxPacket()
        if result != COMM_SUCCESS:
            print(f"[{self.label}] SyncRead failed: {self._pkt.getTxRxResult(result)}")
            self._sync.clearParam()
            for sid in self.servo_ids:
                self._sync.addParam(sid)
            return [0.0] * len(self.servo_ids)

        offsets = []
        for i, sid in enumerate(self.servo_ids):
            ok, _ = self._sync.isAvailable(sid, SYNC_START, 2)
            if ok:
                pos = self._sync.getData(sid, SYNC_START, 2)
                offsets.append(_pos_to_degrees(pos) - self._zero[i])
            else:
                offsets.append(0.0)

        self._sync.clearParam()
        for sid in self.servo_ids:
            self._sync.addParam(sid)
        return offsets

    def close(self):
        self._port.closePort()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
