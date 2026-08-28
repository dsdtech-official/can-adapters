<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C31A — Examples

Both examples run on the firmware the adapter ships with. Nothing to reflash.

| Example | Platform | Classic CAN | CAN FD |
|---|---|---|---|
| [`linux-socketcan.md`](linux-socketcan.md) | Linux | ✅ | ✅ |
| [`python-gsusb.py`](python-gsusb.py) | Windows *(macOS untested)* | ✅ | — |

## Which one do I want

**On Linux, nothing needs installing.** The kernel claims the adapter and gives you a
SocketCAN interface — [`linux-socketcan.md`](linux-socketcan.md) is the whole story, and
Python there means `python-can` with `interface="socketcan"`.

**On Windows** there is no kernel CAN stack, so Python talks to the adapter through libusb.
That is what [`python-gsusb.py`](python-gsusb.py) does, and its header explains the one
install step Windows needs.

Reference for the interface's own arguments:
<https://python-can.readthedocs.io/en/stable/interfaces/gs_usb.html>

## CAN FD

**CAN FD works on the firmware this adapter ships with** — no second firmware, no serial
port. Measured to **5 Mbit/s**, the transceiver's ceiling.
[`../firmware/`](../firmware/) has the full rate table.

**Use Linux for it.** We have exercised CAN FD over SocketCAN, and only there. The Windows
route above carries classic CAN.

> 🔴 **Read the rate back after setting it.** `ip link set ... up` exits `0` even when the
> divisors could not reach the rate you asked for — a 4 Mbit/s request lands on 3 953 488
> without a word of complaint. See [`linux-socketcan.md`](linux-socketcan.md).
