<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C31B — Firmware

## What this board ships with

**ElmueSoft Slcan 2.5**, the `Multiboard` build — **third-party firmware**, published by
its author under the **MIT licence**. It is already installed. Nothing to flash.

This is the one thing that makes an SH-C31B an SH-C31B: the hardware is an
[SH-C31A](../../SH-C31A/), and the SH-C31A leaves the factory with **our own** gs_usb build
instead.

> **What it does to the adapter:** it becomes a **CDC virtual serial port** — a COM port on
> Windows, `/dev/ttyACM*` on Linux — instead of a raw USB device. Nothing to install on
> Windows, and **⛔ do not run Zadig against it.**

## Confirm what you have

The board is silkscreened `SH-C31A`, so the print on it will not tell you. Plug it in:

| You see | You have |
|---|---|
| A **serial port** — `COM<n>` under *Ports*, or `/dev/ttyACM<n>` | **SH-C31B** — this firmware |
| A raw USB device under *Universal Serial Bus devices*, or a SocketCAN `can0` | an **SH-C31A** — our gs_usb build |

For certainty, send `V` and read the reply. **One command reports the board, the MCU, the
firmware version, the CAN clock, whether a crystal is in use, and the bit-timing limits.**
How to send it, and how to read the answer:
[`docs/identify-firmware.md`](../../docs/identify-firmware.md#confirming-the-slcan-version)

## The full description of this firmware

**It lives in one place, shared with the SH-C31A and SH-C31G**, because it is the same
image on all three:

| | |
|---|---|
| **[`docs/elmue-slcan-2.5.md`](../../docs/elmue-slcan-2.5.md)** | What it does on the bench — USB identity, the `V` command, the CAN clock, the sample point, the `S7` rate, the crystal |
| **[`docs/other-firmware.md`](../../docs/other-firmware.md)** | Licence, download, thanks, **support boundaries**, and the Candlelight 2.5 alternative |

**Read those two rather than a copy here.** This page would only drift out of step with them.

## Three things to know before a bus you care about

These are the same three on the shared page. They are repeated here because an SH-C31B
owner did not choose this firmware — it arrived in the box.

| | |
|---|---|
| 🔴 **`S7` is 800 kbit/s**, not 750 | Some tools — `python-can`'s slcan interface among them — assume 750 k for that index. **Nothing reports an error**; the bus simply runs at a rate your script did not intend. There is no standard value for `S7`; both conventions exist. For a rate that has to be exact, set the bit timing explicitly |
| 🔴 **The CAN clock is 160 MHz** | Software that asks the device for its clock is fine. Software that assumes a fixed value programs timings computed for a different clock and **goes bus-off as soon as it sees traffic** — it does not degrade into "a slightly different rate" |
| 🔴 **On a real CAN FD bus, do not set the rate by index** | The author's own manual is explicit: the single-index `S` and `Y` commands cannot select the correct sample point. They are fine between two adapters on your desk. On a live FD bus, calculate the prescaler and segments and use the lower-case `s` and `y` forms |

## Changing it

The bootloader is in ROM and is never overwritten, so this is not a one-way door.

| You want | Go to |
|---|---|
| **Our own gs_usb build**, the one an SH-C31A ships with | [SH-C31A firmware](../../SH-C31A/firmware/#download) — same DFU procedure |
| **A newer Slcan 2.5** than the one in the box | The author's pages always carry the current one → [`docs/other-firmware.md`](../../docs/other-firmware.md#download) |
| **Candlelight 2.5** — Elmue's gs_usb build, with his protocol extensions | [`docs/other-firmware.md`](../../docs/other-firmware.md) |

⚠️ **After flashing our build, the adapter stops being a COM port** and comes up as
`1D50:606F` instead. Any script or udev rule keyed to `16D0:117E` will stop matching.

## Where support goes

| | |
|---|---|
| The **hardware**, and **our own** firmware | **Us.** Permanent technical support, 1-year replacement |
| **Bugs in the Slcan 2.5 firmware itself** | **Its author.** We ship and mirror his work; we did not write it → [`docs/other-firmware.md`](../../docs/other-firmware.md) |

**The MIT licence notice ships with the product documentation**, and travels with the
images if you mirror them.

## Licence

This page: **CC-BY-SA-4.0**. The firmware image: **MIT**, © its author.
See [LICENSES/](../../LICENSES/) and
[`THIRD-PARTY-NOTICES.md`](../../THIRD-PARTY-NOTICES.md).

**No warranty.** Provided AS IS.
