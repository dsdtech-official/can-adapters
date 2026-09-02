<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C31G — Hardware

Schematic and board files for the SH-C31G, board revision **V1.0**.

## Files

| File | What it is |
|---|---|
| `SH-C31G-V1.0.SchDoc` | Schematic |
| `SH-C31G-V1.0.PcbDoc` | Board layout |
| `SH-C31G-V1.0.pdf` | Schematic, printable |
| `SH-C31G-V1.0.epro2` | The EDA project the two above came from |

Both `.SchDoc` and `.PcbDoc` are **Protel ASCII** — plain text, so they diff and review like
source. Altium Designer opens them directly. Other EDA tools' Altium importers mostly target
the *binary* variant; we have not tested them against these ASCII files.

## How the isolation is built

| Part | Job |
|---|---|
| **U4 — ADuM3201ARZ** | Two-channel digital isolator. `TXD`/`RXD` cross here; `VDD1`/`GND1` are the USB side, `VDD2`/`GND2` the CAN side |
| **U5 — B0505S-1WR3** | Isolated DC-DC, 5 V in from USB, 1 W out. Its `+VO`/`0V` **are** `VDD-CAN`/`GND-CAN` |
| **U1 / U6 — ME6209A33** | One 3.3 V regulator per side, so each domain has its own rail |
| **U2 — TJA1051T/3** | Transceiver, powered from the isolated side |

⇒ **The CAN side has its own supply and its own ground reference**, both produced on the
board. Nothing external is required to make the isolation work.

## Terminal block (P2)

| Pin | Net |
|---|---|
| 1 | CAN_L, through a resettable fuse |
| 2 | CAN_H, through a resettable fuse |
| 3 | **GND-CAN** — the isolated ground, *not* USB ground |
| 4 | **VDD-CAN** — the isolated 5 V, generated on the board |

> ⚠️ **Pin 3 is the isolated ground.** Tying it to your PC's ground defeats the isolation
> you paid for.

## Protection on the bus lines

Each CAN line has a **resettable fuse in series** (F2, F3) and a **TVS to isolated ground**
(TV1, TV2), with **D1** across the pair. **F1** protects the USB side.

## Switch (SW1)

Two positions: **BOOT** (holds the MCU in its USB bootloader) and **120 Ω termination**,
which connects the terminator across the bus. When to switch it off →
[`docs/termination.md`](../../docs/termination.md)

## Which board this matches

The bottom silkscreen reads `SH-C31G`, `DSD TECH` and **`V1.0-20241223`**.

## Attribution and notice of modification

This board is part of the **CANable** family and shares its microcontroller and basic
architecture with the CAN FD generation of that design. The files here are an independent
DSD TECH layout, not an edited copy of anyone else's files.

**Full attribution and the licence chain:**
[`THIRD-PARTY-NOTICES.md`](../../THIRD-PARTY-NOTICES.md)

## Licence

Hardware design files: **CERN-OHL-S-2.0** — see [`LICENSE.md`](../../LICENSE.md).

**No warranty.** Provided AS IS.
