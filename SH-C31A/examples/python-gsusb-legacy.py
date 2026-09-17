#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH)
# SPDX-License-Identifier: BSD-3-Clause
"""Read and send classic CAN frames on an older SH-C31A from Python, on Windows.

THIS FILE IS FOR THE ORIGINAL canable2 FIRMWARE.
    It reports itself over USB as product "canable2 gs_usb", made by
    "canable.io". Adapters made before September 2026 carry it, and so does
    older stock still moving through distribution.

    Those units are not faulty and they keep working. But three of their
    behaviours will mislead host software, and the first one is a safety
    problem on a live bus. Read them before you use this.

    A new adapter reports "SH-C31x" instead and should use python-gsusb.py.
    You do not have to work this out first: the script checks and tells you.

*** SAFETY: THIS FIRMWARE REPORTS listen-only AND DOES NOT HONOUR IT ***
    It reports listen-only and loopback support. It honours NEITHER. Ask it
    for listen-only and it still transmits and still acknowledges -- no error,
    no warning, nothing in the log.

    On a vehicle, or on a customer's machine, that means you believe you are
    a passive observer while you are actually interfering with the bus.

    If you need a guaranteed silent node, use an adapter running the current
    firmware, or prove silence with a witness node on a bus you own.

    An RX LED that never lights while traffic is clearly arriving is a strong
    hint you are holding this firmware.

AN ECHO IS NOT PROOF EITHER
    This firmware can return an echo for a frame it never put on the bus.
    Measured: ten frames pushed while the channel was closed produced ten
    echoes and zero frames on the wire. Do not use echoes as evidence that
    anything was transmitted.

NO CAN FD ON THIS FIRMWARE
    It does not report the capability, so the Linux kernel refuses to open FD
    outright. That is not a configuration problem and no flag works around it.
    CAN FD needs the current firmware -- see ../firmware/.

ON LINUX, DO NOT USE THIS FILE.
    The kernel's gs_usb driver claims the adapter and gives you an ordinary
    SocketCAN interface: see linux-socketcan.md.

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
    The same adapter carries 10 k, 125 k and 250 k perfectly well from
    SocketCAN.

    Do NOT carry that to our SH-C30A: its 48 MHz clock opens eight rates
    including 800 k, which cannot open here.

THE ONE THING THAT COSTS PEOPLE DAYS
    bus.send() returning is NOT proof the frame reached the bus. It hands the
    frame to the adapter over USB and returns; it does not wait for a CAN
    acknowledgement.

    With nothing else on the bus the controller retransmits forever, the
    transmit error counter climbs to 128, and the controller goes
    error-passive. Measured on this hardware family: TEC stops at 128 and it
    never reaches bus-off. Nothing is printed.

    To know a frame really went out: read bus.state, or read error frames, or
    put a second node on the bus. Do not infer it from send(), and on this
    firmware do not infer it from an echo either.

TWO SMALLER THINGS
    * Closing the channel DOES discard queued frames here. The current
      firmware does not, so that is one to re-check if you port code over.
    * Setting a bit timing always reports success, even one the device will
      not use -- it stays on the previous one and says nothing. Every firmware
      across both our products does this; only a frame that actually passes
      proves the rate. You reach it only by computing bit timings yourself;
      python-can rejects bad ones before the device sees them.

# AI-NOTE: This file targets ONE firmware of ONE product. The full
# identification table, the other firmware's row, and the R0..R6 rules for
# reading any of it are in README.md in this directory. Do not generalise
# anything here to the other firmware, or to our other product SH-C30A.
# The frames-in-flight ceiling of 30 quoted for this firmware is INHERITED
# from the current one, which shares the same single receive buffer structure.
# It has NOT been measured on this firmware.
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
THIS_FIRMWARE = (0x0000, "canable2 gs_usb")

# Everything else that answers to the same VID:PID, and where to go instead.
ELSEWHERE = {
    (0x0200, "SH-C31x"):
        "the firmware a new SH-C31A ships with -- use python-gsusb.py",
    (0x0000, "candleLight USB to CAN adapter"):
        "an SH-C30A, not an SH-C31A -- use that product's own examples",
    (0x0100, "SH-C30x"):
        "an SH-C30A, not an SH-C31A -- use that product's own examples",
    (0x0100, "sh-C30x"):
        "an SH-C30A, not an SH-C31A -- use that product's own examples",
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
        print("*** This adapter runs the original canable2 firmware. ***")
        print("    listen-only and loopback are REPORTED and NOT HONOURED:")
        print("    it transmits and acknowledges anyway. Do not put it on a")
        print("    bus you must not disturb. An echo is not proof of")
        print("    transmission on this firmware either. No CAN FD.")
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
        # This firmware discards queued frames on close. The current one does
        # not -- check that if you port this code across.
        #
        # close_bus(), not bus.shutdown() -- see its docstring.
        close_bus(bus)
    return 0


if __name__ == "__main__":
    sys.exit(main())
