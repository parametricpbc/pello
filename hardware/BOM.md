# GELLO — Bill of Materials

Everything needed to build **one set of leaders (2 arms)**: a 5/8-scale i2rt YAM
replica with **7× Feetech STS3215 servos per arm (14 total)** and a GELLO-style
gripper handle.

Prices are in USD (parts as of July 2026). The 14 servos are ordered as **two 6-packs
plus one 2-pack** — cheaper and more reliable than buying singles.

## Purchased parts

| # | Component | Qty | Price |
|---|-----------|----:|------:|
| 1 | [Feetech STS3215 servo — 6-pack](https://www.amazon.com/dp/B0FQHCV9GP) | 2 packs (12 servos) | $269.98 |
| 2 | [Feetech STS3215 servo — 2-pack](https://www.amazon.com/STS3215-Serial-Magnetic-Programmable-Robotic/dp/B0FVS63YNN) | 1 pack (2 servos) | $45.98 |
| 3 | [Serial bus servo driver board — Waveshare, 2-pack](https://www.amazon.com/dp/B0DK79JNNK) | 1 pack (2 boards) | $19.99 |
| 4 | [Power supply — SHNITPWR 60W universal adjustable](https://www.amazon.com/SHNITPWR-Universal-Adjustable-100V-240V-Converter/dp/B08BL55LMB) | 2 power supplies | $37.98 |
| | **Total (one leader set / 2 arms)** | | **$373.93** |

> **Not included in the total:** the **3D-printed parts** (~800 g PETG, ~$14 in filament —
> print your own or use a service; see [`print/`](print/)) and the **shared consumables**
> below.

**Servo count:** 14 total = 2 arms × 7 servos (IDs 0–6 per arm). Two 6-packs + one 2-pack =
14, with zero spare. A single-arm build needs 7 servos (one 6-pack + one 2-pack).

## Also required (not in the total)

Commodity items needed to build and run a set, but left out of the cost above — most people
already have them, and the ones you'd buy come in bulk packs that last many builds.

| Item | Qty | For |
|------|-----|-----|
| USB-C cable | 2 (one per arm) | Driver board → host computer. Any data-capable cable. |
| Super glue | 1 | Gluing the hardstop home onto M1 (Step 2); optionally mounting the board (see below). |
| Heat-set inserts — M2.5 | 8 (4 per arm) | Mounting the driver board to the base. The board is then secured with the small screws that come with the servos |
| Rubber band — sturdy ~[#32](https://www.amazon.com/Alliance-26324-Advantage-Contains-Approx/dp/B00A27PFOC) | 2 (one per arm) | Trigger return spring. Only a couple needed per set. |

> **No soldering iron?** You can skip the heat-set inserts entirely and **glue the
> driver board onto the back of the base** instead, mounting it the same way shown in the
> assembly reference photos. See [`ASSEMBLY.md`](assembly/ASSEMBLY.md) (Step 1, Group 4).

<!-- Provenance: internal GELLO BOM (Notion) 3a6b7cb7-364f-8033-8293-d405878abf79 -->
