#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH)
# SPDX-License-Identifier: BSD-3-Clause
"""Read and send classic CAN frames on a DSD TECH SH-C31G from Python.

Firmware: our v1.4 gs_usb build -- what the adapter ships with. Nothing to reflash.

WHICH ROUTE TO TAKE
    Linux   the kernel's gs_usb driver claims the adapter and gives you a normal
            SocketCAN interface. Simpler and faster than this script, and it is
            the only route here that carries CAN FD. See linux-socketcan.md.
    Windows this script, for classic CAN.
    macOS    this script, in principle. We have not run it on macOS.

CAN FD IS NOT ON THIS ROUTE
    The adapter does CAN FD, and does it well -- 5 Mbit/s measured. But we have
    only exercised FD over SocketCAN. For CAN FD, use Linux.

TWO LIMITS OF python-can, NOT OF THE ADAPTER
    * Its gs_usb backend refuses a bit rate where f_clock / bitrate exceeds 800,
      so on this board 125 kbit/s and 250 kbit/s will not open. The same adapter
      carries both fine from SocketCAN. Use 500000 or 1000000 here.
    * Rates it cannot hit exactly are rejected outright rather than silently
      adjusted, which is the behaviour you want.

INSTALL
    pip install python-can gs_usb pyusb

    python-can also needs the libusb runtime library, which Windows does not ship:

      * On Windows x86-64, "pip install libusb-package" provides it.
        NOTE: that package has no Windows ARM64 wheel. On an ARM64 machine take
        the official libusb release, put libusb-1.0.dll somewhere, and point
        LIBUSB_DIR below at it.
      * On Linux and macOS the system libusb is normally already present.

ONE THING THAT WILL BITE YOU
    Do not enumerate the device and then open it in the same process -- opening it
    twice fails with "Access denied". If you scan for adapters first, release the
    handles before calling can.Bus().
"""

import os
import sys

# Point this at the folder holding libusb-1.0.dll, or leave it as None if the
# library is already findable (pip package, system package, or on PATH).
LIBUSB_DIR = None

if LIBUSB_DIR:
    os.environ["PATH"] = LIBUSB_DIR + os.pathsep + os.environ.get("PATH", "")
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(LIBUSB_DIR)

import can  # noqa: E402  (import after the DLL directory is registered)

BITRATE = 500000        # 500000 or 1000000 -- see the note above

def main() -> int:
    print("python-can", can.__version__)

    # index=0 means "the first gs_usb adapter". With one adapter plugged in that
    # is the one you want. With several, python-can also accepts bus= and
    # address= to name a specific device.
    bus = can.Bus(interface="gs_usb", channel=0, bitrate=BITRATE, index=0)
    try:
        print("listening for 5 s at %d bit/s -- Ctrl-C to stop" % BITRATE)
        deadline = 5.0
        while deadline > 0:
            msg = bus.recv(timeout=1.0)
            deadline -= 1.0
            if msg is not None:
                print("  rx  id=0x%03X  dlc=%d  data=%s"
                      % (msg.arbitration_id, msg.dlc, msg.data.hex(" ")))

        # Sending needs at least one other node on the bus to acknowledge the
        # frame. On a bus with no other node this raises, and that is correct
        # behaviour, not a fault in the adapter.
        frame = can.Message(arbitration_id=0x123,
                            data=[0xDE, 0xAD, 0xBE, 0xEF],
                            is_extended_id=False)
        try:
            bus.send(frame, timeout=1.0)
            print("  tx  id=0x123 sent")
        except can.CanError as exc:
            print("  tx  failed: %s" % exc)
            print("      no other node on the bus, or the bit rate does not match")
    finally:
        bus.shutdown()
    return 0

if __name__ == "__main__":
    sys.exit(main())
