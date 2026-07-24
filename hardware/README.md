# Hardware

Everything needed to build a set of Pello leader arms: bill of materials, the 3D-print
file, and assembly instructions. A set is **2 arms**, each with **7× Feetech STS3215**
servos (14 total) arranged as linkages **L1–L5** plus a **handle**, **trigger**, and
**base**.

## Bill of materials

See [`BOM.md`](BOM.md) — real parts, quantities, and prices (~$389 for a bimanual set).
The dominant cost is the 14 servos, ordered as two 6-packs plus one 2-pack.

## 3D printing

Print [`gello3dp.3mf`](gello3dp.3mf) — one arm's parts per plate (two plates for a
bimanual set). Printed in **PETG**. This covers all structural parts: base, L1–L5 linkages,
handle, trigger, and hardstops.

## Assembly

> The full illustrated step-by-step — with photos for every group — is in
> **[`ASSEMBLY.md`](ASSEMBLY.md)**. The outline below is a summary and follows
> that SOP's numbering. Recommend an electric screwdriver; two screw sizes are referred to
> as **BIG** and **SMALL**.

- **Step 0 — Prep the servos (×7 per arm).** Open each servo, remove the two internal
  reduction gears (this decouples the motor from the drive shaft so the joint is freely back-drivable), reassemble, and mount both servo horns (toothed + non-toothed).
- **Step 1 — Build the four sub-assemblies:** Group 1 (L1–L3), Group 2 (L4–L5), Group 3
  (handle + trigger), Group 4 (base + driver board).
- **Step 2 — Join the groups** into a full arm, then press-fit the assembly into the base (do this after
  wiring for easier cable routing).
- **Step 3 — Wire** the servos as a daisy chain terminating at the driver board, then connect
  the board to the host over USB-C.
- **Step 4 — Verify** in software: power the board, assign servo IDs, and confirm
  the bus (see bring-up below).

## Electronics & bring-up

- **Power:** ~7.4V @ 5A external DC to the servo driver board.
- **Host:** USB-C from the board to your computer.
- **Assign servo IDs first** — fresh servos all ship with the same default ID. Assign each
  an ID from **0 (base) to 6 (gripper/trigger)** with
  [`../Uarm_teleop/Feetech_servo/feetech_servo_changeid.py`](../Uarm_teleop/Feetech_servo/feetech_servo_changeid.py),
  isolating one servo on the bus at a time (the write broadcasts to every powered servo).
- **Verify the bus** — once all 7 are set and the chain is wired, run
  [`feetech_gui.py`](../Uarm_teleop/Feetech_servo/feetech_gui.py) or
  [`feetech_scan.py`](../Uarm_teleop/Feetech_servo/feetech_scan.py) and confirm IDs 0–6 all
  respond with none on the factory default.

Full software setup is in the [top-level README](../README.md).
