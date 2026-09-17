<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C31B

USB to **CAN FD** adapter that presents itself as an ordinary **serial port**.
Non-isolated. Part of the **CANable** family of adapters — lineage and attribution:
[`THIRD-PARTY-NOTICES.md`](../THIRD-PARTY-NOTICES.md).

> **The board is an [SH-C31A](../SH-C31A/).** Same microcontroller, same transceiver, same
> protection, same design files. **What differs is the firmware fitted at the factory**,
> and that changes how the adapter appears to your computer.

> 🔴 **The board is silkscreened `SH-C31A`, and that is correct.** There is one board, and
> it carries one part number. Nothing printed on it says SH-C31B, because what makes it an
> SH-C31B is the firmware inside.
>
> **The enclosure is how you tell the two apart on a shelf: the SH-C31B is grey, the
> [SH-C31A](../SH-C31A/) is clear.** But the enclosure says which one was *sold* — to know
> which firmware is *on it right now*, plug it in. An SH-C31B comes up as a **serial port**
> (a COM port on Windows, `/dev/ttyACM*` on Linux). See [`firmware/`](firmware/).

| | |
|---|---|
| MCU | **STM32G431** — 170 MHz Cortex-M4F, FDCAN. Both the **C8T6** (64 KB flash) and the **CBT6** (128 KB) are fitted in production |
| Transceiver | SIT1051T |
| **Factory firmware** | **ElmueSoft Slcan 2.5**, `Multiboard` build — third-party work, MIT licence |
| **Host interface** | **CDC virtual serial port** — a COM port on Windows, `/dev/ttyACM*` on Linux |
| **CAN FD** | ✅ **Working out of the box**, at data rates up to **5 Mbit/s** |
| Classic CAN | CAN 2.0A and 2.0B |
| Isolation | **None** |
| Clock | No external crystal — the MCU runs from its internal oscillator |
| USB | USB 2.0 Full Speed, USB-A plug |
| CAN | 3.81 mm 3-pin terminal, right-angle — `1 = CAN_L` · `2 = GND` · `3 = CAN_H` |
| Board | 68.9 × 24.4 mm |

> ⭐ **Nothing to install on Windows.** It enumerates as a standard USB serial device.
> **⛔ Do not run Zadig against it** — that applies to every adapter here.

## How it differs from the SH-C31A and SH-C31G

The three boards share a microcontroller and a firmware family. **Read the two halves of
this table separately: the top half is hardware, the bottom half is the firmware fitted at
the factory** — and the firmware can be changed on any of them.

### Hardware

| | **SH-C31A** | **SH-C31B** | **SH-C31G** |
|---|---|---|---|
| MCU | STM32G431, C8T6 + CBT6 | **← identical** | STM32G431, C8T6 + CBT6 |
| Transceiver | `SIT1051T` | **← identical** | `TJA1051T/3` (NXP) |
| Isolation | none | **← identical** | ✅ **digital isolator + isolated DC-DC** — signal *and* power |
| Crystal | none, internal oscillator | **← identical** | none, internal oscillator |
| USB connector | USB-A plug on the board | **← identical** | Type-B receptacle |
| CAN connector | 3.81 mm **3-pin**, right-angle | **← identical** | 5.08 mm **4-pin** screw terminal |
| CAN pinout | `1 = CAN_L` · `2 = GND` · `3 = CAN_H` | **← identical** | `CAN_L` · `CAN_H` · **GND-CAN** · **VDD-CAN (isolated 5 V out)** |
| Board | 68.9 × 24.4 mm | **← identical** | 53.5 × 36.0 mm |
| Termination | 120 Ω switch on the board | **← identical** | 120 Ω switch on the board |
| Bus-line protection | resettable fuse on each line (`F2`, `F3`), TVS to ground (`TV1`, `TV2`), `D1` across the pair, `F1` on the USB side | **← identical** | same arrangement, TVS to the **isolated** ground |
| Design files | [`SH-C31A/hardware/`](../SH-C31A/hardware/) | **the same files** — see [`hardware/`](hardware/) | [`SH-C31G/hardware/`](../SH-C31G/hardware/) |

> **The SH-C31A column and the SH-C31B column are the same board.** There is one design,
> and it is published once, under the SH-C31A.

### Firmware fitted at the factory

| | **SH-C31A** | **SH-C31B** | **SH-C31G** |
|---|---|---|---|
| Build | our own gs_usb build, `v1.4` | **ElmueSoft Slcan 2.5**, `Multiboard` | our own gs_usb build, `v1.4` |
| Written by | **us** | **a third party** — ElmueSoft, MIT licence | **us** |
| Host interface | raw USB (gs_usb / WinUSB) | **CDC virtual serial port** | raw USB (gs_usb / WinUSB) |
| USB `VID:PID` | `1D50:606F` | **`16D0:117E`** | `1D50:606F` |
| Product string | `SH-C31x` | **`Slcan 2.5 - Multiboard`** | `SH-C31x` |
| Wire protocol | gs_usb | **slcan `1.05`** | gs_usb |
| CAN clock | 170 MHz | **160 MHz** | 170 MHz |
| Windows | no driver to install — WinUSB binds itself | no driver to install — **it is a COM port** | no driver to install — WinUSB binds itself |
| Linux | kernel `gs_usb` → SocketCAN | **`slcand`** → SocketCAN, or any serial tool | kernel `gs_usb` → SocketCAN |
| CAN FD | ✅ | ✅ | ✅ |
| `python-can` backend | `gs_usb` — ⚠️ that library opens only 500 kbit/s and 1 Mbit/s | `slcan` — ⚠️ **it assumes `S7` = 750 k; this firmware uses 800 k** | `gs_usb` — same library limit |
| Software-switchable termination | not supported — use the switch | not supported — use the switch | not supported — use the switch |
| Who supports the firmware | **us** | **the author**, for the firmware itself — see below | **us** |
| Details | [`SH-C31A/firmware/`](../SH-C31A/firmware/) | [`docs/elmue-slcan-2.5.md`](../docs/elmue-slcan-2.5.md) | [`SH-C31G/firmware/`](../SH-C31G/firmware/) |

### Which one do I want?

| If | Take |
|---|---|
| Your software wants a **serial port**, or you would rather not deal with WinUSB at all | **SH-C31B** |
| You work on **Linux with SocketCAN**, or use cangaroo, `can-utils`, `python-can` over gs_usb | **SH-C31A** |
| Your CAN side must be **electrically separated** from the PC | **SH-C31G** |

> **All three can be reflashed either way, free, over USB.** The bootloader lives in ROM
> and cannot be erased, so an adapter bought as one can be made into the other →
> [`docs/other-firmware.md`](../docs/other-firmware.md)

## Before you put it on a bus you care about

1. **Check the 120 Ω terminator.** Switch it **off** when the bus already has two, which a
   vehicle bus does → [`docs/termination.md`](../docs/termination.md)
2. 🔴 **`S7` is 800 kbit/s on this firmware**, not the 750 kbit/s some tools assume. Nothing
   reports an error — the bus simply runs at a rate your script did not intend. For a rate
   that has to be exact, set the bit timing explicitly →
   [`docs/elmue-slcan-2.5.md`](../docs/elmue-slcan-2.5.md)
3. 🔴 **The CAN clock is 160 MHz.** Software that asks the device for its clock is fine.
   Software that assumes a fixed value programs the wrong timings and goes bus-off as soon
   as it sees traffic — it does not degrade into "a slightly different rate".
4. **Send `V` to confirm what you have.** One command reports the board, the MCU, the
   firmware version, the CAN clock and the bit-timing limits.
5. **The green LEDs stay dark until software opens the channel.** That is normal →
   [`docs/leds.md`](../docs/leds.md)

## Third-party firmware, and where support goes

The Slcan 2.5 build this adapter ships with is **the work of ElmueSoft**, published under
the **MIT licence**. We ship it, we mirror it, and we credit it — we did not write it.

| | |
|---|---|
| The **hardware**, and our own firmware | **us** — permanent support, 1-year replacement |
| **Bugs in the Slcan 2.5 firmware itself** | the author → [`docs/other-firmware.md`](../docs/other-firmware.md) |
| Going back to our own gs_usb build | [`docs/other-firmware.md`](../docs/other-firmware.md) |

## In this folder

| | |
|---|---|
| [`manual/`](manual/) | User manual |
| [`datasheet/`](datasheet/) | Electrical and mechanical specifications |
| [`hardware/`](hardware/) | Where the design files are, and why they live under the SH-C31A |

> **Firmware and examples for this model are not in this folder yet.** Until they land:
> the firmware is documented in [`docs/elmue-slcan-2.5.md`](../docs/elmue-slcan-2.5.md)
> and [`docs/other-firmware.md`](../docs/other-firmware.md), and
> [`docs/identify-firmware.md`](../docs/identify-firmware.md) covers telling builds apart.

Firmware images and fabrication bundles are attached to
[Releases](../../../releases), not stored in this folder.

## Licence

Hardware design files: **CERN-OHL-S-2.0** · Documentation: **CC-BY-SA-4.0** ·
Example code: **BSD-3-Clause** · Firmware images: **MIT**. See [LICENSES/](../LICENSES/).

**No warranty.** Provided AS IS.
