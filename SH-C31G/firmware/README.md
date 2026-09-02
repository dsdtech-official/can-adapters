<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C31G — Firmware

## Same firmware as the SH-C31A

**The SH-C31G runs exactly the image the [SH-C31A](../../SH-C31A/firmware/) runs**, `v1.4`.
Same microcontroller, same pin assignment, one build for both boards.

That page is the full story — measured bit rates, how the host behaves under load, how to
flash, licensing. Everything below is the short form.

## What this board ships with

**Our own gs_usb build, `v1.4`.** The adapter presents itself as a raw USB device: the
kernel `gs_usb` driver on Linux, WinUSB on Windows. On Linux that means a standard SocketCAN
interface with nothing to install.

**Units produced from September 2026 ship with v1.4.** Anything made before that carries an
earlier build, and so does older stock still moving through distribution. Those units are
not faulty and keep working.

## CAN FD works out of the box

**No reflashing, no second firmware, no serial port.** CAN FD runs over the same gs_usb
interface as classic CAN.

The measurements are on the [SH-C31A page](../../SH-C31A/firmware/) and apply to this board
— it is the same microcontroller running the same image. In short: FD data rates of 1 M,
2 M, 2.5 M, 3.4 M and 5 M all verified with 64-byte payloads, and a 75-minute bidirectional
run at 5 Mbit/s with zero frames lost and zero bus errors.

**To check which build you have**, look at the name the adapter reports over USB — Device
Manager on Windows, or `lsusb` on Linux. v1.4 reports itself as **`SH-C31x`**, made by
**`DSD TECH`**. Anything else is an earlier build.

## Download

**[SH-C31A firmware v1.4](https://github.com/dsdtech-official/can-adapters/releases/tag/SH-C31A/fw-v1.4)**
— the release is named for the SH-C31A because that is the board it was first cut for.
**One build serves SH-C31A and SH-C31G.**

Check what you downloaded before flashing it:

```bash
sha256sum -c SHA256SUMS.txt
```

## Flashing

Over USB DFU, to the STM32 system bootloader (`0483:DF11`). A USB cable is all you need;
the **BOOT** position of the on-board switch puts the MCU there.

> Reflashing is not required for normal use.

## Licence and attribution

Built from **[`candleLight_fw_canable_v2_fd`](https://github.com/tymmothy/candleLight_fw_canable_v2_fd)**
by **Tymm Zerr**, the CAN FD fork of candleLight for STM32G4 boards. **MIT.** The notice
that has to travel with the binaries is
[`THIRD-PARTY-NOTICES.md`](../../THIRD-PARTY-NOTICES.md), and it is attached to the release.

**If you mirror our firmware images anywhere, carry that file with them.**
