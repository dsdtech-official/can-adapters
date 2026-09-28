<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Software for your CAN adapter

**[diCAN](https://github.com/dsdtech-official/diCAN)** is our free, open-source CAN
analyser for Windows and macOS. Use it to view live traffic, send frames, record a
session and export CSV or PEAK `.trc` files. It supports the six adapters in this
repository with their supported firmware. You do not need to change firmware just
to try diCAN.

## Get diCAN

| Your computer | Where to get it |
|---|---|
| Windows 10 version 1809 or later | [Microsoft Store](https://apps.microsoft.com/detail/9N16CGHG2L72) or [direct downloads](https://github.com/dsdtech-official/diCAN/releases/latest) for x64, x86 and ARM64 |
| macOS 12 or later, Apple silicon | [Direct download](https://github.com/dsdtech-official/diCAN/releases/latest) |
| macOS on Intel | diCAN supports Intel Macs, but a ready-to-run Intel download is not currently provided. See its [source and build instructions](https://github.com/dsdtech-official/diCAN#building-from-source) |
| Linux | diCAN is not available. See [which firmware is on your adapter](identify-firmware.md) for the Linux interfaces and other software |

For installation details, any store availability updates and the current platform list, see the
[diCAN README](https://github.com/dsdtech-official/diCAN#downloads).

## Which adapter do you have?

| Model | Typical factory interface | diCAN connection |
|---|---|---|
| [SH-C30A](../SH-C30A/) | gs_usb | Raw USB |
| [SH-C30G](../SH-C30G/) | gs_usb | Raw USB |
| [SH-C30L](../SH-C30L/) | gs_usb | Raw USB |
| [SH-C31A](../SH-C31A/) | gs_usb | Raw USB |
| [SH-C31B](../SH-C31B/) | ElmueSoft Slcan 2.5 (`Multiboard`) | Serial port |
| [SH-C31G](../SH-C31G/) | gs_usb | Raw USB |

**Check the firmware actually installed before relying on this table.** Adapters
can be reflashed, and an SH-C31B board is silkscreened SH-C31A. diCAN also supports
compatible Elmue Multiboard 2.5 firmware. See
[how to identify the firmware](identify-firmware.md) if the USB connection looks
different from the one shown here.

The available CAN modes depend on the firmware and hardware, not just the model
name. SH-C30x hardware supports Classic CAN, not CAN FD. SH-C31x hardware supports
CAN FD, but some older factory firmware does not report that capability. diCAN
offers only the modes the connected adapter reports; if CAN FD is missing, check
your [model's firmware page](../README.md) before changing firmware.

## First connection

1. Download diCAN, connect the adapter, then choose **Session → New session**.
2. Select the adapter and set the CAN mode and bit rates for your bus.
3. [Check the 120 Ω terminator](termination.md) before connecting to a live bus.
4. View the frame stream, send a test frame, or start recording.

On Windows, gs_usb adapters use WinUSB; the SH-C31B's factory Slcan firmware
instead appears as a serial port. Do not apply a USB driver replacement to that
serial port. If diCAN lists an adapter as unavailable, read the explanation in
the app and check its [firmware identity](identify-firmware.md).

For diCAN questions, use its [repository and support information](https://github.com/dsdtech-official/diCAN).
Firmware images and update steps remain in each adapter's `firmware/` folder.
