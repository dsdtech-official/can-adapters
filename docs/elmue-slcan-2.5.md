<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# ElmueSoft Slcan 2.5 on the SH-C31A and SH-C31G

Third-party firmware by **ElmueSoft**. Licence, download, thanks and support boundaries are
on [`other-firmware.md`](other-firmware.md) — **read that first**. This page is what
changes on your bench once you have flashed it.

**File:** `STM32G431-Slcan2.5-Multiboard.dfu` · 38 219 bytes ·
`sha256 8fb57b07…43e7f59`

Everything below was read off one of our own boards, not from a datasheet.
**The board was an SH-C31A.** The SH-C31G is the same microcontroller running the same
image, but we have not repeated these readings on one.

## What changes: it becomes a serial port

| | Our `v1.4` | **Slcan 2.5** |
|---|---|---|
| Host interface | raw USB, `gs_usb` / WinUSB | **CDC virtual serial port** |
| VID:PID | `1D50:606F` | **`16D0:117E`** |
| `bcdDevice` | `REV_0200` | `REV_2608` |
| Product string | `SH-C31x` | `Slcan 2.5 - Multiboard` |
| Protocol | gs_usb | **slcan `1.05`** |

⭐ **On Windows it appears as a COM port with no driver installation** — no WinUSB, and
**no Zadig**. If your software wants a serial port, this is the build that gives it one.

On Linux it can be attached to SocketCAN with `slcand`, or driven directly as a serial
device by anything that speaks slcan.

⚠️ **The USB ID is completely different from the gs_usb build**, so unlike Candlelight 2.5
there is no risk of confusing the two — but any udev rule or script keyed to
`1D50:606F` will stop matching.

## `V` tells you everything

One command reports the board, the MCU, the firmware version, the CAN clock, whether a
crystal is in use, and the bit-timing limits. **Use it to confirm what you flashed before
you trust anything else.**

Ours reported: `MCU: STM32G431` · `DevID: 0x468` · `160 MHz` · `Channels: 1` ·
`Quartz: No`.

## 🔴 Three numbers that are not what you would assume

**① The CAN clock is 160 MHz, not the 170 MHz our firmware uses.**

Bit timing derives from it. A configuration that gives an exact rate on our build will not
necessarily give the same rate here, and a different set of rates lands exactly. **Read the
rate back after bringing the interface up.**

**② `S7` is 800 kbit/s, not 750 kbit/s.**

We measured it. In the classic slcan table `S7` is commonly 750 k, so **software that
assumes the standard table will set a different rate than it thinks it is setting.**

**③ The sample point is 75.0 %, not the 87.5 % you might expect.**

We measured 75.0 %. Note that **upstream's own header comment says 87.5 %**, which does not
match the constant the firmware actually uses — we are reporting what the device does.

⚠️ **This one matters more than it looks.** A mismatched arbitration sample point between
two nodes can make CAN FD fail **in one direction only**, which presents as a
hard-to-diagnose partial failure rather than a clean error. **If you put this firmware on a
bus with other nodes, check that the sample points agree.**

## Crystal

`V` reports `Quartz: No`, which is correct: **neither the SH-C31A nor the SH-C31G has a
crystal fitted.** The MCU runs from its internal oscillator.

⛔ **Do not flash a variant built for a 25 MHz crystal onto these boards.** Upstream ships
several G431 slcan variants and they self-report differently — `V` will tell you
immediately if you took the wrong one. The `Multiboard` build named at the top of this page
is the one for hardware without a crystal.

## Going back to our firmware

Same DFU procedure, and the bootloader is in ROM and is never overwritten →
[`other-firmware.md`](other-firmware.md#flashing)

⚠️ After flashing back, the adapter returns to `1D50:606F` and stops being a COM port.
