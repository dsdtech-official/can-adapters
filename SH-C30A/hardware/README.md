<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C30A — Hardware

Schematic and board files for the SH-C30A, board revision **V1.21**.

## Files

| File | What it is |
|---|---|
| `SH-C30A-V1.21.SchDoc` | Schematic |
| `SH-C30A-V1.21.PcbDoc` | Board layout |

Both are **Protel ASCII** (`Protel for Windows – Schematic Capture Ascii File Version 5.0`
and `Protel_Advanced_PCB VERSION=5.01`) — plain text, so they diff and review like source.
Altium Designer opens them directly. Other EDA tools' Altium importers mostly target the
*binary* `.SchDoc` / `.PcbDoc` variant; we have not tested them against these ASCII files.

**Fabrication bundles (Gerbers, drill files) are attached to
[Releases](../../../../releases)**, not stored here — they are generated from the files
above and would otherwise sit in git history for good.

## Which board this matches

The bottom silkscreen reads `SH-C30A`, `Based on Canable` and **`V1-20230506`**. The
schematic was created 2022-06-27 and last updated 2022-07-10; the board revision is dated
2023-05-06.

## Substitute parts

The schematic records the part chosen at design time. Production sourcing has since moved
on in one place:

| Position | Schematic | **In production** |
|---|---|---|
| X1 — 24 MHz crystal | `SX32Y024000BC1T` (TKD), 3225, CL 12 pF | **`7V24000005 / SMD3225-4P` (TXC)** |

Same package and frequency. We have deliberately **not** rewritten the 2022 schematic to
say something it did not say at the time.

## Attribution and notice of modification

This board is part of the **CANable** family and shares its microcontroller and basic
architecture with **candleLight** by **Hubert Denkmair**, published under the
**CERN Open Hardware Licence v1.2**. The files here are an independent DSD TECH layout, not
an edited copy of the candleLight files.

**The full attribution, the licence chain and a verified list of what differs from
candleLight are in [`THIRD-PARTY-NOTICES.md`](../../THIRD-PARTY-NOTICES.md).**

## Licence

Hardware design files: **CERN-OHL-S-2.0** — see [`LICENSE.md`](../../LICENSE.md).
This is permitted by CERN OHL v1.2 §3.4(e), which allows a later CERN version.

**No warranty.** Provided AS IS.
