<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C31A — Hardware

Schematic and board files for the SH-C31A, board revision **V1.1**.

## Files

| File | What it is |
|---|---|
| `SH-C31A-V1.1.epro2` | JLC EDA project — the format the board is edited in |
| `SH-C31A-V1.1.pdf` | Schematic, for reading without an EDA tool |
| `SH-C31A-V1.1.SchDoc` | Schematic, Protel ASCII export |
| `SH-C31A-V1.1.PcbDoc` | Board layout, Protel ASCII export |

The `.epro2` is the one to take if you intend to **change** the board. The Protel ASCII
files are exports of it, and lossy ones — degree signs disappear on the way out — so read
them, do not treat them as the master.

**Fabrication bundles (Gerbers, drill files) are attached to
[Releases](../../../../releases)**, not stored here — they are generated from the files
above and would otherwise sit in git history for good.

## Substitute parts

The schematic records the part chosen at design time. Production sourcing has since moved
on in one place:

| Position | Schematic | **Fitted in production** |
|---|---|---|
| CAN transceiver | `TJA1051T/3` (NXP) | **`SIT1051T`** |

Pin- and function-compatible. We have deliberately **not** rewritten the schematic to say
something it did not say at the time.

## Licence

Hardware design files: **CERN-OHL-S-2.0** — see [`LICENSE.md`](../../LICENSE.md).

Attribution and the licence chain: [`THIRD-PARTY-NOTICES.md`](../../THIRD-PARTY-NOTICES.md).

**No warranty.** Provided AS IS.
