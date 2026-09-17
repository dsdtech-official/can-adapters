<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# ElmueSoft Slcan 2.5 on the SH-C31A, SH-C31B and SH-C31G

Third-party firmware by **ElmueSoft**. Licence, download, thanks and support boundaries are
on [`other-firmware.md`](other-firmware.md) — **read that first**. This page is what this
firmware does on the bench.

> **Two ways you can be reading this.** On the **[SH-C31B](../SH-C31B/)** this firmware is
> what the adapter **ships with** — you did not flash it, it arrived that way, and
> "going back" below means moving to our own build for the first time. On the
> **[SH-C31A](../SH-C31A/)** and **[SH-C31G](../SH-C31G/)** it is something you chose to
> flash over ours. **Everything else on this page is the same either way** — it is the same
> image on the same microcontroller.

**File:** `STM32G431-Slcan2.5-Multiboard.dfu` · 38 071 bytes ·
`sha256 8d958470…65555a`

> 🔴 **This is a snapshot of commit `eb1c7e35` (2026-09-15), not the latest build.**
> Elmue's own pages always have the current one — see
> [`other-firmware.md`](other-firmware.md#download), which also lists what changed since our
> previous snapshot.

Everything below was read off one of our own boards, not from a datasheet.
> ℹ️ **Which build these readings came from:** commit `e862f6a6`, the snapshot this page
> carried until 2026-09-17. They have not been repeated on the current build. Nothing here
> is expected to have moved, but we have not re-read it, so we say so.
**The board was an SH-C31A.** The **SH-C31B is that same board**, so these readings were
taken on SH-C31B hardware. The SH-C31G is the same microcontroller running the same image,
but we have not repeated these readings on one.

## What changes: it becomes a serial port

| | Our `v1.4` | **Slcan 2.5** |
|---|---|---|
| Host interface | raw USB, `gs_usb` / WinUSB | **CDC virtual serial port** |
| VID:PID | `1D50:606F` | **`16D0:117E`** |
| `bcdDevice` | `REV_0200` — ours, fixed | ⚠️ **carries his build version and moves every release — ⛔ do not identify by it** |
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
crystal is in use, and the bit-timing limits. **Use it to confirm what is actually on the
board before you trust anything else.**

Ours reported: `MCU: STM32G431` · `DevID: 0x468` · `160 MHz` · `Channels: 1` ·
`Quartz: No`.

## 🔴 Three numbers that are not what you would assume

**① The CAN clock is 160 MHz, not the 170 MHz our firmware uses.**

Bit timing is derived from that clock. Software that **asks the device for its clock** and
computes the prescaler and segments from the answer is fine — that is what correct software
does. Software that **assumes a fixed clock** is not: it programs timings computed for one
clock onto a device running another, and the result is not a slightly different rate. It is
a **wrong rate and a wrong sample point, and the controller goes bus-off as soon as it sees
traffic.** It does not degrade gracefully.

⇒ **If a tool asks you to enter the clock by hand, enter 160 MHz.** Otherwise read the
rate back after bringing the interface up.

**② `S7` is 800 kbit/s here — and no standard says what it ought to be.**

We measured 800 kbit/s. **There is no single "classic slcan table"** — every firmware
picked its own:

| `S7` = **800 k** | `S7` = **750 k** |
|---|---|
| the original LAWICEL specification · the **Linux kernel** (`slcan_bitrate_const[]`) · USBtin · WeActStudio | **CANable's own firmware 1.0 / 2.0**, and `python-can` following it |

⇒ ⚠️ **What this means for you in practice:** `python-can`'s slcan interface follows the
CANable convention and treats `S7` as 750 k. **Point it at this firmware and the bus runs at
800 k while your script believes it set 750 k** — and nothing reports an error. The same
applies to any script or tool carrying its own table.

**Neither value is wrong; they are two conventions.** For a rate that has to be exact, set
the bit timing explicitly rather than by index.

**③ The sample point is 75.0 %, not the 87.5 % an older reading of the source suggests.**

We measured 75.0 %. **Upstream has confirmed this is deliberate:** the sample point was
changed from 87.5 % to 75 % in November 2025 because 75 % tested as more robust, and only
the source-code comments were left behind. They are being corrected upstream.

⚠️ **Sample points still matter more than they look.** A mismatched arbitration sample point
between two nodes can make CAN FD fail **in one direction only**, which presents as a
hard-to-diagnose partial failure rather than a clean error. **If you put this firmware on a
bus with other nodes, check that the sample points agree.**

## Crystal

`V` reports `Quartz: No`, which is correct: **none of the SH-C31A, SH-C31B or SH-C31G has
a crystal fitted.** The MCU runs from its internal oscillator.

⛔ **Do not flash a variant built for a 25 MHz crystal onto these boards.** Upstream ships
several G431 slcan variants and they self-report differently — `V` will tell you
immediately if you took the wrong one. The `Multiboard` build named at the top of this page
is the one for hardware without a crystal.

## Moving to our own firmware

Same DFU procedure either way, and the bootloader is in ROM and is never overwritten →
[`other-firmware.md`](other-firmware.md#flashing)

On an **SH-C31A** or **SH-C31G** this puts back the build the adapter came with. On an
**SH-C31B** it replaces the build it came with — the images are on the
[SH-C31A firmware page](../SH-C31A/firmware/#download), and they fit all three boards.

⚠️ Afterwards the adapter reports `1D50:606F` and **stops being a COM port**. Any script
or udev rule keyed to `16D0:117E` will stop matching.
