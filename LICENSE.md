<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Licensing

This repository holds several kinds of material, and they are not under the same licence.
**Every file carries an `SPDX-License-Identifier`** naming its own licence; the full texts
are in [`LICENSES/`](LICENSES/). This follows the [REUSE](https://reuse.software/)
specification, so the licence of any single file can be read off that file.

| Material | Licence | Full text |
|---|---|---|
| Hardware design files — schematics, board files, BOMs | **CERN-OHL-S-2.0** | [`LICENSES/CERN-OHL-S-2.0.txt`](LICENSES/CERN-OHL-S-2.0.txt) |
| Documentation — manuals, datasheets, READMEs | **CC-BY-SA-4.0** | [`LICENSES/CC-BY-SA-4.0.txt`](LICENSES/CC-BY-SA-4.0.txt) |
| Example code | **BSD-3-Clause** | [`LICENSES/BSD-3-Clause.txt`](LICENSES/BSD-3-Clause.txt) |
| Firmware images we build and publish | **MIT** *(candleLight_fw, © 2016 Hubert Denkmair)* | [`LICENSES/MIT.txt`](LICENSES/MIT.txt) |

> ⚠️ **GitHub shows one licence badge per repository, and one badge cannot describe the
> table above.** Take the `SPDX-License-Identifier` in the file you are actually using as
> authoritative, not the badge.

## Third-party material

Our hardware and our firmware both build on other people's open-source work, which keeps
**its own licence and its own copyright notices, retained verbatim**.

**[`THIRD-PARTY-NOTICES.md`](THIRD-PARTY-NOTICES.md) is the single place that records all of
it** — who wrote what, under which licence, and what we changed. Read it before
redistributing anything from this repository.

In short:

| What | Upstream | Licence |
|---|---|---|
| Hardware lineage | **candleLight** by Hubert Denkmair | **CERN-OHL-1.2** → our files are **CERN-OHL-S-2.0**, permitted by its §3.4(e) |
| Firmware | **candleLight_fw** by Hubert Denkmair | **MIT** |
| Inside the firmware | STM32 HAL / STM32 USB library | BSD-style / **ST SLA0044** — **not OSI-approved** |

## Not covered by any of the above

The **DSD TECH** name and logo are trademarks and are not licensed here.

FCC / CE / RoHS certifications apply only to units we manufacture and sell — building your
own board from these files does not carry them over.

**No warranty.** All material is provided AS IS, without warranty of any kind.
