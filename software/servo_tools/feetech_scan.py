#!/usr/bin/env python3
"""Scan the bus and print the ID of every connected servo."""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scservo_sdk import *

SERIAL_PORT = '/dev/cu.usbmodemYYYY'  # macOS; use /dev/ttyUSB0 on Linux
BAUDRATE = 1000000
SCAN_IDS = range(0, 20)

port = PortHandler(SERIAL_PORT)
pkt = sms_sts(port)

if not port.openPort():
    print(f"Failed to open {SERIAL_PORT}")
    sys.exit(1)
port.setBaudRate(BAUDRATE)

print(f"Scanning IDs {SCAN_IDS.start}–{SCAN_IDS.stop - 1}...")
found = []
for sid in SCAN_IDS:
    try:
        model, result, error = pkt.ping(sid)
        if result == COMM_SUCCESS:
            found.append((sid, model))
    except (TypeError, IndexError):
        continue

port.closePort()

if found:
    for sid, model in found:
        print(f"  ID {sid}  (model {model})")
else:
    print("No servos found. Check power and wiring.")
