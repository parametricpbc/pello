#!/usr/bin/env python3
"""Read Feetech STS3215 servo positions from two arms side-by-side.

Each arm runs its own GroupSyncRead loop in a background thread.
The main thread merges and prints both columns at ~20 Hz.
"""

import os
import sys
import time
import threading
import queue

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scservo_sdk import (
    PortHandler, sms_sts, GroupSyncRead,
    SMS_STS_PRESENT_POSITION_L, COMM_SUCCESS,
)

SERIAL_PORTS = [
    '/dev/cu.usbmodemXXXX',  # left
    '/dev/cu.usbmodemYYYY',  # right
]
BAUDRATE = 1_000_000
SERVO_IDS = list(range(0, 7))
SCAN_IDS = list(range(0, 16))

SYNC_START = SMS_STS_PRESENT_POSITION_L
SYNC_LEN = 4


def pos_to_degrees(pos, center=2047, span=4095):
    return (pos - center) / span * 360.0


def discover_servos(pkt, ids, retries=3):
    """Ping each servo ID up to `retries` times; return (id, model) for responders."""
    found = []
    for sid in ids:
        for _ in range(retries):
            try:
                model, result, _ = pkt.ping(sid)
                if result == COMM_SUCCESS:
                    found.append((sid, model))
                    break
            except (TypeError, IndexError):
                pass
    return found


def arm_thread(serial_port: str, label: str, out: queue.Queue, stop: threading.Event):
    port = PortHandler(serial_port)
    pkt = sms_sts(port)

    if not port.openPort() or not port.setBaudRate(BAUDRATE):
        out.put((label, None, f"OPEN FAILED: {serial_port}"))
        return

    time.sleep(0.5)

    # Retry discovery passes until all expected IDs respond or max_passes exhausted.
    MAX_PASSES = 5
    found = []
    for pass_num in range(MAX_PASSES):
        already = {sid for sid, _ in found}
        remaining_expected = [sid for sid in SERVO_IDS if sid not in already]
        scan_ids = remaining_expected if already else SCAN_IDS
        new_found = discover_servos(pkt, scan_ids)
        for entry in new_found:
            if entry[0] not in already:
                found.append(entry)
        if all(sid in {sid for sid, _ in found} for sid in SERVO_IDS):
            break
        if pass_num < MAX_PASSES - 1:
            time.sleep(0.1)

    if not found:
        out.put((label, None, "NO SERVOS FOUND"))
        port.closePort()
        return

    active = [sid for sid, _ in found if sid in SERVO_IDS]
    sync = GroupSyncRead(pkt, SYNC_START, SYNC_LEN)
    for sid in active:
        sync.addParam(sid)

    while not stop.is_set():
        result = sync.txRxPacket()
        if result != COMM_SUCCESS:
            sync.clearParam()
            for sid in active:
                sync.addParam(sid)
            continue

        row = {}
        for sid in SERVO_IDS:
            if sid not in active:
                row[sid] = None
                continue
            ok, _ = sync.isAvailable(sid, SYNC_START, 2)
            row[sid] = sync.getData(sid, SYNC_START, 2) if ok else None

        out.put((label, row, None))
        sync.clearParam()
        for sid in active:
            sync.addParam(sid)

    port.closePort()


def format_row(row, label):
    if row is None:
        return f"{label}: ---"
    parts = []
    for sid in SERVO_IDS:
        pos = row.get(sid)
        if pos is None:
            parts.append(f"ID{sid}:  ---")
        else:
            parts.append(f"ID{sid}:{pos:5d}({pos_to_degrees(pos):+6.1f}°)")
    return f"{label}  " + "  ".join(parts)


def main():
    labels = ["LEFT ", "RIGHT"]
    results = {"LEFT ": None, "RIGHT": None}
    errors = {}

    out = queue.Queue(maxsize=20)
    stop = threading.Event()

    threads = []
    for serial_port, label in zip(SERIAL_PORTS, labels):
        t = threading.Thread(target=arm_thread, args=(serial_port, label, out, stop),
                             daemon=True)
        t.start()
        threads.append(t)

    print(f"Opened {SERIAL_PORTS[0]} (left) and {SERIAL_PORTS[1]} (right)")
    print("Move the arms — Ctrl+C to stop.\n")

    try:
        while True:
            # drain queue, keep latest per label
            try:
                while True:
                    label, row, err = out.get_nowait()
                    if err:
                        errors[label] = err
                    else:
                        results[label] = row
            except queue.Empty:
                pass

            for label in labels:
                if label in errors:
                    print(f"{label}: {errors[label]}")
                else:
                    print(format_row(results[label], label))
            print()
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        stop.set()


if __name__ == "__main__":
    main()
