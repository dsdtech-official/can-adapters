<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C31B — Hardware

**The design files are published under the [SH-C31A](../../SH-C31A/hardware/), board
revision V1.1.** They are not duplicated here.

**The SH-C31B is that board.** Same schematic, same layout, same bill of materials — the
SH-C31B is the same hardware shipped with different firmware in it. There is one design, so
there is one set of design files, and copying them under a second name would only create two
things to keep in step.

## Where to get them

| File | |
|---|---|
| [`SH-C31A-V1.1.epro2`](../../SH-C31A/hardware/) | JLC EDA project — **take this one if you intend to change the board** |
| [`SH-C31A-V1.1.pdf`](../../SH-C31A/hardware/) | Schematic, for reading without an EDA tool |
| [`SH-C31A-V1.1.SchDoc`](../../SH-C31A/hardware/) | Schematic, Protel ASCII export |
| [`SH-C31A-V1.1.PcbDoc`](../../SH-C31A/hardware/) | Board layout, Protel ASCII export |

Full notes on the formats, the substitute parts actually fitted in production, and the
terminal pinout are on the [SH-C31A hardware page](../../SH-C31A/hardware/).

**Fabrication bundles (Gerbers, drill files) are attached to
[Releases](../../../../releases)**, not stored here.

## What is on the board

| | |
|---|---|
| Bus lines | A resettable fuse in series with each (`F2` on CAN_H, `F3` on CAN_L), a TVS to ground on each (`TV1`, `TV2`), and `D1` across the pair |
| USB side | `F1` |
| Terminal | 3.81 mm 3-pin, right-angle — `1 = CAN_L` · `2 = GND` · `3 = CAN_H` |
| Switch | Two positions: **BOOT** (holds the MCU in its USB bootloader) and **120 Ω termination**. When to switch it off → [`docs/termination.md`](../../docs/termination.md) |
| Clock | No crystal is fitted. The MCU runs from its internal oscillator |

## Licence

**CERN-OHL-S-2.0**, the same as the files themselves. See [LICENSES/](../../LICENSES/).

**No warranty.** Provided AS IS.
