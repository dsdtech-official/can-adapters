#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH)
# SPDX-License-Identifier: BSD-3-Clause
"""Read and send classic CAN frames on a DSD TECH SH-C31B from Python.

The SH-C31B runs slcan firmware and appears as an ordinary serial port, so this
needs nothing but pyserial:

    pip install pyserial
    python python-slcan.py                 # auto-detect the port
    python python-slcan.py COM7            # or name it
    python python-slcan.py /dev/ttyACM0

READ THIS FIRST -- YOU CANNOT IDENTIFY THIS ADAPTER BY LOOKING AT IT
    The silkscreen says "SH-C31A" on both products. SH-C31A and SH-C31B are the
    same board; the name says which firmware was installed at the factory.

        a serial port appears   -> SH-C31B, slcan firmware   -> this file
        a CAN network device    -> SH-C31A, gs_usb firmware  -> ../../SH-C31A/examples/

    They speak completely different protocols over USB. Nothing here works on
    the other one, and it will not fail with a clear message -- the port simply
    will not be there.

WHY pyserial AND NOT python-can's slcan BACKEND
    python-can can drive this adapter, and for plain 500 k / 1 M work it is
    fine. But its bitrate table follows the CANable convention, which disagrees
    with this firmware on one entry:

        you ask for bitrate=750000  ->  it sends S7  ->  the adapter runs 800000
        you ask for bitrate=800000  ->  rejected as an invalid bitrate

    Neither side reports anything; you are simply 6.7% off. Going through the
    serial port directly means the command you send is the command that runs.
    (On Linux, slcand does NOT have this problem -- the kernel's table agrees
    with the adapter. It is specific to python-can.)

WHAT THIS FILE DOES NOT COVER
    CAN FD. The adapter supports it, but FD has enough sharp edges of its own
    that it lives in canfd.md.
"""

import sys
import time

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    sys.exit("pyserial is required:  pip install pyserial")


# Single-digit rate codes, as THIS firmware defines them. They are not a
# standard -- other slcan firmwares assign different rates to the same digit.
# S7 in particular is 800k here (matching LAWICEL and the Linux kernel), not
# the 750k that CANable-derived software assumes.
BITRATES = {
    10_000: "S0",
    20_000: "S1",
    50_000: "S2",
    100_000: "S3",
    125_000: "S4",
    250_000: "S5",
    500_000: "S6",
    800_000: "S7",
    1_000_000: "S8",
}

OK = b"\r"
ERR = b"\a"  # 0x07 -- this firmware's "no" to any command it did not like


class SlcanError(Exception):
    pass


class Adapter:
    def __init__(self, port, timeout=1.0):
        # The adapter is USB CDC: the baud rate on the host side is ignored,
        # any value works.
        self.ser = serial.Serial(port, 115200, timeout=timeout)
        self.is_open = False
        self._rx = b""

    # -- plumbing ---------------------------------------------------------

    def _cmd(self, text, expect_string=False, expect_reply=True):
        """Send one command and check the reply.

        Reply convention on this firmware:
            \\r        success
            \\a (0x07) error, or command not understood
            +...\\r    a string answer (V, *Boot0:? ...)

        EXCEPTION -- 'C' (close) answers NOTHING AT ALL. Not \\r, not \\a,
        whether the channel was open or already closed. Measured on a real
        board on 2026-09-17. So it is sent with expect_reply=False;
        waiting for an answer just burns the timeout.

        NOTE: if MF (command feedback) has been turned on, every reply gains a
        leading '#'. This file never turns MF on. If you do, this parser -- and
        most other slcan host software -- will stop understanding the replies.
        """
        self.ser.write(text.encode("ascii") + b"\r")
        self.ser.flush()
        if not expect_reply:
            time.sleep(0.05)
            try:
                self.ser.reset_input_buffer()
            except Exception:
                pass
            return b""
        reply = b""
        deadline = time.time() + 1.0
        while time.time() < deadline:
            ch = self.ser.read(1)
            if not ch:
                break
            if ch == ERR:
                self._resync()
                raise SlcanError("adapter rejected %r" % text)
            if ch == OK:
                return reply
            reply += ch
        self._resync()
        if expect_string:
            raise SlcanError("no reply to %r" % text)
        raise SlcanError("timed out waiting for a reply to %r" % text)

    def _resync(self):
        """Throw away anything still arriving after a failed command, so its
        tail is not read as the reply to the next one.

        Defensive only -- no case has been observed where it was required.
        """
        time.sleep(0.05)
        try:
            self.ser.reset_input_buffer()
        except Exception:
            pass

    # -- identity ---------------------------------------------------------

    def identify(self):
        """Return the V line as a dict. The single most useful command here."""
        raw = self._cmd("V", expect_string=True).decode("ascii", "replace")
        if raw.startswith("+"):
            raw = raw[1:]
        out = {}
        for part in raw.replace("\n", "\t").split("\t"):
            if ":" in part:
                k, v = part.split(":", 1)
                out[k.strip()] = v.strip()
        return out

    # -- session ----------------------------------------------------------

    def open(self, bitrate):
        """Set the bitrate and go on the bus.

        The bitrate can only be set while the channel is CLOSED. That is also
        true of the retransmission and silent-mode commands -- this firmware
        answers \\a if you try them while open, which is better than the silent
        no-op some other firmwares do, but you still have to get the order
        right.
        """
        if self.is_open:
            raise SlcanError("already open -- close() before changing bitrate")
        if bitrate not in BITRATES:
            raise SlcanError(
                "no single-digit code for %d bit/s on this firmware; "
                "use an explicit bit timing (lowercase 's') instead" % bitrate)
        self._close_quietly()
        self._cmd(BITRATES[bitrate])
        self._cmd("O")
        self.is_open = True

    def _close_quietly(self):
        """Make sure the channel is closed before setting the bitrate.

        C answers nothing at all on this firmware (see _cmd), so there is
        nothing to wait for and nothing here that can fail.
        """
        self._cmd("C", expect_reply=False)

    def close(self):
        if self.is_open:
            self._cmd("C", expect_reply=False)
            self.is_open = False
        self.ser.close()

    # -- traffic ----------------------------------------------------------

    def send(self, can_id, data, extended=False):
        """Send one classic CAN frame (up to 8 bytes)."""
        if len(data) > 8:
            raise SlcanError("classic CAN carries at most 8 bytes; "
                             "use CAN FD (see canfd.md) for more")
        if extended:
            frame = "T%08X%d" % (can_id, len(data))
        else:
            frame = "t%03X%d" % (can_id, len(data))
        frame += "".join("%02X" % b for b in data)
        self._cmd(frame)

    def recv(self, timeout=1.0):
        """Return (can_id, data, extended) or None on timeout.

        Frames arrive as text terminated by \\r, interleaved with nothing else
        as long as MD/ME/MF are left off (they are, by default).
        """
        deadline = time.time() + timeout
        while time.time() < deadline:
            ch = self.ser.read(1)
            if not ch:
                continue
            if ch in (OK, ERR):
                line, self._rx = self._rx, b""
                parsed = _parse_frame(line.decode("ascii", "replace"))
                if parsed:
                    return parsed
                continue
            self._rx += ch
        return None


def _parse_frame(line):
    if len(line) < 5 or line[0] not in "tTrR":
        return None
    extended = line[0] in "TR"
    remote = line[0] in "rR"
    idlen = 8 if extended else 3
    try:
        can_id = int(line[1:1 + idlen], 16)
        dlc = int(line[1 + idlen], 16)
    except ValueError:
        return None
    body = line[2 + idlen:]
    if remote:
        return can_id, b"", extended
    data = bytes(int(body[i:i + 2], 16) for i in range(0, min(len(body), dlc * 2), 2))
    return can_id, data, extended


def find_port():
    """Pick a likely SH-C31B. Never silently grabs 'the first serial port'."""
    candidates = []
    for p in list_ports.comports():
        # 16D0:117E is the slcan firmware's USB id. Other adapters use it too,
        # so this narrows the search -- it does not prove what you have. The V
        # command below is what actually confirms it.
        if (p.vid, p.pid) == (0x16D0, 0x117E):
            candidates.append(p.device)
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        print("No 16D0:117E serial port found.")
        print("If you see a CAN network device instead, you have an SH-C31A")
        print("(gs_usb firmware) -- see ../../SH-C31A/examples/ .")
    else:
        print("More than one candidate: %s" % ", ".join(candidates))
        print("Pass the one you want on the command line.")
    return None


def main():
    port = sys.argv[1] if len(sys.argv) > 1 else find_port()
    if not port:
        return 2

    dev = Adapter(port)
    try:
        info = dev.identify()
        print("-- adapter --")
        for k in ("Board", "MCU", "DevID", "Firmware", "Slcan",
                  "Clock", "Channels", "Quartz", "Serial"):
            if k in info:
                print("   %-9s %s" % (k + ":", info[k]))
        print()
        print("   NOTE: 'Board' and 'MCU' are compile-time strings, not hardware")
        print("         readings. Do not use them to recognise the product.")
        if info.get("Clock") and info["Clock"] != "160":
            print("   WARNING: expected Clock: 160, got %r" % info["Clock"])

        print("\n-- opening at 500 kbit/s --")
        dev.open(500_000)

        print("-- sending one frame --")
        dev.send(0x123, bytes([0xDE, 0xAD, 0xBE, 0xEF]))
        print("   sent 123#DEADBEEF")

        print("\n-- listening for 5 s (Ctrl-C to stop) --")
        end = time.time() + 5
        seen = 0
        while time.time() < end:
            frame = dev.recv(timeout=0.5)
            if frame:
                can_id, data, ext = frame
                seen += 1
                print("   %s %0*X  [%d]  %s"
                      % ("ext" if ext else "std", 8 if ext else 3, can_id,
                         len(data), " ".join("%02X" % b for b in data)))
        if not seen:
            print("   nothing received.")
            print("   If the bus is live, check the bitrate matches: a mismatch")
            print("   produces silence, not an error.")
    except SlcanError as e:
        print("error: %s" % e)
        return 1
    except KeyboardInterrupt:
        pass
    finally:
        dev.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
