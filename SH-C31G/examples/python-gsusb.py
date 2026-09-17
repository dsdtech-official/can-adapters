#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH)
# SPDX-License-Identifier: BSD-3-Clause
"""Read and send classic CAN frames on a DSD TECH SH-C31G from Python, on Windows.

THIS FILE IS FOR THE FIRMWARE A NEW ADAPTER SHIPS WITH.
    It reports itself over USB as product "SH-C31x", made by "DSD TECH".
    If you bought the adapter recently, this is the one you have.

    Adapters made before September 2026 carry the original upstream canable2
    firmware instead, which reports "canable2 gs_usb". That one behaves
    differently in ways that will mislead host software -- one of them is a
    safety problem on a live bus -- so it gets its own file:
    python-gsusb-legacy.py

    You do not have to work out which one you have before running this. The
    script checks, and if it finds the older firmware it tells you and stops.
    README.md also shows you how to check by hand.

CAN FD IS NOT ON THIS ROUTE
    This firmware does CAN FD and does it well, rated to 5 Mbit/s -- the
    transceiver's ceiling. But we have only exercised FD over SocketCAN.
    For CAN FD, use Linux: see linux-socketcan.md.

    Provenance: the per-rate sweep was run on an SH-C31A -- same chip, same
    image, but no isolation in the signal path. What has been run on the
    SH-C31G itself is CAN FD with the isolation in circuit, including an
    extended soak.

ON LINUX, DO NOT USE THIS FILE AT ALL.
    The kernel's gs_usb driver claims the adapter and gives you an ordinary
    SocketCAN interface, which is simpler, faster, and carries FD.

INSTALL (Windows)
    pip install python-can gs_usb pyusb libusb-package

    libusb-package has no Windows ARM64 wheel. On an ARM64 machine, download
    the official libusb release, put libusb-1.0.dll somewhere, and set
    LIBUSB_DIR below to that folder.

    macOS: this should work, but we have not run it there.

ONLY TWO BIT RATES OPEN HERE, AND THAT IS python-can, NOT THE ADAPTER
    Its gs_usb backend solves the bit timing itself, strictly: f_clock/bitrate
    has to factor into brp * nbt with brp <= 32 and nbt in 8..25. This board
    runs a 170 MHz CAN clock, which leaves 500000 and 1000000 and nothing else.

    Measured: 18 rates tried on real hardware, only those two open, both 20
    frames each way. The same adapter carries 10 k, 125 k and 250 k perfectly
    well from SocketCAN at 0.0000 % loss.

    Do NOT carry that list to our SH-C30A: its 48 MHz clock opens eight rates
    including 800 k, which cannot open here.

DRAIN BEFORE YOU CLOSE
    On this firmware, closing the channel does NOT discard frames still queued
    for transmission. They go out after you open it again -- possibly minutes
    later, into whatever bus you are attached to by then. The older firmware
    discards them instead, so this is one to re-check if you port code between
    the two.

THE ONE THING THAT COSTS PEOPLE DAYS
    bus.send() returning is NOT proof the frame reached the bus. It hands the
    frame to the adapter over USB and returns; it does not wait for a CAN
    acknowledgement.

    With nothing else on the bus the controller retransmits forever, the
    transmit error counter climbs to 128, and the controller goes
    error-passive. Measured on this hardware family: TEC stops at 128 and it
    never reaches bus-off. Nothing is printed.

    To know a frame really went out: read bus.state, or read error frames, or
    put a second node on the bus. Do not infer it from send().

THERE IS A LIMIT ON FRAMES IN FLIGHT: 30
    The adapter holds a fixed pool of frame objects. Push more unacknowledged
    frames at it than the pool holds and the extra ones are lost -- usually
    with no overflow bit and no error frame at all. Measured on this firmware.
    This example sends one frame so it cannot hit it; any bulk sender must.

# AI-NOTE: This file targets ONE firmware of ONE product. The full
# identification table, the other firmware's row, and the R0..R6 rules for
# reading any of it are in README.md in this directory. Do not generalise
# anything here to the other firmware, or to our other product SH-C30A.
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
THIS_FIRMWARE = (0x0200, "SH-C31x")

# Everything else that answers to the same VID:PID, and where to go instead.
ELSEWHERE = {
    (0x0000, "canable2 gs_usb"):
        "the original canable2 firmware -- use python-gsusb-legacy.py",
    (0x0000, "candleLight USB to CAN adapter"):
        "an SH-C30A, not an SH-C31G -- use that product's own examples",
    (0x0100, "SH-C30x"):
        "an SH-C30A, not an SH-C31G -- use that product's own examples",
    (0x0100, "sh-C30x"):
        "an SH-C30A, not an SH-C31G -- use that product's own examples",
}

# See the docstring: 170 MHz leaves only these two reachable from python-can.
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
