<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C30L — Hardware

Schematic and board files for the SH-C30L, board revision **V1.0**.

## Files

| File | What it is |
|---|---|
| `SH-C30L-V1.0.SchDoc` | Schematic |
| `SH-C30L-V1.0.PcbDoc` | Board layout |
| `SH-C30L-V1.0.pdf` | Schematic, printable |
| `SH-C30L-V1.0.epro2` | The EDA project the two above came from |

Both `.SchDoc` and `.PcbDoc` are **Protel ASCII** — plain text, so they diff and review like
source. Altium Designer opens them directly. Other EDA tools' Altium importers mostly target
the *binary* variant; we have not tested them against these ASCII files.

## What differs from the SH-C30A

One thing, and it is mechanical rather than electrical.

| | SH-C30A | **SH-C30L** |
|---|---|---|
| USB | `USB1`, a soldered USB-A plug on the board | **`J1`, four pads** — the cable's VBUS / D− / D+ / GND solder here, and the plug is at the far end of the lead |
| Board | 68.9 × 24.4 mm | **49.6 × 24.4 mm** |

Everything else is the same part-for-part: STM32F072C8T6, a TJA1040-family transceiver, the
24 MHz crystal, the same protection and the same 3.81 mm terminal. The firmware does not
know the difference — **one build serves SH-C30A, SH-C30G and SH-C30L**.

## Terminal block (P1)

| Pin | Net | |
|---|---|---|
| 1 | CAN_H | through resettable fuse **F1** |
| 2 | GND | |
| 3 | CAN_L | through resettable fuse **F2** |

## Protection on the bus lines

Each CAN line has a **resettable fuse in series** (F1, F2) and a **TVS to ground** (TV1,
TV2), with **D1** across the pair. **F3** protects the USB side.

## Switch (SW1)

Two positions: **BOOT** (holds the MCU in its USB bootloader) and **120 Ω termination**,
which connects the terminator across the bus. When to switch it off →
[`docs/termination.md`](../../docs/termination.md)

## Which board this matches

The bottom silkscreen reads `SH-C30L`, `Made By DSD TECH` and **`V1-20241115`**.

## Attribution and notice of modification

This board is part of the **CANable** family and shares its microcontroller and basic
architecture with **candleLight** by **Hubert Denkmair**, published under the **CERN Open
Hardware Licence v1.2**. The files here are an independent DSD TECH layout, not an edited
copy of the candleLight files.

**Full attribution and the licence chain:**
[`THIRD-PARTY-NOTICES.md`](../../THIRD-PARTY-NOTICES.md)

## Licence

Hardware design files: **CERN-OHL-S-2.0** — see [`LICENSE.md`](../../LICENSE.md).
This is permitted by CERN OHL v1.2 §3.4(e), which allows a later CERN version.

**No warranty.** Provided AS IS.
