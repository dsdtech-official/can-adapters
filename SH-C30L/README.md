<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C30L

USB to CAN adapter **on a lead**. Electrically the [SH-C30A](../SH-C30A/) — same
microcontroller, same transceiver family, same firmware — but the USB-A plug sits at the
end of a captive cable instead of on the board, which makes the board 19 mm shorter. Part
of the **CANable** family: lineage and attribution in
[`THIRD-PARTY-NOTICES.md`](../THIRD-PARTY-NOTICES.md).

> **Buy:** <https://www.deshide.com>

| | |
|---|---|
| MCU | **STM32F072C8T6** — Cortex-M0 with a classic bxCAN peripheral |
| Transceiver | **TJA1040T/CM** |
| CAN FD | ❌ **Not supported, and reflashing cannot add it** — bxCAN is not FDCAN |
| Classic CAN | CAN 2.0A and 2.0B, up to 1 Mbit/s |
| Isolation | **None** |
| Clock | 24 MHz crystal on the board |
| USB | USB 2.0 Full Speed, **USB-A plug on a captive lead** — the cable solders to four pads on the board |
| CAN | **3-pin 3.81 mm pluggable terminal** — CAN_H / GND / CAN_L |
| Board | 49.6 × 24.4 mm |

## Same firmware as the SH-C30A

One build covers **SH-C30A, SH-C30G and SH-C30L**. Everything the
[SH-C30A firmware page](../SH-C30A/firmware/) says applies here — see
[`firmware/`](firmware/) for the short form.

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
