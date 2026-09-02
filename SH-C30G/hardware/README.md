<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C30G — Hardware

Schematic and board files for the SH-C30G, board revision **V1.5**.

## Files

| File | What it is |
|---|---|
| `SH-C30G-V1.5.SchDoc` | Schematic |
| `SH-C30G-V1.5.PcbDoc` | Board layout |
| `SH-C30G-V1.5.pdf` | Schematic, printable |
| `SH-C30G-V1.5.epro2` | The EDA project the two above came from |

Both `.SchDoc` and `.PcbDoc` are **Protel ASCII** — plain text, so they diff and review like
source. Altium Designer opens them directly. Other EDA tools' Altium importers mostly target
the *binary* variant; we have not tested them against these ASCII files.

## How the isolation is built

| Part | Job |
|---|---|
| **U2 — ADuM3201ARZ** | Two-channel digital isolator. `TXD`/`RXD` cross here; `VDD1`/`GND1` are the USB side, `VDD2`/`GND2` the CAN side |
| **U3 — B0505S-1WR3** | Isolated DC-DC, 5 V in from USB, 1 W out. Its `+VO`/`0V` **are** `VDD-CAN`/`GND-CAN` |
| **U6 — SIT1040T** | Transceiver, powered from `VDD-CAN`. `STB` tied to `GND-CAN`, so it is always awake |

⇒ **The CAN side has its own supply and its own ground reference**, both produced on the
board. Nothing external is required to make the isolation work.

## Terminal block (P1)

| Pin | Net | |
|---|---|---|
| 1 | CAN_L | through resettable fuse **F2** |
| 2 | CAN_H | through resettable fuse **F1** |
| 3 | **GND-CAN** | the isolated ground — this is *not* USB ground |
| 4 | **VDD-CAN** | the isolated 5 V, generated on the board |

> ⚠️ **Pin 3 is the isolated ground.** Tying it to your PC's ground defeats the isolation
> you paid for.

## Protection on the bus lines

Each CAN line has a **resettable fuse in series** (F1, F2) and a **TVS to isolated ground**
(TV1, TV2), with **D1** across the pair. **F3** protects the DC-DC input on the USB side.

## Switch (SW1)

Two positions: **BOOT** (holds the MCU in its USB bootloader) and **120 Ω termination**,
which connects the terminator across the bus. When to switch it off →
[`docs/termination.md`](../../docs/termination.md)

## Which board this matches

The bottom silkscreen reads `SH-C30G`, `DSD TECH` and **`V1.5-20241005`**.

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
