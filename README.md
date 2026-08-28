<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# DSD TECH CAN adapters

Everything that ships with our USB-to-CAN adapters, in one place per model: the manual,
the datasheet, the hardware design files, the firmware and how to flash it, and working
example code.

**Find your model below.** The part number is printed on the board.

| Model | Bus | Isolation | Host connector | CAN connector |
|---|---|---|---|---|
| [**SH-C30A**](SH-C30A/) | CAN 2.0A / 2.0B | — | USB-A plug | 3.81 mm terminal |
| [**SH-C31A**](SH-C31A/) | **CAN FD** | — | USB-A plug | 3.81 mm terminal |

_More models are being added._

## What is in each model folder

| Folder | What is in it |
|---|---|
| `manual/` | The user manual — start here |
| `datasheet/` | Electrical and mechanical specifications |
| `hardware/` | Schematic, bill of materials, board files |
| `firmware/` | Which firmware the board runs, and how to change it |
| `examples/` | Working code you can run — Python, SocketCAN, C |

Shared documentation that applies to every model — termination, bit rates, LEDs,
identifying your firmware — is in [`docs/`](docs/).

## Downloads

**Binaries are not stored in this repository.** Firmware images, fabrication bundles and
driver packages are attached to [Releases](../../releases), where each one is tied to a
version you can cite in a support request.

## Licensing

This repository holds several kinds of material under different licences. Every file
carries an `SPDX-License-Identifier`, and the full texts are in [`LICENSES/`](LICENSES/).

| Material | Licence |
|---|---|
| Hardware design files | CERN-OHL-S-2.0 |
| Documentation, manuals, datasheets | CC-BY-SA-4.0 |
| Example code | BSD-3-Clause |
| Firmware images we publish | MIT (candleLight_fw, © 2016 Hubert Denkmair) |

Our boards descend from the **CANable** family and share their microcontroller and basic
architecture with **candleLight** by Hubert Denkmair (**CERN-OHL-1.2**). Full attribution,
the licence chain and what we changed: **[`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md)**.

The **DSD TECH** name and logo are trademarks and are not licensed here. FCC / CE / RoHS
certifications apply only to units we manufacture and sell.

**No warranty.** These files are provided AS IS.

## Support

Questions about a product go in [Issues](../../issues).
For sales, warranty and returns: <https://www.deshide.com>

Found a security issue? Report it privately rather than in an issue — see
[`SECURITY.md`](SECURITY.md).
