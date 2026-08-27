<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C31A — Firmware

## What this board ships with

**candlelight.** The adapter presents itself as a raw USB device: the kernel `gs_usb`
driver on Linux, WinUSB on Windows.

> ⚠️ **Out of the box this adapter does not do CAN FD**, because candlelight does not carry
> CAN FD at all. **The hardware is CAN FD capable** — the STM32G431 has an FDCAN
> peripheral — and reflashing to a **slcan** firmware is what turns that on.

| | CAN FD hardware | CAN FD as shipped | CAN FD after flashing slcan |
|---|---|---|---|
| SH-C31A | ✅ | **No** | **Yes** |

CAN 2.0A and 2.0B run at up to 1 Mbit/s on either firmware.

## Which firmware do I have?

Ten seconds to tell them apart →
[`docs/identify-firmware.md`](../../docs/identify-firmware.md)

| | **candlelight** | **slcan** |
|---|---|---|
| Appears as | a raw USB device | a serial port |
| Windows | *Universal Serial Bus devices*, WinUSB | `COM<n>` under *Ports* |
| Linux | kernel `gs_usb` → a **SocketCAN** interface | `/dev/ttyACM<n>` |
| CAN FD | — | ✅ when the software opens the serial port directly |

## Changing firmware

Both personalities are flashed over USB DFU.

**Firmware images are attached to [Releases](../../../../releases)**, not stored in this
folder — binaries cannot be removed from git history afterwards, and a release ties an
image to a version you can quote in a support request.

## Third-party firmware

**CANable 2.5** by ElmüSoft is an independent, actively maintained firmware that runs on
CANable-derived boards and ships both personalities. It is published under BSD-3-Clause and
is **not** what we install at the factory.

Upstream manual: <https://netcult.ch/elmue/CANable%20Firmware%20Update/>
