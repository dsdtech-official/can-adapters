<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C30A — Firmware

## What this board ships with

**candlelight.** The adapter presents itself as a raw USB device: the kernel `gs_usb`
driver on Linux, WinUSB on Windows.

**The SH-C30A has no CAN FD and cannot gain it by reflashing** — the STM32F072 has a
classic bxCAN peripheral, not FDCAN. It runs CAN 2.0A and 2.0B at up to 1 Mbit/s.

## Which firmware do I have?

Two personalities exist for this class of adapter and they look completely different to the
host. Ten seconds to tell them apart →
[`docs/identify-firmware.md`](../../docs/identify-firmware.md)

| | **candlelight** | **slcan** |
|---|---|---|
| Appears as | a raw USB device | a serial port |
| Windows | *Universal Serial Bus devices*, WinUSB | `COM<n>` under *Ports* |
| Linux | kernel `gs_usb` → a **SocketCAN** interface | `/dev/ttyACM<n>` |

## Changing firmware

Both personalities are flashed over USB DFU.

**Firmware images are attached to [Releases](../../../../releases)**, not stored in this
folder — binaries cannot be removed from git history afterwards, and a release ties an
image to a version you can quote in a support request.

> ⚠️ **Reflashing is not required for normal use.** The board works as shipped. Only
> reflash if you specifically need the other personality.

## Licence and attribution

The firmware images we publish are built from **candleLight_fw** by **Hubert Denkmair**,
released under the **MIT** licence.

> Copyright (c) 2016 Hubert Denkmair — [`LICENSES/MIT.txt`](../../LICENSES/MIT.txt)

MIT requires the copyright and permission notice to be included **in binary distributions
too**, so [`THIRD-PARTY-NOTICES.md`](../../THIRD-PARTY-NOTICES.md) ships with every firmware
release. It also records two components inside candleLight_fw that carry their own terms —
the **STM32 HAL** (BSD-style) and the **STM32 USB library**
(**ST Ultimate Liberty License SLA0044**, not an OSI-approved licence).

**If you mirror our firmware images anywhere, carry that file with them.**
