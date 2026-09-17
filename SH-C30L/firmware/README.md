<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C30L — Firmware

## Same firmware as the SH-C30A

**The SH-C30L runs exactly the image the [SH-C30A](../../SH-C30A/firmware/) runs**, `v2.1`.
Same microcontroller, same pin assignment, one build for the whole SH-C30x family:
**SH-C30A, SH-C30G and SH-C30L**. The difference between these boards is where the USB plug
sits, and firmware cannot see that.

That page is the full story — versions, what changed, how to flash, licensing. Everything
below is the short form.

## What this board ships with

**candlelight.** The adapter presents itself as a raw USB device: the kernel `gs_usb`
driver on Linux, WinUSB on Windows.

**Units produced from September 2026 ship with v2.1.** Anything made before that carries an
earlier build, and so does older stock still moving through distribution. **Those units keep
working and you can stay on them** — but `v2.1` fixes two behaviours worth having, and the
[SH-C30A page](../../SH-C30A/firmware/) lists them.

**The SH-C30L has no CAN FD and cannot gain it by reflashing** — the STM32F072 has a classic
bxCAN peripheral, not FDCAN. It runs CAN 2.0A and 2.0B at up to 1 Mbit/s.

**To check which build you have**, look at the name the adapter reports over USB — Device
Manager on Windows under *Universal Serial Bus devices*, or `lsusb` on Linux. v2.1 reports
itself as **`SH-C30x`**, made by **`DSD TECH`**. Anything else is an earlier build.

## Download

**[SH-C30A firmware v2.1](https://github.com/dsdtech-official/can-adapters/releases/tag/SH-C30A/fw-v2.1)**
— the release is named for the SH-C30A because that is the board it was first cut for.
**One build serves SH-C30A, SH-C30G and SH-C30L.**

Check what you downloaded before flashing it:

```bash
sha256sum -c SHA256SUMS.txt
```

## Flashing

Over USB DFU, to the STM32 system bootloader (`0483:DF11`). A USB cable is all you need;
the **BOOT** position of the on-board switch puts the MCU there.

> ⚠️ **Reflashing is not required for normal use.** An adapter on an earlier build keeps
> working.

## Which firmware do I have?

Two personalities exist for this class of adapter and they look completely different to the
host. Ten seconds to tell them apart →
[`docs/identify-firmware.md`](../../docs/identify-firmware.md)

## Licence and attribution

Built from **candleLight_fw** by **Hubert Denkmair**, **MIT**. The notice that has to travel
with the binaries is [`THIRD-PARTY-NOTICES.md`](../../THIRD-PARTY-NOTICES.md), and it is
attached to the release.

**If you mirror our firmware images anywhere, carry that file with them.**
