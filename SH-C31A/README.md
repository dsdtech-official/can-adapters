<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C31A

USB to **CAN FD** adapter. Non-isolated. Derived from the CANable 2.0 open-hardware design.

> **Isolated version:** [SH-C31G](https://www.deshide.com/product-details_SH-C31G.html) ·
> **Buy:** <https://www.deshide.com/product-details_SH-C31A.html>

| | |
|---|---|
| MCU | STM32G431C8T6 — 170 MHz Cortex-M4F, 64 KB flash, FDCAN |
| Transceiver | SIT1051T — pin- and function-compatible with the NXP TJA1051T/3 |
| CAN FD | **Supported by the hardware.** Not available on the firmware it ships with — see below |
| Isolation | **None** |
| Clock | No external crystal — the MCU runs from its internal oscillator |
| USB | USB 2.0 Full Speed, USB-A plug |
| CAN | 3.81 mm terminal — CAN_H / CAN_L / GND |

> ⚠️ **This adapter ships with the candlelight firmware, which has no CAN FD.** The
> hardware is CAN FD capable; reflashing to a **slcan** firmware is what turns that on.
> CAN 2.0A and 2.0B work at up to 1 Mbit/s either way. → [`firmware/`](firmware/)

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

## Credits

Derived from **CANable 2.0** by Openlight Labs / Eric Evenchick.

## Licence

Hardware design files: **CERN-OHL-S-2.0** · Documentation: **CC-BY-SA-4.0** ·
Example code: **BSD-3-Clause**. See [LICENSES/](../LICENSES/).

**No warranty.** Provided AS IS.
