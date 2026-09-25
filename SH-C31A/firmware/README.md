<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C31A — Firmware

## What this board ships with

**Our own gs_usb build.** The current release is **`v1.5`** — see **[Download](#download)**
below and **[What changed in v1.5](#what-changed-in-v15)**.

**Units produced from September 2026 ship with v1.4.** Anything made before that carries
the original upstream canable2 build, and so does older stock still moving through
distribution. **Those units work, and you can keep using them** — but that build has
three limitations worth knowing about, and one of them matters on a live bus:

- 🔴 **It reports `listen-only` support and does not honour it.** Ask it to stay silent and
  it still transmits and still acknowledges, with no error and no warning. If you need a
  guaranteed passive node, that build cannot give you one.
- 🔴 **It has no CAN FD at all** — it does not report the capability, so the kernel
  refuses to open FD on it.
- ⚠️ **Its echoes are not trustworthy**: ten frames pushed while the channel was closed
  produced ten echoes and zero frames on the wire.

⭐ **So we do recommend updating** — the file below is free, and the upgrade is reversible
because the bootloader lives in ROM and is never overwritten.

The adapter presents itself as a raw USB device: the kernel `gs_usb` driver on Linux,
WinUSB on Windows. On Linux that means a standard SocketCAN interface with nothing to
install.

## CAN FD works out of the box

**No reflashing, no second firmware, no serial port.** CAN FD runs over the same gs_usb
interface as classic CAN.

These are measurements on this board, not figures from a datasheet:

Every rate below was read back from the interface and the payload verified byte for byte.

| FD data rate | |
|---|---|
| 1 M · 2 M · 2.5 M | ✅ 8/8 frames, 64-byte payloads |
| 3.4 M | ✅ 8/8 |
| **5 M** | ✅ 8/8 — **the transceiver's ceiling, not the microcontroller's** |

| Nominal rate | |
|---|---|
| 10 k · 125 k · 250 k · 500 k · 1 M | ✅ all five, **0.0000 % loss**, each read back correctly |

| Endurance | |
|---|---|
| 2 Mbit/s FD, 180 s, bidirectional, 64-byte payloads | **17548 / 17548 frames, 0.0000 % loss**, zero CAN errors |
| 500 kbit/s flood, Linux SocketCAN, 60 s | 165162 / 165162, **0.00 % loss**, 2753 frames/s |
| Hardware timestamps | 12/12 delivered, strictly increasing, 0.94 % deviation |

Measured over SocketCAN on Linux, on `v1.4`. `v1.5` does not change bit timing, the CAN
clock or the supported rates; on `v1.5` we re-ran classic CAN at 500 kbit/s and 1 Mbit/s, CAN FD
with bit-rate switching up to 5 Mbit/s, and a 180-second bidirectional CAN FD run.

## Two things that will catch you out

**① `python-can` cannot open 125 k or 250 k. The adapter can.**

Over SocketCAN all five standard nominal rates work, measured above. `python-can`'s
`gs_usb` backend refuses anything where `f_clock / bitrate` exceeds 800, which rules out
125 k and 250 k on a 170 MHz CAN clock. **That is a limitation inside that library, not a
property of this board** — the same adapter carries those rates fine from Linux.

**② A rate you asked for is not necessarily the rate you got.**

`ip link set ... up` exits `0` even when the divisors cannot reach your number. Asking for
a 4 Mbit/s data rate yields **3 953 488**, silently. 1 M, 2 M, 2.5 M, 3.4 M and 5 M land
exactly.

```bash
ip -details link show can0 | grep -E 'bitrate|dbitrate'
```

**Read it back. Every time.** A script that trusts the exit code will run a bus at the
wrong speed and look fine doing it.

## How the host behaves under a flood

Worth knowing because it looks like a firmware fault and is not:

| Host | Frames lost |
|---|---|
| **Linux SocketCAN** | **0 %** — the kernel waits for each USB transfer to complete rather than pushing blindly |
| **Windows, python-can, an application that reads while it writes** | ~5 %, when transmitting faster than the bus can carry |
| **Windows, an application that never reads** | ~99 % — the internal frame pool fills and everything after it is dropped |

The last row is a misuse, not a rate: an application that transmits and never calls
`recv` will lose almost everything. Read while you write.

## What changed in v1.5

**① The adapter no longer drops into its bootloader on its own.**

On this board the microcontroller's BOOT0 pin is also its CAN RX pin. An idle CAN bus holds
that pin high, so if the adapter loses power for a moment — a USB hub switching off, a host
rebooting — it can come back up in the ST bootloader (`0483:DF11`) instead of running.

About two seconds after a host has enumerated it, with the CAN channel closed, `v1.5` sets
the chip to ignore that pin and always start the firmware. It writes the setting only if it is
not already in place, and it takes effect from the next power-up.

⚠️ **The price: the BOOT switch alone no longer enters firmware-update mode.** Unlock first —
see **[Flashing](#flashing)**.

**② Closing the channel now discards what was still queued.** Frames the host queued but the
bus never took are dropped on close — 0 of 40 came out after reopening, against 40 of 40 on
`v1.4`. Two details for anyone writing host software:

- frames sent to the adapter **while the channel is closed** are discarded, with no echo;
- **at most one** transmit echo from the previous session can still arrive after reopening,
  because it had already been handed to USB. The Linux kernel ignores echoes it is not waiting
  for; other host software should do the same.

**③ Bus state on demand.** New `GS_USB_BREQ_GET_STATE` (request 14, feature bit 13): 12 bytes,
`u32 state, u32 rxerr, u32 txerr`. With the channel closed it reports `GS_CAN_STATE_STOPPED`
and zero counters.

**④ CAN FD transmit echoes keep their FD flag**, and carry their hardware timestamp in the FD
record's timestamp field, where the Linux kernel reads it.

Not tested on `v1.5`: runs longer than 180 seconds, macOS, and a power cut during the ~25 ms in
which the setting in ① is written.

## Which firmware do I have?

Look at the name the adapter reports over USB: Device Manager on Windows, under
*Universal Serial Bus devices*, or `lsusb` on Linux.

| | |
|---|---|
| **v1.5** | **`SH-C31x`**, made by **`DSD TECH`**, device revision **`0x0215`** — Windows shows `REV_0215` in the hardware ID |
| **v1.4** | **`SH-C31x`**, made by **`DSD TECH`**, device revision `0x0200` |
| Anything else | an earlier build |

The device revision is `bcdDevice` in the USB descriptor (`lsusb -v` on Linux). From `v1.5`
on it carries the version: `0x15` in the low byte is 1.5. After updating, Windows sets the
adapter up once more because of the new revision — that is expected.

## Download

**[SH-C31A firmware v1.5](https://github.com/dsdtech-official/can-adapters/releases/tag/SH-C31A/fw-v1.5)** — the current release.

| File | |
|---|---|
| [`SH-C31A_canable2_v1.5.dfu`](https://github.com/dsdtech-official/can-adapters/releases/download/SH-C31A/fw-v1.5/SH-C31A_canable2_v1.5.dfu) | **Start here.** DfuSe format, for `dfu-util` or ST tools |
| [`SH-C31A_canable2_v1.5.bin`](https://github.com/dsdtech-official/can-adapters/releases/download/SH-C31A/fw-v1.5/SH-C31A_canable2_v1.5.bin) | Raw image, flashed at `0x08000000` |
| [`SH-C31A_canable2_v1.5.hex`](https://github.com/dsdtech-official/can-adapters/releases/download/SH-C31A/fw-v1.5/SH-C31A_canable2_v1.5.hex) | Intel HEX |
| [`SHA256SUMS.txt`](https://github.com/dsdtech-official/can-adapters/releases/download/SH-C31A/fw-v1.5/SHA256SUMS.txt) | Checksums for the three above |
| [`THIRD-PARTY-NOTICES.md`](https://github.com/dsdtech-official/can-adapters/releases/download/SH-C31A/fw-v1.5/THIRD-PARTY-NOTICES.md) | The licence notice. **Carry it with the images if you mirror them** |

The previous build stays available: **[SH-C31A firmware v1.4](https://github.com/dsdtech-official/can-adapters/releases/tag/SH-C31A/fw-v1.4)**.

Check what you downloaded before flashing it:

```bash
sha256sum -c SHA256SUMS.txt
```

Images are not kept in this folder. Binaries cannot be removed from git history
afterwards, and a release ties an image to a version you can quote in a support request.

## Other firmware you can run instead

These boards will also run **ElmueSoft's CANable 2.5**, a separate project by a different
author, in either of two forms — a gs_usb build like ours, or one that turns the adapter
into a plain **serial port**. Both are published here with our thanks to Elmue, and neither
is required: → [`docs/other-firmware.md`](../../docs/other-firmware.md)

## Flashing

Over USB DFU, to the STM32 system bootloader (`0483:DF11`). A USB cable and
[`dfu-util`](https://dfu-util.sourceforge.net/) are all you need.

> Reflashing is not required for normal use.

**From `v1.5` (and to any later build):**

1. Unlock the bootloader: `dfu-util -e -d 1d50:606f`. It returns at once — that is normal.
2. Unplug, set the BOOT switch, plug back in. The adapter appears as `0483:DF11`.
3. `dfu-util -d 0483:df11 -a 0 -s 0x08000000 -D SH-C31A_canable2_v1.5.bin`
4. Set the switch back and replug. The new firmware locks the pin again about two seconds
   after it starts.

The unlock lasts **one power cycle**: power the adapter up normally instead, and it locks
again. If flashing fails half-way, the switch still works, because the unlock happened before
the bootloader started — recover the usual way.

**From `v1.4` or older:** skip step 1.

Host software can do step 1 without `dfu-util`: vendor request 24 (`bmRequestType 0x41`,
12 bytes little-endian `u16 operation, u16 pin, u32 0, u32 0`, `pin = 1`, `operation = 6`
unlocks, `5` locks). It does not report failure; read the result back with request 25
(`bmRequestType 0xC1`, `wValue = 1`, 2 bytes: bit `0x0002` = BOOT0 currently honoured,
bit `0x0100` = changes at the next power-up). If the CAN channel is open, the change is made
when it closes.

## Licence and attribution

Built from **[`candleLight_fw_canable_v2_fd`](https://github.com/tymmothy/candleLight_fw_canable_v2_fd)**
by **Tymm Zerr** (`tymmothy`) — the CAN FD fork of candleLight for STM32G4 boards. **MIT.**

**Our changes are published in [`source/`](source/)**: one patch against upstream, the build
steps and a toolchain file. Built as described there, the result is byte-for-byte the `v1.5`
image in the release; leave out one build switch and the same patch gives `v1.4`.

> Copyright (c) 2016 Hubert Denkmair
> Copyright (c) 2022 Ryan Edwards (changes for STM32G4 and CAN-FD)
> — [`LICENSES/MIT.txt`](../../LICENSES/MIT.txt)

> ⚠️ **Upstream describes itself as not maintained** — the repository summary reads
> *"gs_usb compatible firmware for canable v2 w/FD (not maintained)"*, and its README says
> *"This is not likely to be maintained."* We are telling you because you may want to know
> before building on it. It is still what we build on, and every measurement above was taken
> on our builds of it.

MIT requires the copyright and permission notice to be included **in binary distributions
too**, so [`THIRD-PARTY-NOTICES.md`](../../THIRD-PARTY-NOTICES.md) ships with every
firmware release. It also records two components inside that firmware which carry their own
terms — the **STM32 HAL** (BSD-style) and the **STM32 USB library**
(**ST Ultimate Liberty License SLA0044**, not an OSI-approved licence).

**If you mirror our firmware images anywhere, carry that file with them.**
