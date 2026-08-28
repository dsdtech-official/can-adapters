#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH)
# SPDX-License-Identifier: BSD-3-Clause
"""Read and send CAN frames on a DSD TECH SH-C31A running the slcan firmware.

Firmware:  slcan  (the adapter appears as a serial port)
Requires:  pip install python-can

If your adapter appears as a raw USB device instead of a serial port, it is running
candlelight — see linux-socketcan.md, or python-can's gs_usb interface on Windows.
"""

import can

# Windows: "COM3"      Linux: "/dev/ttyACM0"      macOS: "/dev/tty.usbmodem*"
CHANNEL = "COM3"
BITRATE = 500000

with can.Bus(interface="slcan", channel=CHANNEL, bitrate=BITRATE) as bus:
    # Send one frame
    bus.send(can.Message(arbitration_id=0x123,
                         data=[0xDE, 0xAD, 0xBE, 0xEF],
                         is_extended_id=False))

    # Print everything that arrives, until Ctrl-C
    for msg in bus:
        print(msg)
