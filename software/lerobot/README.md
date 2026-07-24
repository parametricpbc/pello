# Using the leader arms with LeRobot follower robots

The GELLO leader arms drive follower robots through [🤗 LeRobot](https://github.com/huggingface/lerobot).
This directory ships the U-Arm teleoperator module and the SO-100 / YAM follower scripts.

```
lerobot/
├── so100/
│   ├── dual_uarm_yam_teleop.py   # bimanual: two YAM arms, each driven as an SO-100 follower
│   └── so100_teleop.py           # single-arm SO-100
├── uarm.py                       # U-Arm teleoperator module (ServoReader)
└── README.md
```

## Setup

1. Install LeRobot with the `[feetech]` extra — see the
   [LeRobot installation guide](https://github.com/huggingface/lerobot/blob/main/README.md).
   No ROS required.
2. Place `uarm.py` in your LeRobot teleoperators directory:
   ```bash
   mv uarm.py ${PATH_TO_YOUR_LEROBOT}/lerobot/src/lerobot/teleoperators/
   ```

## Run

Single-arm SO-100:
```bash
python so100_teleop.py
```

Bimanual YAM (each arm driven as an SO-100 follower):
```bash
python dual_uarm_yam_teleop.py
```

Set the leader (U-Arm) port and the follower robot port at the top of each `*_teleop.py`
script before running.
