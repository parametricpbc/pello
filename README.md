# Pello — Parametric's open-source GELLO leader arms

Open-source bimanual [GELLO](https://wuphilipp.github.io/gello_site/) teleoperation leader
arms, purpose-built to drive **[i2rt YAM](https://github.com/i2rt-robotics) follower arms**.
Each leader is a **5/8-scale replica of the 6-DOF YAM** (plus a gripper trigger), sensed by
**7× Feetech STS3215 serial-bus servos per arm**. You move the lightweight leaders by hand
and the YAM followers mirror your motion in real time via
[LeRobot](https://github.com/huggingface/lerobot).

> **Designed for the 6-DOF YAM**, not the 5-DOF SO-100. The software happens to drive the
> YAM through LeRobot's SO-100 follower interface, but the arm geometry and joint count are
> the YAM's.

<!-- TODO(preliminary): add a hero photo / short GIF of the arms in use -->

## What's in this repo

| Path | Contents |
|------|----------|
| [`hardware/`](hardware/) | Bill of materials, 3D-print file, and assembly instructions |
| [`Uarm_teleop/Feetech_servo/`](Uarm_teleop/Feetech_servo/) | Servo GUI, bus scanner, and ID-assignment tools |
| [`Follower_Arm/LeRobot/`](Follower_Arm/LeRobot/) | Drive an i2rt YAM follower from the leaders via LeRobot |

## Build a set

1. **Order the parts** — [`hardware/BOM.md`](hardware/BOM.md) (~$389 for a bimanual set, 14 servos).
2. **Print the frame** — [`hardware/RIGHT+LEFT_GELLO.3mf`](hardware/RIGHT+LEFT_GELLO.3mf) (one arm on each plate).
3. **Assemble** — follow [`hardware/README.md`](hardware/README.md).
4. **Bring up the software** — below.

## Quick start (software)

**1. Install dependencies**

```bash
pip install -r requirements.txt
```

**2. Set your serial ports.** Each USB adapter enumerates differently per machine:

```bash
ls /dev/cu.usbmodem*   # macOS
ls /dev/ttyUSB*        # Linux
```

Update the port strings in `Uarm_teleop/Feetech_servo/feetech_gui.py` (top of file) and
`Follower_Arm/LeRobot/so100/dual_uarm_yam_teleop.py`.

**3. Assign servo IDs** (fresh servos all ship with the same default ID). With **one servo
connected to the bus at a time**, assign each an ID from **0 (base) to 6 (gripper/trigger)**:

```bash
cd Uarm_teleop/Feetech_servo
python3 feetech_servo_changeid.py 0   # then 1, 2, … 6, one servo at a time
```

The write broadcasts to every powered servo on the bus, so isolate each servo before
setting its ID. Once all 7 are set, wire the full daisy chain.

**4. Launch the servo GUI** (live 3D monitor — start here to verify a new build):

```bash
python3 feetech_gui.py
```

It opens `feetech_gui.html` in your browser, auto-discovers the servos, auto-zeros on the
first frame, and renders both arms in 3D. Press **H** to re-zero to the current pose. You
can also confirm the bus with `python3 feetech_scan.py`.

**5. Drive the YAM followers** (bimanual — each arm driven through LeRobot's SO-100 follower
interface):

```bash
cd ../../Follower_Arm/LeRobot/so100
python3 dual_uarm_yam_teleop.py
```

See [`Follower_Arm/LeRobot/README.md`](Follower_Arm/LeRobot/README.md) for the LeRobot setup.

## Hardware notes

- **Passive by design:** the two internal reduction gears are removed from each servo during
  assembly, so the joints are freely back-drivable. The servos sense position; they don't
  drive the arm (there is no active gravity compensation).
- **Servo IDs:** 0–6 per arm, stored in each servo's EEPROM. Re-assign with
  `Uarm_teleop/Feetech_servo/feetech_servo_changeid.py`.
- **Zero calibration:** captured live at startup — put the arms in their home pose before
  starting, or press **H** in the GUI to re-zero.

## Credits & license

Licensed under the **Apache License 2.0** — see [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).
This project is derived from
[MINT-SJTU/LeRobot-Anything-U-Arm](https://github.com/MINT-SJTU/LeRobot-Anything-U-Arm)
(please cite [arXiv:2509.02437](https://arxiv.org/abs/2509.02437)) and builds on the
[GELLO](https://github.com/wuphilipp/gello_mechanical) leader-arm concept (Wu et al.).
