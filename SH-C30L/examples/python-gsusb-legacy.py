#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH)
# SPDX-License-Identifier: BSD-3-Clause
"""Read and send CAN frames on an older SH-C30L from Python, on Windows.

THIS FILE IS FOR THE ORIGINAL candleLight FIRMWARE.
    It reports itself over USB as product "candleLight USB to CAN adapter",
    made by "bytewerk". Adapters made before September 2026 carry it, and so
    does older stock still moving through distribution.

    Those units are not faulty and they keep working. This file exists because
    one of their behaviours differs from the current firmware in a way that
    will cost you a debugging session -- see DRAIN BEFORE YOU CLOSE below.

    A new adapter reports "SH-C30x" instead and should use python-gsusb.py.
    You do not have to work this out first: the script checks and tells you.

ON LINUX, DO NOT USE THIS FILE.
    The kernel's gs_usb driver claims the adapter and gives you an ordinary
    SocketCAN interface: see linux-socketcan.md.

INSTALL (Windows)
    pip install python-can gs_usb pyusb libusb-package

    libusb-package has no Windows ARM64 wheel. On an ARM64 machine, download
    the official libusb release, put libusb-1.0.dll somewhere, and set
    LIBUSB_DIR below to that folder.

    macOS: this should work, but we have not run it there.

DRAIN BEFORE YOU CLOSE  <- the reason this file is separate
    On this firmware, closing the channel does NOT discard frames still queued
    for transmission. They go out after you open it again -- possibly minutes
    later, into whatever bus you are attached to by then.

    So: let the queue empty before you close, or accept that leftovers will
    appear in your next session. The current firmware purges both queues on
    close and does not do this.

THE ONE THING THAT COSTS PEOPLE DAYS
    bus.send() returning is NOT proof the frame reached the bus. It hands the
    frame to the adapter over USB and returns; it does not wait for a CAN
    acknowledgement.

    With nothing else on the bus the controller retransmits forever, the
    transmit error counter climbs to 128, and the controller goes
    error-passive. Measured on this hardware: TEC stops at 128 and it never
    reaches bus-off. Nothing is printed.

    To know a frame really went out: read bus.state, or read error frames, or
    put a second node on the bus. Do not infer it from send().

TWO SMALLER THINGS ABOUT THIS FIRMWARE
    * Neither LED lights up. That is this firmware, not a broken board.
    * Setting a bit timing always reports success, even one the device will
      not use -- it stays on the previous one and says nothing. Every firmware
      across both our products does this; only a frame that actually passes
      proves the rate. You reach it only by computing bit timings yourself;
      python-can rejects bad ones before the device sees them.

10 kbit/s DOES NOT TRANSMIT ON THIS BOARD
    Measured on the SH-C30A, not on the SH-C30L itself -- same image,
    equivalent transceiver from a different vendor. Assume it applies here
    until we publish a measurement on this board.

    A property of the board, not of the firmware -- reflashing will not change
    it. The usable range is 100 kbit/s - 1 Mbit/s. README.md has the mechanism.

# AI-NOTE: This file targets ONE firmware of ONE product. The full
# identification table, the other firmware's row, and the R0..R6 rules for
# reading any of it are in README.md in this directory. Do not generalise
# anything here to the other firmware, or to our other product SH-C31A.
"""

import os
import sys

# Folder holding libusb-1.0.dll. Leave as None if the library is already
# findable (libusb-package, a system package, or on PATH).
LIBUSB_DIR = None

if LIBUSB_DIR:
    os.environ["PATH"] = LIBUSB_DIR + os.pathsep + os.environ.get("PATH", "")
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(LIBUSB_DIR)

import can    # noqa: E402  (import after the DLL directory is registered)
import usb.core   # noqa: E402
import usb.util   # noqa: E402

VID, PID = 0x1D50, 0x606F       # shared candleLight ID -- NOT unique to us

# What this file targets, as reported over USB.
THIS_FIRMWARE = (0x0000, "candleLight USB to CAN adapter")

# Everything else that answers to the same VID:PID, and where to go instead.
ELSEWHERE = {
    (0x0100, "SH-C30x"):
        "the firmware a new SH-C30L ships with -- use python-gsusb.py",
    (0x0100, "sh-C30x"):
        "the firmware a new SH-C30L ships with -- use python-gsusb.py",
    (0x0000, "canable2 gs_usb"):
        "an SH-C31A, not an SH-C30L -- use that product's own examples",
    (0x0200, "SH-C31x"):
        "an SH-C31A, not an SH-C30L -- use that product's own examples",
}

# python-can's gs_usb backend solves the bit timing itself, strictly: with this
# board's 48 MHz CAN clock it opens 83.333k, 100k, 125k, 250k, 500k, 750k, 800k
# and 1M, and refuses everything else before touching the device. All eight are
# measured, both firmwares, 20 frames each way. README.md has the full table.
# On Linux, SocketCAN is not restricted this way.
BITRATE = 500000


def _string(dev, index):
    """Read a USB string descriptor, tolerating index 0 (= no string)."""
    if not index:
        return None
    try:
        return usb.util.get_string(dev, index)
    except Exception:
        return None


def find_adapter():
    """Return (bus, address) for an adapter running the firmware this file is
    for, or None after explaining what was found instead.

    Releases every USB handle before returning. python-can cannot open a device
    this process still holds -- that is errno 13, "Access denied".
    """
    seen = []
    match = None
    for dev in usb.core.find(find_all=True, idVendor=VID, idProduct=PID):
        try:
            key = (int(dev.bcdDevice), _string(dev, dev.iProduct))
            if key == THIS_FIRMWARE:
                if match is None:
                    match = (dev.bus, dev.address)
            else:
                seen.append(key)
        finally:
            # Always, even on error. This is why the function returns numbers
            # rather than pyusb device objects.
            usb.util.dispose_resources(dev)

    if match:
        return match

    if not seen:
        print("No candleLight-family adapter found (VID:PID %04X:%04X)."
              % (VID, PID))
        return None

    print("Found an adapter, but not the firmware this file is written for:")
    for bcd, product in seen:
        where = ELSEWHERE.get((bcd, product), "not a firmware we publish notes for")
        print("  bcdDevice=0x%04X product=%r" % (bcd, product))
        print("    -> %s" % where)
    return None


def close_bus(bus):
    """Close the bus AND release the USB handle.

    bus.shutdown() alone is not enough when you opened with bus=/address=.
    python-can 4.6.1's GsUsbBus.shutdown() ends with a cleanup dance whose own
    comment says it exists to avoid errors on the next __init__(), but it is
    guarded by `if self._index is not None`. Open by bus/address and that is
    skipped, the pyusb handle stays claimed, and the NEXT can.Bus() in the same
    process fails with errno 13.

    A script that opens once and exits does not care. A program that reopens --
    to change bit rate, in a test loop, anything long-running -- very much does.
    """
    if bus is None:
        return
    try:
        bus.shutdown()
    finally:
        try:
            usb.util.dispose_resources(bus.gs_usb.gs_usb)
        except Exception:
            pass


def main() -> int:
    print("python-can", can.__version__)

    target = find_adapter()
    if target is None:
        return 1

    # Selected by bus and address, not by index. index=0 means "whichever the
    # backend enumerates first", and our two products share VID:PID 1D50:606F,
    # so on a machine with both plugged in "first" can be the wrong product.
    # index and bus/address are mutually exclusive -- passing both raises
    # CanInitializationError.
    bus = can.Bus(interface="gs_usb", channel=0, bitrate=BITRATE,
                  bus=target[0], address=target[1])
    try:
        print("listening for 5 s at %d bit/s" % BITRATE)
        for _ in range(5):
            msg = bus.recv(timeout=1.0)
            if msg is not None:
                print("  rx  id=0x%03X  dlc=%d  data=%s"
                      % (msg.arbitration_id, msg.dlc, msg.data.hex(" ")))

        frame = can.Message(arbitration_id=0x123,
                            data=[0xDE, 0xAD, 0xBE, 0xEF],
                            is_extended_id=False)
        try:
            bus.send(frame, timeout=1.0)
            print("  tx  id=0x123 handed to the adapter")
        except can.CanError as exc:
            # Only the USB transfer failing lands here. A missing CAN
            # acknowledgement does not.
            print("  tx  the adapter did not accept the frame: %s" % exc)

        print("  bus state after sending: %s" % bus.state)
        print("  (ERROR_PASSIVE usually means nothing acknowledged the frame,")
        print("   or the bit rate does not match the rest of the bus)")
    finally:
        # DRAIN BEFORE YOU CLOSE, see the module docstring. On this firmware
        # anything still queued when you close is transmitted after the next
        # open, not discarded. This example sends one frame, so in practice the
        # queue is empty here -- a program that sends in bulk has to check.
        #
        # close_bus(), not bus.shutdown() -- see its docstring.
        close_bus(bus)
    return 0


if __name__ == "__main__":
    sys.exit(main())
