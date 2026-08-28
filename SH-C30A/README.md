<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C30A

USB to **CAN 2.0** adapter. Non-isolated. Part of the **CANable** family of adapters —
lineage and attribution: [`THIRD-PARTY-NOTICES.md`](../THIRD-PARTY-NOTICES.md).

> **Buy:** <https://www.amazon.com/dp/B0BQ5G3KLR>
> Also stocked on Amazon in the **UK, Europe, Japan and Australia** — search the
> model number on your local site. Product page:
> <https://www.deshide.com/product-details_SH-C30A.html>

| | |
|---|---|
| MCU | STM32F072C8T6 — Cortex-M0, 64 KB flash, bxCAN |
| Transceiver | NXP TJA1040T |
| CAN FD | **Not supported** — the silicon has no CAN FD. See [SH-C31A](../SH-C31A/) |
| Isolation | **None** |
| Clock | 24 MHz crystal on board |
| USB | USB 2.0 Full Speed, USB-A plug |
| CAN | 3.81 mm terminal — CAN_H / CAN_L / GND |

## Start here

1. **[Manual](manual/)** — wiring, LEDs, first connection
2. **Check the 120 Ω terminator.** Switch it **off** when the bus already has two, which a
   vehicle bus does → [`docs/termination.md`](../docs/termination.md)
3. **Find out which firmware you have** → [`docs/identify-firmware.md`](../docs/identify-firmware.md)
4. **[Examples](examples/)** — read the bus, send a frame

## In this folder

| | |
|---|---|
| [`manual/`](manual/) | User manual |
| [`datasheet/`](datasheet/) | Electrical and mechanical specifications |
| [`hardware/`](hardware/) | Schematic, BOM, board files |
| [`firmware/`](firmware/) | Which firmware it runs and how to change it |
| [`examples/`](examples/) | Working code |

Firmware images and fabrication bundles are attached to
[Releases](../../../releases), not stored in this folder.

## Licence

Hardware design files: **CERN-OHL-S-2.0** · Documentation: **CC-BY-SA-4.0** ·
Example code: **BSD-3-Clause** · Firmware images: **MIT**. See [LICENSES/](../LICENSES/).

This board descends from the **CANable** family and shares its microcontroller and basic
architecture with **candleLight** by Hubert Denkmair (**CERN-OHL-1.2**). Attribution, the
licence chain and what we changed:
[`THIRD-PARTY-NOTICES.md`](../THIRD-PARTY-NOTICES.md).

**No warranty.** Provided AS IS.
