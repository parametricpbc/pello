# set new id for servo
import sys
from scservo_sdk import *

SERIAL_PORT = '/dev/cu.usbmodemXXXX'  # macOS; use /dev/ttyUSB0 on Linux

if len(sys.argv) != 2 or not sys.argv[1].isdigit():
    print("Usage: python feetech_servo_changeid.py <new_id>")
    print("  new_id: 1–7 (connect only ONE servo at a time)")
    print("  Example: python feetech_servo_changeid.py 3")
    sys.exit(1)

new_id = int(sys.argv[1])
if not (0 <= new_id <= 6):
    print(f"Error: new_id must be 0–6, got {new_id}")
    sys.exit(1)

portHandler = PortHandler(SERIAL_PORT)
packetHandler = sms_sts(portHandler)

# Open port
if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    quit()

# Set port baudrate 1000000
if portHandler.setBaudRate(1000000):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    quit()

print(f"Set the servo's id to: {new_id} (Make sure only one servo is connected)...")

# Unlock EPROM
packetHandler.unLockEprom(BROADCAST_ID)
time.sleep(0.1)

# Write new id in
result, error = packetHandler.write1ByteTxRx(BROADCAST_ID, SMS_STS_ID, new_id)
if result != COMM_SUCCESS:
    print(f"Failed to set id: {packetHandler.getTxRxResult(result)}")
    # Lock EPROM
    packetHandler.LockEprom(BROADCAST_ID)
    portHandler.closePort()
    exit()

print(f"Succeed to set id: {new_id}")
time.sleep(0.1)

# Lock EPROM
packetHandler.LockEprom(new_id)
time.sleep(0.1)