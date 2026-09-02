<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C30G

**Galvanically isolated** USB to CAN adapter. The isolated sibling of the
[SH-C30A](../SH-C30A/) — same microcontroller, same firmware, with the CAN side cut loose
from the USB side. Part of the **CANable** family: lineage and attribution in
[`THIRD-PARTY-NOTICES.md`](../THIRD-PARTY-NOTICES.md).

> **Buy:** <https://www.deshide.com>

| | |
|---|---|
| MCU | **STM32F072C8T6** — Cortex-M0 with a classic bxCAN peripheral |
| Transceiver | **SIT1040T** — 1 Mbit/s |
| **Isolation** | ✅ **ADuM3201 digital isolator + B0505S-1WR3 isolated DC-DC.** Signal *and* power are isolated |
| CAN FD | ❌ **Not supported, and reflashing cannot add it** — bxCAN is not FDCAN |
| Classic CAN | CAN 2.0A and 2.0B, up to 1 Mbit/s |
| Clock | 24 MHz crystal on the board |
| USB | USB 2.0 Full Speed, **Type-B receptacle** (cable not captive) |
| CAN | **4-pin 5.08 mm screw terminal** — CAN_L / CAN_H / GND / +5 V |
| Board | 53.5 × 36.0 mm |

## The isolated side powers itself

**You do not need an external supply.** The on-board DC-DC converter makes the isolated
5 V from USB, and the transceiver runs from it. Pin 4 of the terminal carries that isolated
5 V, so it can also feed a small load on the bus side — it is an output, not an input.

## Start here

1. **[Manual](manual/)** — wiring, LEDs, first connection
2. **Check the 120 Ω terminator.** Switch it **off** when the bus already has two, which a
   vehicle bus does → [`docs/termination.md`](../docs/termination.md)
3. **The green LEDs stay dark until software opens the channel.** That is normal →
   [`docs/leds.md`](../docs/leds.md)
4. **[Examples](examples/)** — read the bus, send a frame

## In this folder

| | |
|---|---|
| [`manual/`](manual/) | User manual |
| [`datasheet/`](datasheet/) | Electrical and mechanical specifications |
| [`hardware/`](hardware/) | Schematic and board files |
| [`firmware/`](firmware/) | What it runs and how to change it |
| [`examples/`](examples/) | Working code |

Firmware images are attached to [Releases](../../../releases), not stored in this folder.

## Licence

Hardware design files: **CERN-OHL-S-2.0** · Documentation: **CC-BY-SA-4.0** ·
Example code: **BSD-3-Clause** · Firmware images: **MIT**. See [LICENSES/](../LICENSES/).

**No warranty.** Provided AS IS.
