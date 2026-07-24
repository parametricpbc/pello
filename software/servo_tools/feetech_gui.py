#!/usr/bin/env python3
"""Real-time servo position WebSocket server for dual U-Arm GUI visualizer.

Run:  python3 feetech_gui.py
      (browser opens automatically to feetech_gui.html)
"""

import asyncio
import json
import os
import pathlib
import sys
import threading
import time
import webbrowser
import websockets

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scservo_sdk import *

# ── Config ────────────────────────────────────────────────────────────────────
SERIAL_PORTS = {
    'left':  '/dev/cu.usbmodemXXXX',
    'right': '/dev/cu.usbmodemYYYY',
}
BAUDRATE    = 1_000_000
SERVO_IDS   = list(range(0, 7))
SCAN_IDS    = list(range(0, 16))
WS_HOST     = 'localhost'
WS_PORT     = 8765

# GroupSyncRead: pos(2) + speed(2) + load(2) starting at reg 56
SYNC_START = SMS_STS_PRESENT_POSITION_L  # 56
SYNC_LEN   = 6

READ_HZ  = 50
BCAST_HZ = 30

# ── Shared state ──────────────────────────────────────────────────────────────
_lock = threading.Lock()
_state: dict = {
    'left':  {'status': 'starting', 'servos': {}},
    'right': {'status': 'starting', 'servos': {}},
}


def _pos_to_deg(pos, center=2047, span=4095):
    return (pos - center) / span * 360.0


def _discover(pkt, ids):
    found = []
    for sid in ids:
        try:
            model, result, _ = pkt.ping(sid)
            if result == COMM_SUCCESS:
                found.append(sid)
        except (TypeError, IndexError):
            continue
    return found


def _set_status(arm, s):
    with _lock:
        _state[arm]['status'] = s


# ── Servo reader thread (retries indefinitely) ─────────────────────────────
def _reader_thread(arm: str, serial_port: str):
    """
    Outer loop: open port → discover servos → sync-read loop.
    If any step fails, waits 5 s and retries from the top.
    """
    period = 1.0 / READ_HZ

    while True:
        port = PortHandler(serial_port)
        pkt  = sms_sts(port)

        if not port.openPort():
            _set_status(arm, f'error: cannot open port')
            print(f"[{arm}] Cannot open {serial_port} — retrying in 5 s")
            time.sleep(5)
            continue

        if not port.setBaudRate(BAUDRATE):
            _set_status(arm, 'error: baudrate failed')
            port.closePort()
            time.sleep(5)
            continue

        print(f"[{arm}] Port open: {serial_port} @ {BAUDRATE}")
        time.sleep(0.2)

        _set_status(arm, 'scanning…')
        active = _discover(pkt, SERVO_IDS)
        if not active:
            print(f"[{arm}] IDs 0-6 not found — scanning 0-15…")
            active = _discover(pkt, SCAN_IDS)

        if not active:
            _set_status(arm, 'scanning…')
            print(f"[{arm}] No servos found — retrying in 5 s")
            print(f"        Is the PSU (7.4-8 V) connected to the {arm} arm?")
            port.closePort()
            time.sleep(5)
            continue

        print(f"[{arm}] Found: {active}")
        missing = [i for i in SERVO_IDS if i not in active]
        if missing:
            print(f"[{arm}] Missing IDs: {missing}")

        sync = GroupSyncRead(pkt, SYNC_START, SYNC_LEN)
        for sid in active:
            sync.addParam(sid)

        _set_status(arm, 'ok')

        try:
            while True:
                t0 = time.monotonic()
                result = sync.txRxPacket()

                servos = {}
                if result != COMM_SUCCESS:
                    for sid in active:
                        servos[str(sid)] = {'pos': 0, 'deg': 0.0, 'speed': 0,
                                            'load': 0, 'ok': False}
                    sync.clearParam()
                    for sid in active:
                        sync.addParam(sid)
                else:
                    for sid in SERVO_IDS:
                        if sid not in active:
                            continue
                        ok_pos, _ = sync.isAvailable(sid, SYNC_START, 2)
                        ok_spd, _ = sync.isAvailable(sid, SYNC_START + 2, 2)
                        ok_ld,  _ = sync.isAvailable(sid, SYNC_START + 4, 2)
                        if ok_pos:
                            pos   = sync.getData(sid, SYNC_START, 2)
                            speed = sync.getData(sid, SYNC_START + 2, 2) if ok_spd else 0
                            load  = sync.getData(sid, SYNC_START + 4, 2) if ok_ld  else 0
                            servos[str(sid)] = {
                                'pos':   pos,
                                'deg':   round(_pos_to_deg(pos), 2),
                                'speed': speed,
                                'load':  load,
                                'ok':    True,
                            }
                        else:
                            servos[str(sid)] = {'pos': 0, 'deg': 0.0, 'speed': 0,
                                                'load': 0, 'ok': False}
                    sync.clearParam()
                    for sid in active:
                        sync.addParam(sid)

                with _lock:
                    _state[arm]['servos'] = servos

                elapsed = time.monotonic() - t0
                sleept  = period - elapsed
                if sleept > 0:
                    time.sleep(sleept)

        except Exception as e:
            print(f"[{arm}] Read loop error: {e} — restarting")
            _set_status(arm, 'scanning…')
        finally:
            try:
                port.closePort()
            except Exception:
                pass

        time.sleep(2)


# ── WebSocket server ──────────────────────────────────────────────────────────
async def _ws_handler(websocket):
    try:
        while True:
            with _lock:
                payload = json.dumps(_state)
            await websocket.send(payload)
            await asyncio.sleep(1.0 / BCAST_HZ)
    except Exception:
        pass


async def _serve():
    async with websockets.serve(_ws_handler, WS_HOST, WS_PORT):
        html_path = pathlib.Path(__file__).with_name('feetech_gui.html').as_uri()
        print(f"[ws]    Serving on ws://{WS_HOST}:{WS_PORT}")
        print(f"[ws]    Opening {html_path}\n")
        webbrowser.open(html_path)
        await asyncio.Future()  # run until cancelled


def main():
    for arm, port in SERIAL_PORTS.items():
        t = threading.Thread(target=_reader_thread, args=(arm, port), daemon=True)
        t.start()
    try:
        asyncio.run(_serve())
    except KeyboardInterrupt:
        print("\n[ws] Stopped.")


if __name__ == '__main__':
    main()
