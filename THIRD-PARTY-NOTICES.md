<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Third-party notices and attribution

Our adapters build on other people's open-source work. This file records what we used,
who wrote it, and under which licence — for the hardware and for the firmware separately.

**If you redistribute anything from this repository, or a firmware image from our
[Releases](../../releases), this file must travel with it.**

---

## 1. Hardware — the candleLight / CANable lineage

The SH-C30A belongs to the **CANable** family of USB-to-CAN adapters. The board says so
itself: `Based on Canable` is printed on the bottom silkscreen.

The CANable project's own **hardware** design files were never published by its author —
the CANable repositories contain firmware only. The closest published ancestor of this
class of board is the **candleLight** adapter by **Hubert Denkmair**:

| | |
|---|---|
| Project | **candleLight** — <https://github.com/HubertD/candleLight> |
| Author | **Hubert Denkmair** |
| Licence | **CERN Open Hardware Licence v1.2** — [`LICENSES/CERN-OHL-1.2.txt`](LICENSES/CERN-OHL-1.2.txt) |
| Shared with our boards | the same microcontroller, **STM32F072C8**, and the same basic architecture: USB device, one CAN transceiver, three status LEDs, a crystal |

### Why our files say CERN-OHL-S-2.0 and not v1.2

CERN OHL v1.2 §3.4(e) lets a modified design be licensed under *"a later version of this
Licence as may be issued by CERN"*. CERN-OHL-S-2.0 is that later version, and it is what
our hardware design files are released under. The upstream v1.2 text is kept in
[`LICENSES/`](LICENSES/) so the chain can be followed.

### Notice of modification

> **DSD TECH has modified this class of design.** The board files in this repository are an
> independent DSD TECH layout, drawn in a different EDA tool (JLC EDA, exported to Protel
> ASCII), not an edited copy of the candleLight files.

**Verified differences between candleLight and the SH-C30A** (read off both projects' own
schematics, 2026-08):

| | candleLight | **SH-C30A** |
|---|---|---|
| Microcontroller | STM32F072C8Tx | STM32F072C8T6 — **same** |
| CAN transceiver | TJA1051/3 | **TJA1040T** |
| 3.3 V regulator | MCP1754ST-3302E | **ME6209A33M3G** |
| CAN connector | SUB-D9 | **3.81 mm 3-pin terminal block** |
| Host connector | USB OTG socket | **USB-A plug** |
| Bus termination | one resistor, marked do-not-populate | **120 Ω switched by a 2-position DIP switch** |
| Bus protection | none on the schematic | **2 × gas discharge tube, ESD diode array, resettable fuses** |
| Debug header | SWD connector | **5-pin 2.54 mm header** |
| Status LEDs | 3 | 3 — **same** |

Dates: candleLight schematic as published upstream; SH-C30A schematic created 2022-06-27,
last updated 2022-07-10, board revision V1.21 dated 2023-05-06.

---

## 2. Firmware — candleLight_fw and what is inside it

The firmware images we attach to [Releases](../../releases) for the **SH-C30x** family —
**SH-C30A, SH-C30G and SH-C30L**, which share one firmware build — are built from
**candleLight_fw**.

> Other models are **not** covered by this section. Their firmware provenance is recorded
> here as their images are published.

| | |
|---|---|
| Project | **candleLight_fw** — <https://github.com/candle-usb/candleLight_fw> |
| Copyright | **Copyright (c) 2016 Hubert Denkmair** |
| Licence | **MIT** — [`LICENSES/MIT.txt`](LICENSES/MIT.txt) |

MIT requires the copyright notice and permission notice to be included **in binary
distributions too**, which is why this file ships with every firmware release.

### Components inside candleLight_fw with their own terms

Upstream's own licence file records two more components. We reproduce that record here;
we have not independently audited which of them end up in a given build.

| Component | Terms |
|---|---|
| **STM32 HAL** | BSD-style licence from STMicroelectronics |
| **STM32 USB library** | **ST Ultimate Liberty License SLA0044** — <https://www.st.com/SLA0044> |

> ⚠️ **SLA0044 is not an OSI-approved licence.** It permits redistribution in binary form
> for use on ST microcontrollers and carries its own conditions. Anyone redistributing our
> firmware images onward should read it at the link above.

---

## 3. Trademarks

**DSD TECH** is our trademark and is not licensed by this repository. **CANable**,
**candleLight**, **STM32** and other names are the marks of their respective owners and are
used here only to identify the projects and parts described above.
