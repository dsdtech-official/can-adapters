<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C31A — Firmware

## What this board ships with

**Our own gs_usb build, `v1.4`** — see **[Download](#download)** below.

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
because the bootloader lives in ROM and is never overwritten. ⚠️ **One thing changes in the
other direction**: `v1.4` does **not** discard queued frames when you close the channel,
while the older build does, so drain before you close.

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

Measured over SocketCAN on Linux.

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

## Which firmware do I have?

Look at the name the adapter reports over USB: Device Manager on Windows, under
*Universal Serial Bus devices*, or `lsusb` on Linux.

| | |
|---|---|
| **v1.4** | reports itself as **`SH-C31x`**, made by **`DSD TECH`** |
| Anything else | an earlier build |

## Download

**[SH-C31A firmware v1.4](https://github.com/dsdtech-official/can-adapters/releases/tag/SH-C31A/fw-v1.4)** — the current build, and what units produced from September 2026
ship with.

| File | |
|---|---|
| [`SH-C31A_canable2_v1.4.dfu`](https://github.com/dsdtech-official/can-adapters/releases/download/SH-C31A/fw-v1.4/SH-C31A_canable2_v1.4.dfu) | **Start here.** DfuSe format, for `dfu-util` or ST tools |
| [`SH-C31A_canable2_v1.4.bin`](https://github.com/dsdtech-official/can-adapters/releases/download/SH-C31A/fw-v1.4/SH-C31A_canable2_v1.4.bin) | Raw image, flashed at `0x08000000` |
| [`SH-C31A_canable2_v1.4.hex`](https://github.com/dsdtech-official/can-adapters/releases/download/SH-C31A/fw-v1.4/SH-C31A_canable2_v1.4.hex) | Intel HEX |
| [`SHA256SUMS.txt`](https://github.com/dsdtech-official/can-adapters/releases/download/SH-C31A/fw-v1.4/SHA256SUMS.txt) | Checksums for the three above |
| [`THIRD-PARTY-NOTICES.md`](https://github.com/dsdtech-official/can-adapters/releases/download/SH-C31A/fw-v1.4/THIRD-PARTY-NOTICES.md) | The licence notice. **Carry it with the images if you mirror them** |

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

Over USB DFU, to the STM32 system bootloader (`0483:DF11`). A USB cable is all you
need.

> Reflashing is not required for normal use.

## Licence and attribution

Built from **[`candleLight_fw_canable_v2_fd`](https://github.com/tymmothy/candleLight_fw_canable_v2_fd)**
by **Tymm Zerr** (`tymmothy`) — the CAN FD fork of candleLight for STM32G4 boards. **MIT.**

> Copyright (c) 2016 Hubert Denkmair
> Copyright (c) 2022 Ryan Edwards (changes for STM32G4 and CAN-FD)
> — [`LICENSES/MIT.txt`](../../LICENSES/MIT.txt)

> ⚠️ **Upstream describes itself as not maintained** — the repository summary reads
> *"gs_usb compatible firmware for canable v2 w/FD (not maintained)"*, and its README says
> *"This is not likely to be maintained."* We are telling you because you may want to know
> before building on it. It is still what we ship, and every measurement above was taken on
> the build we ship.

MIT requires the copyright and permission notice to be included **in binary distributions
too**, so [`THIRD-PARTY-NOTICES.md`](../../THIRD-PARTY-NOTICES.md) ships with every
firmware release. It also records two components inside that firmware which carry their own
terms — the **STM32 HAL** (BSD-style) and the **STM32 USB library**
(**ST Ultimate Liberty License SLA0044**, not an OSI-approved licence).

**If you mirror our firmware images anywhere, carry that file with them.**
