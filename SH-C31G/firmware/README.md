<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C31G — Firmware

## Same firmware as the SH-C31A

**The SH-C31G uses the same firmware image as the
[SH-C31A](../../SH-C31A/firmware/).** The current release is **v1.5**; existing
SH-C31G units may still have v1.4 or an earlier build. We recommend that owners
check their firmware and [update to v1.5](#download).

That page is the full story — measured bit rates, how the host behaves under load, how to
flash, licensing. Everything below is the short form.

## What this board ships with

**Our own gs_usb build.** The adapter presents itself as a raw USB device: the
kernel `gs_usb` driver on Linux, WinUSB on Windows. On Linux that means a standard SocketCAN
interface with nothing to install.

Some existing units carry v1.4; earlier units and older stock may carry the original
upstream canable2 build. **Those units work, and you can keep using them** — but the
original upstream build has
three limitations worth knowing about, and one of them matters on a live bus:

- 🔴 **It reports `listen-only` support and does not honour it.** Ask it to stay silent and
  it still transmits and still acknowledges, with no error and no warning. If you need a
  guaranteed passive node, that build cannot give you one.
- 🔴 **It has no CAN FD at all** — it does not report the capability, so the kernel
  refuses to open FD on it.
- ⚠️ **Its echoes are not trustworthy**: ten frames pushed while the channel was closed
  produced ten echoes and zero frames on the wire.

⭐ **We recommend updating to v1.5**, including from v1.4. It changes how the BOOT switch
is used for future updates; read [Flashing](#flashing) before starting. The original
upstream build and v1.4 also differ in what happens to queued frames when you close the
channel: v1.4 does **not** discard them. Drain before you close.

## CAN FD works out of the box

**No reflashing, no second firmware, no serial port.** CAN FD runs over the same gs_usb
interface as classic CAN.

The measurements are on the [SH-C31A page](../../SH-C31A/firmware/): FD data rates of 1 M,
2 M, 2.5 M, 3.4 M and 5 M all verified with 64-byte payloads, and a 75-minute bidirectional
run at 5 Mbit/s with zero frames lost and zero bus errors.

**The SH-C31G is rated for the same data rates**, up to 5 Mbit/s. It is the same
microcontroller running the same image, and every part in the signal path is rated for it: the
digital isolator between the USB and CAN sides is a 10 Mbit/s part, and the **TJA1051T/3**
transceiver has its CAN FD fast-phase timing guaranteed to 5 Mbit/s. **5 Mbit/s is the top of
that transceiver's guaranteed range, so treat it as the ceiling rather than a starting point.**

**On provenance:** the per-rate sweep above was run on an SH-C31A. What has been run on the
SH-C31G itself is CAN FD with the isolation in circuit, including an extended soak. We will
publish a sweep taken on this board when we have one.

**To check which build you have**, inspect the USB product string and device revision —
Device Manager on Windows, or `lsusb -v` on Linux. Both v1.4 and v1.5 report
**`SH-C31x`** by **`DSD TECH`**; the revision distinguishes them. See the
[version table on the SH-C31A firmware page](../../SH-C31A/firmware/#which-firmware-do-i-have).

## Download

**[SH-C31A firmware v1.5](https://github.com/dsdtech-official/can-adapters/releases/tag/SH-C31A/fw-v1.5)**
— the current shared image for SH-C31A and SH-C31G. The release retains the SH-C31A
tag name because both models use one build. The
[v1.4 release](https://github.com/dsdtech-official/can-adapters/releases/tag/SH-C31A/fw-v1.4)
remains available for reference. We have tested v1.5 on an SH-C31G. The detailed
per-rate measurements cited above were made on an SH-C31A.

Check what you downloaded before flashing it:

```bash
sha256sum -c SHA256SUMS.txt
```

## Other firmware you can run instead

These boards will also run **ElmueSoft's CANable 2.5**, a separate project by a different
author, in either of two forms — a gs_usb build like ours, or one that turns the adapter
into a plain **serial port**. Both are published here with our thanks to Elmue, and neither
is required: → [`docs/other-firmware.md`](../../docs/other-firmware.md)

## Flashing

Over USB DFU, to the STM32 system bootloader (`0483:DF11`). Follow the
[SH-C31A flashing steps](../../SH-C31A/firmware/#flashing) with the shared v1.5 image.
If the adapter already runs v1.5, first unlock BOOT0 while the firmware is running;
then unplug, set the BOOT switch and reconnect. The switch alone no longer enters DFU
from v1.5. From v1.4 or the original upstream build, the unlock step is not required.

> Reflashing is not required for normal use.

## Licence and attribution

Built from **[`candleLight_fw_canable_v2_fd`](https://github.com/tymmothy/candleLight_fw_canable_v2_fd)**
by **Tymm Zerr**, the CAN FD fork of candleLight for STM32G4 boards. **MIT.** The notice
that has to travel with the binaries is
[`THIRD-PARTY-NOTICES.md`](../../THIRD-PARTY-NOTICES.md), and it is attached to the release.

**If you mirror our firmware images anywhere, carry that file with them.**
