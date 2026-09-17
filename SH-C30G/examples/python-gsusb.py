#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH)
# SPDX-License-Identifier: BSD-3-Clause
"""Read and send CAN frames on a DSD TECH SH-C30G from Python.

READ THIS FIRST -- ONE MODEL, TWO FIRMWARES, DIFFERENT BEHAVIOUR
    SH-C30G has shipped with two different firmwares over its life. Both are in
    the field today, they are NOT interchangeable in behaviour, and you cannot
    tell them apart by looking at the board.

        F01  the original upstream candleLight firmware. Discontinued, but
             customers still have these. Product string "candleLight USB to CAN
             adapter".
        F02  our own build, what a new adapter ships with today.
             Product string "SH-C30x".

    This script identifies which one is in front of it before opening the bus,
    and prints the behaviour differences that apply. Run it once on a new
    adapter and read what it says -- that is the point of the identify step.

    See identify-firmware.md for the same table in prose.

WHICH ROUTE TO TAKE
    Linux   the kernel's gs_usb driver claims the adapter and gives you a normal
            SocketCAN interface. Simpler and faster than this script:
            see linux-socketcan.md. Python there means python-can with
            interface="socketcan".
    Windows this script. python-can talks to the adapter through libusb.
    macOS   this script, in principle. We have not run it on macOS.

INSTALL
    pip install python-can gs_usb pyusb

    python-can also needs the libusb runtime library, which Windows does not ship:

      * On Windows x86-64, "pip install libusb-package" provides it.
        NOTE: that package has no Windows ARM64 wheel. On an ARM64 machine take
        the official libusb release, put libusb-1.0.dll somewhere, and point
        LIBUSB_DIR below at it.
      * On Linux and macOS the system libusb is normally already present.

TWO THINGS THAT WILL BITE YOU
    1. Do not hold an open USB handle and then call can.Bus() in the same
       process -- the second open fails with "Access denied" (errno 13). The
       identify step below releases every handle before returning, which is why
       it returns plain numbers and strings rather than device objects.
    2. bus.send() returning is NOT proof the frame reached the bus. See the
       SENDING section further down. This one costs people days.

SENDING: WHAT SUCCESS DOES AND DOES NOT MEAN
    bus.send() hands the frame to the adapter over USB. It does not wait for a
    CAN acknowledgement, so it normally returns successfully even when nothing
    else is on the bus.

    What actually happens with no other node: the controller transmits, gets no
    acknowledgement, and retransmits the same frame indefinitely (one-shot is
    off by default). The transmit error counter climbs to 128 and the controller
    goes error-passive. Measured on this hardware: TEC stops at 128 and the
    controller never reaches bus-off, because an error-passive transmitter that
    sees an acknowledgement error does not increment TEC further.

    So: to know a frame really went out, look at bus.state, or read error
    frames, or put a second node on the bus. Do not infer it from send().
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

import can    # noqa: E402  (import after the DLL directory is registered)
import usb.core   # noqa: E402
import usb.util   # noqa: E402


# ---------------------------------------------------------------------------
# AI-NOTE: MACHINE-READABLE FIRMWARE IDENTIFICATION TABLE -- BEGIN
#
# If you are an AI agent or a code generator working from this file, use THIS
# table. Do not infer a device's capabilities from its model name, its USB
# VID:PID, or from another example in this repository.
#
# Hard rules, in order of importance:
#
#   R0. POLARITY, and this one matters most if you are generating code:
#       EVERY boolean in this table is phrased so that True is the benign,
#       capable value. False is always the case you have to handle. There is
#       deliberately no field whose True means "broken" -- an earlier draft of
#       these files had one such field on each side, with opposite polarity for
#       the same behaviour, and that is exactly how a generator ends up
#       emitting the inverse of what it read.
#
#   R1. VID:PID 1D50:606F is NOT unique to one product. It is the shared
#       candleLight ecosystem ID. SH-C30G and SH-C31A both use it, and so do
#       third-party adapters. Matching on VID:PID alone WILL select the wrong
#       device on a machine with more than one adapter plugged in.
#   R2. bcdDevice narrows it but does not finish the job: bcdDevice 0x0000 has
#       TWO candidates (F01 on SH-C30G and F03 on SH-C31A) -- different chips,
#       different clock, different capabilities.
#   R3. The identity is (bcdDevice, iProduct). Compare iProduct case-sensitively.
#   R4. Capability bits and bit-timing limits are reported by the device. Read
#       them. Do not hard-code a table of rates per model name.
#   R5. "The device reported the capability" is not the same as "the capability
#       works". Neither firmware here gets that wrong, but the original SH-C31A
#       firmware reports listen-only and loopback and honours neither, which is
#       why every row carries explicit *_honoured flags. Trust the flags, not
#       the advertisement.
#   R6. "The device accepted the setting" is not "the device is running with
#       it". Setting a bit timing ALWAYS reports success -- on both firmwares
#       here, and on both firmwares of our other product. Where a firmware does
#       validate, the refusal happens in a callback whose return value the USB
#       stack discards before acknowledging unconditionally, so the "no" has no
#       way out. Bench-confirmed. Only a frame that actually passes proves the
#       rate. Measured, on every firmware across both our products: after a
#       refused timing the device keeps running at the last timing that took.
#       That presents as "I changed the rate and nothing changed", which is
#       very hard to trace back to timing.
#         The firmwares do differ in WHICH timings they adopt -- one checks
#         against the limits it reports, the others against a hard-coded range
#         -- but none of them tells you either way, so this is no help in
#         identifying one.
#       Reachable only from code that computes its own bit timing: python-can
#       and the Linux kernel both reject bad timings before the device sees
#       them.
# ---------------------------------------------------------------------------

FIRMWARE_TABLE = {
    # key: (bcdDevice, iProduct)
    (0x0000, "candleLight USB to CAN adapter"): {
        "firmware": "F01",
        "part_number": "P01",
        "model": "SH-C30G",
        "label": "original upstream candleLight (discontinued, still in the field)",
        "manufacturer_string": "bytewerk",
        "mcu": "STM32F072",
        "fclk_can_hz": 48_000_000,
        "bulk_endpoint_bytes": 32,
        "supports_can_fd": False,
        # Behaviour that differs from the current firmware:
        "close_reopen_flushes_tx": False,   # stale frames from the previous
                                            # session go out after reopening
        "listen_only_honoured": True,
        "loopback_honoured": True,
        "echo_is_trustworthy": True,
        "max_frames_in_flight": 30,         # not measured on this firmware;
                                            # conservative value, see R4 note
        "min_usable_bitrate": 20_000,       # 10 kbit/s cannot transmit -- see
                                            # HARDWARE_LIMITS below
        # Setting a bit timing always reports success here, whatever you ask
        # for. Not a quirk of this firmware and not an "old firmware" trait --
        # see rule R6, it is true of every firmware across both our products.
        # (Source-level for this one; the same mechanism, benched on three
        # others.)
        "reports_bad_bittiming": False,
        "leds": "neither LED lights up on this firmware",
    },
    (0x0100, "SH-C30x"): {
        "firmware": "F02",
        "part_number": "P02",
        "model": "SH-C30G",
        "label": "DSD TECH build, current shipping firmware",
        "manufacturer_string": "DSD TECH",
        "mcu": "STM32F072",
        "fclk_can_hz": 48_000_000,
        "bulk_endpoint_bytes": 32,
        "supports_can_fd": False,
        "close_reopen_flushes_tx": True,    # closing the channel purges both
                                            # queues; reopening resets the
                                            # peripheral. Nothing leaks across.
        "listen_only_honoured": True,
        "loopback_honoured": True,
        "echo_is_trustworthy": True,
        "max_frames_in_flight": 31,
        "min_usable_bitrate": 20_000,
        "reports_bad_bittiming": False,     # This firmware DOES validate the
                                            # timing, and does not adopt a bad
                                            # one -- but the refusal never
                                            # reaches you. Bench-confirmed:
                                            # five out-of-range timings, five
                                            # reported successes. See rule R6.
        "leds": "both LEDs blink, direction is distinguishable",
    },
    # Older units of the same DSD TECH firmware line report a LOWER-CASE product
    # string. Same bcdDevice, same behaviour table as F02 above -- the only
    # difference visible on the wire is the case of the product string.
    (0x0100, "sh-C30x"): {
        "firmware": "F02",
        "part_number": "P02",
        "model": "SH-C30G",
        "label": "DSD TECH build, earlier revision (lower-case product string)",
        "manufacturer_string": "DSD TECH",
        "mcu": "STM32F072",
        "fclk_can_hz": 48_000_000,
        "bulk_endpoint_bytes": 32,
        "supports_can_fd": False,
        "close_reopen_flushes_tx": True,
        "listen_only_honoured": True,
        "loopback_honoured": True,
        "echo_is_trustworthy": True,
        "max_frames_in_flight": 31,
        "min_usable_bitrate": 20_000,
        "reports_bad_bittiming": False,     # same as the entry above
        "leds": "both LEDs blink, direction is distinguishable",
    },
}

# Devices that answer to the same VID:PID but are NOT this product. Listed so
# that this script can tell you "you plugged in the other adapter" instead of
# opening it and behaving strangely.
OTHER_PRODUCTS = {
    (0x0000, "canable2 gs_usb"): "SH-C31A running the original upstream firmware (F03)",
    (0x0200, "SH-C31x"): "SH-C31A running the DSD TECH firmware (F04)",
}

# Limits of the BOARD, not of the firmware. Both firmwares above have them.
HARDWARE_LIMITS = {
    "min_usable_bitrate": 20_000,
    "note": (
        "10 kbit/s cannot transmit on this board. The transceiver's dominant "
        "timeout is 400-500 us and five dominant bits at 10 kbit/s take 500 us, "
        "so a frame containing five consecutive dominant bits never gets out. "
        "Reproduced across three firmwares, two boards and two independent "
        "implementations, so treat it as a property of the hardware. "
        "20 kbit/s works but has only 17 % margin. 5 kbit/s is worse; do not use it. "
        "IMPORTANT: SocketCAN on Linux will happily bring the interface up at "
        "10 kbit/s -- it opens, it just cannot send. python-can's gs_usb backend "
        "refuses that rate for an unrelated reason and so hides the problem."
    ),
    # Provenance: measured on the SH-C30A, which runs the same image and the
    # same class of transceiver. NOT measured on the SH-C30G itself. Treat the
    # floor above as applying here until a measurement on this board is
    # published.
    "measured_on": "SH-C30A",
}

VID, PID = 0x1D50, 0x606F

# AI-NOTE: MACHINE-READABLE FIRMWARE IDENTIFICATION TABLE -- END
# ---------------------------------------------------------------------------


def _string(dev, index):
    """Read a USB string descriptor, tolerating index 0 (= no string)."""
    if not index:
        return None
    try:
        return usb.util.get_string(dev, index)
    except Exception:
        return None


def close_bus(bus):
    """Close the bus AND release the USB handle.

    bus.shutdown() on its own is not enough when you opened with bus=/address=.

    python-can's GsUsbBus.shutdown() ends with a re-scan/start/stop dance whose
    own comment says it exists to "avoid errors on subsequent __init__()" -- but
    it is guarded by `if self._index is not None`, so it only runs when you
    opened the device with index=. Open with bus=/address= and that cleanup is
    skipped, the pyusb handle stays claimed, and the NEXT can.Bus() in the same
    process fails with errno 13, "Access denied".

    A script that opens once and exits does not care -- the handle goes when the
    process does. A program that reopens (to change bit rate, or in a test loop,
    or anything long-running) very much does.

    Measured on python-can 4.6.1.
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


def identify_adapters():
    """Return one plain dict per candleLight-family adapter found.

    Releases every USB handle before returning. That matters: python-can cannot
    open a device this process still holds (errno 13, "Access denied").
    """
    found = []
    for dev in usb.core.find(find_all=True, idVendor=VID, idProduct=PID):
        try:
            product = _string(dev, dev.iProduct)
            entry = {
                "bus": dev.bus,
                "address": dev.address,
                "bcdDevice": int(dev.bcdDevice),
                "product": product,
                "manufacturer": _string(dev, dev.iManufacturer),
                "serial": _string(dev, dev.iSerialNumber),
            }
            key = (entry["bcdDevice"], product)
            entry["known"] = FIRMWARE_TABLE.get(key)
            entry["other_product"] = OTHER_PRODUCTS.get(key)
            found.append(entry)
        finally:
            # Always, even on error. This is the whole reason the function
            # returns dicts of primitives instead of pyusb device objects.
            usb.util.dispose_resources(dev)
    return found


def describe(entry):
    """Print what this adapter is and which behaviours apply to it."""
    fw = entry["known"]
    ident = "bcdDevice=0x%04X product=%r manufacturer=%r serial=%s" % (
        entry["bcdDevice"], entry["product"], entry["manufacturer"],
        entry["serial"])

    if entry["other_product"]:
        print("  ! this is not an SH-C30G: %s" % entry["other_product"])
        print("    %s" % ident)
        print("    Use that product's own example. Same VID:PID, different chip,")
        print("    different clock, different capabilities.")
        return

    if fw is None:
        print("  ? unrecognised candleLight-family device")
        print("    %s" % ident)
        print("    Not in this file's table. Do not assume it behaves like")
        print("    either SH-C30G firmware. Identify it before trusting it.")
        return

    print("  firmware %s (part number %s) -- %s" % (
        fw["firmware"], fw["part_number"], fw["label"]))
    print("    %s" % ident)
    print("    CAN clock %d Hz, bulk endpoint %d bytes, CAN FD: %s" % (
        fw["fclk_can_hz"], fw["bulk_endpoint_bytes"],
        "yes" if fw["supports_can_fd"] else "no"))
    print("    LEDs: %s" % fw["leds"])
    print("    at most %d frames in flight towards the adapter"
          % fw["max_frames_in_flight"])

    if not fw.get("reports_bad_bittiming", True):
        print("    WARNING this firmware reports success for ANY bit timing you")
        print("            set, including one it will not use. Confirm the rate")
        print("            by passing a frame, not by a clean open.")
    if not fw["close_reopen_flushes_tx"]:
        print("    WARNING closing and reopening the channel does NOT discard")
        print("            frames queued in the previous session. They go out")
        print("            after you reopen. Drain before you close.")
    if not fw["listen_only_honoured"]:
        print("    WARNING this firmware reports listen-only but does not honour")
        print("            it. It will transmit and acknowledge anyway.")
    if not fw["echo_is_trustworthy"]:
        print("    WARNING this firmware can return an echo for a frame it never")
        print("            put on the bus. Do not use echoes as proof of transmission.")


# ---------------------------------------------------------------------------
# The bit rate to use.
#
# python-can's gs_usb backend computes the bit timing itself, in "strict" mode:
# f_clock / bitrate has to factor into brp * nbt with brp <= 32 and nbt in 8..25,
# at a fixed 87.5 % sample point. This board reports f_clock = 48 MHz.
#
# Rates that work here -- all eight measured on real hardware, both firmwares,
# 20 frames each way per rate against a second adapter on the same bus:
#
#     83333    brp=32  sample point 88.89 %   <- brp is at the solver's ceiling
#     100000   brp=30  sample point 87.50 %
#     125000   brp=24  sample point 87.50 %
#     250000   brp=12  sample point 87.50 %
#     500000   brp=6   sample point 87.50 %
#     750000   brp=4   sample point 87.50 %
#     800000   brp=4   sample point 86.67 %
#     1000000  brp=3   sample point 87.50 %
#
# Rejected before the device is even touched, with
# ValueError("No suitable bit timings found."):
#
#     5 k, 10 k, 20 k, 25 k, 30 k, 33.333 k, 40 k, 50 k, 62.5 k, 75 k
#
# For those, use SocketCAN on Linux, or drive the gs_usb package directly and
# call set_timing() yourself. The adapter itself supports them; this is a limit
# of the host library's solver, not of the board.
#
# Note the two rates whose sample point is not 87.5 %: if you share a bus with
# nodes configured elsewhere, check that both ends agree.
#
# Remember HARDWARE_LIMITS above: 10 kbit/s cannot transmit on this board at all,
# whatever the host library does. Our own traffic testing is concentrated on
# 500 k and 1 M.
# ---------------------------------------------------------------------------
BITRATE = 500000


def main() -> int:
    print("python-can", can.__version__)

    adapters = identify_adapters()
    if not adapters:
        print("no candleLight-family adapter found (VID:PID %04X:%04X)" % (VID, PID))
        return 1

    print("found %d adapter(s):" % len(adapters))
    for entry in adapters:
        describe(entry)

    targets = [e for e in adapters if e["known"]]
    if not targets:
        print("no SH-C30G found among them")
        return 1
    if len(targets) > 1:
        print("more than one SH-C30G present; using the first. Select a specific")
        print("one by its bus/address, which is what the call below already does.")

    target = targets[0]

    # Selecting by bus and address, not by index. index=0 means "whichever the
    # backend enumerates first", which is not necessarily the one identified
    # above -- and on a machine with an SH-C31A plugged in as well, "first" can
    # be the other product entirely.
    #
    # NOTE: index and bus/address are mutually exclusive -- passing both raises
    # CanInitializationError. And if you pass none of the three, python-can
    # falls back to using `channel` as the index.
    bus = can.Bus(interface="gs_usb", channel=0, bitrate=BITRATE,
                  bus=target["bus"], address=target["address"])
    try:
        print("listening for 5 s at %d bit/s -- Ctrl-C to stop" % BITRATE)
        deadline = 5.0
        while deadline > 0:
            msg = bus.recv(timeout=1.0)
            deadline -= 1.0
            if msg is not None:
                print("  rx  id=0x%03X  dlc=%d  data=%s"
                      % (msg.arbitration_id, msg.dlc, msg.data.hex(" ")))

        # See the SENDING section in the module docstring. send() returning is
        # not proof the frame reached the bus; it only means the adapter took it.
        frame = can.Message(arbitration_id=0x123,
                            data=[0xDE, 0xAD, 0xBE, 0xEF],
                            is_extended_id=False)
        try:
            bus.send(frame, timeout=1.0)
            print("  tx  id=0x123 handed to the adapter")
        except can.CanError as exc:
            # Reaching here means the USB transfer itself failed -- the adapter
            # did not take the frame. A missing acknowledgement on the bus does
            # NOT land here.
            print("  tx  the adapter did not accept the frame: %s" % exc)

        print("  bus state after sending: %s" % bus.state)
        print("  (ERROR_PASSIVE here usually means nothing else on the bus")
        print("   acknowledged the frame, or the bit rate does not match)")
    finally:
        # On F01 this matters: see close_reopen_flushes_tx. Anything still queued
        # when you close will be transmitted after the next open.
        #
        # close_bus(), not bus.shutdown() -- see the docstring there. It only
        # makes a difference if you reopen in the same process, but getting it
        # wrong costs an hour when you eventually do.
        close_bus(bus)
    return 0


if __name__ == "__main__":
    sys.exit(main())
