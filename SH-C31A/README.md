<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C31A

USB to **CAN FD** adapter. Non-isolated. Part of the **CANable** family of adapters —
lineage and attribution: [`THIRD-PARTY-NOTICES.md`](../THIRD-PARTY-NOTICES.md).

> **Buy:** <https://www.deshide.com/product-details_SH-C31A.html> ·
> **Isolated version:** [SH-C31G](https://www.deshide.com/product-details_SH-C31G.html)

| | |
|---|---|
| MCU | **STM32G431** — 170 MHz Cortex-M4F, FDCAN. Both the **C8T6** (64 KB flash) and the **CBT6** (128 KB) are fitted in production; the firmware is the same either way |
| Transceiver | SIT1051T |
| **CAN FD** | ✅ **Working out of the box.** Measured to **5 Mbit/s** data rate — see [`firmware/`](firmware/) |
| Classic CAN | CAN 2.0A and 2.0B |
| Isolation | **None** |
| Clock | No external crystal — the MCU runs from its internal oscillator |
| USB | USB 2.0 Full Speed, USB-A plug |
| CAN | 3.81 mm 3-pin terminal, right-angle — CAN_H / CAN_L / GND |

> ⚠️ **One limit is your software, not this adapter.** Over SocketCAN every standard
> nominal rate works, 10 kbit/s through 1 Mbit/s. `python-can`'s `gs_usb` backend can only
> open 500 kbit/s and 1 Mbit/s — that is a restriction inside that library.
> [`firmware/`](firmware/) has the measurements.

## Start here

1. **[Manual](manual/)** — wiring, LEDs, first connection
2. **Check the 120 Ω terminator.** Switch it **off** when the bus already has two, which a
   vehicle bus does → [`docs/termination.md`](../docs/termination.md)
3. **The green LEDs stay dark until software opens the channel.** That is normal →
   [`docs/leds.md`](../docs/leds.md)
4. **[Examples](examples/)** — read the bus, send a frame, send an FD frame

## In this folder

| | |
|---|---|
| [`manual/`](manual/) | User manual |
| [`datasheet/`](datasheet/) | Electrical and mechanical specifications |
| [`hardware/`](hardware/) | Schematic and board files |
| [`firmware/`](firmware/) | What it runs, what that firmware can do, and how to change it |
| [`examples/`](examples/) | Working code |

Firmware images and fabrication bundles are attached to
[Releases](../../../releases), not stored in this folder.

## Licence

Hardware design files: **CERN-OHL-S-2.0** · Documentation: **CC-BY-SA-4.0** ·
Example code: **BSD-3-Clause** · Firmware images: **MIT**. See [LICENSES/](../LICENSES/).

**No warranty.** Provided AS IS.
