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

## 2. Firmware — where each build comes from, and what is inside it

Our firmware images are attached to [Releases](../../releases). Two boards, two different
upstreams — both MIT, both carrying the same two sub-components underneath.

### SH-C30x — SH-C30A, SH-C30G and SH-C30L, which share one build

| | |
|---|---|
| Project | **candleLight_fw** — <https://github.com/candle-usb/candleLight_fw> |
| Copyright | **Copyright (c) 2016 Hubert Denkmair** |
| Licence | **MIT** — [`LICENSES/MIT.txt`](LICENSES/MIT.txt) |

### SH-C31A

The CAN FD fork of candleLight for STM32G4 boards. This is what gives the SH-C31A CAN FD
out of the box.

| | |
|---|---|
| Project | **candleLight_fw_canable_v2_fd** — <https://github.com/tymmothy/candleLight_fw_canable_v2_fd> |
| Author of the fork | **Tymm Zerr** (`tymmothy`) |
| Copyright | **Copyright (c) 2016 Hubert Denkmair**<br>**Copyright (c) 2022 Ryan Edwards** — changes for STM32G4 and CAN FD |
| Licence | **MIT** — [`LICENSES/MIT.txt`](LICENSES/MIT.txt) |

> ⚠️ **That fork describes itself as unmaintained** — its repository summary reads
> *"gs_usb compatible firmware for canable v2 w/FD (not maintained)"*. We say so because
> you may want to know before building on it. It is still what we ship.

> Models not named above are **not** covered by this section. Their firmware provenance is
> recorded here as their images are published.

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

### ElmueSoft CANable 2.5 — optional firmware, not what we ship

We publish two builds of **CANable 2.5** by **ElmueSoft** so that owners of the SH-C31A and
SH-C31G can choose them. **They are not our work**, they are not what the boards ship with,
and we did not compile them — what we publish are the author's own precompiled files,
taken byte for byte from a pinned upstream commit. See
[`docs/other-firmware.md`](docs/other-firmware.md).

> The MIT License
> Copyright (c) 2025 ElmueSoft / Nakanishi Kiyomaro / Normadotcom
> https://netcult.ch/elmue/CANable Firmware Update

| | |
|---|---|
| Upstream | <https://github.com/Elmue/CANable-2.5-firmware-Slcan-and-Candlelight> |
| Pinned commit | `eb1c7e3589b6135469dd0745c3a81911b88513c6` (2026-09-15) |
| Licence of `Firmware/` | **MIT** — the notice above must travel with the binaries |

> ⚠️ **The copyright is held by three parties, not one.** Reproduce the notice in full.
>
> ⚠️ The **sample applications** in the same upstream repository are under a different
> licence (**BSD-3-Clause**, `SampleApplication C#/Source/License.txt`), which additionally
> forbids using the copyright holder's name to endorse or promote products. We do not
> redistribute those, and we do not present ElmueSoft as endorsing anything of ours.

**With thanks to Elmue** for making CANable 2.5 work on boards that have no crystal fitted,
which is what ours are.

---

## 3. Trademarks

**DSD TECH** is our trademark and is not licensed by this repository. **CANable**,
**candleLight**, **STM32** and other names are the marks of their respective owners and are
used here only to identify the projects and parts described above.
