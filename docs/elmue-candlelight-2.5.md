<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# ElmueSoft Candlelight 2.5 on the SH-C31A and SH-C31G

Third-party firmware by **ElmueSoft**. Licence, download, thanks and support boundaries are
on [`other-firmware.md`](other-firmware.md) — **read that first**. This page is what
changes on your bench once you have flashed it.

**File:** `STM32G431-Candlelight2.5-Multiboard.dfu` · 38 107 bytes ·
`sha256 79d438f5…870480`

> 🔴 **This is a snapshot of commit `eb1c7e35` (2026-09-15), not the latest build.**
> Elmue's own pages always have the current one — see
> [`other-firmware.md`](other-firmware.md#download), which also lists what changed since our
> previous snapshot.

Everything below was read off one of our own boards, not from a datasheet.
> ℹ️ **Which build these readings came from:** commit `e862f6a6`, the snapshot this page
> carried until 2026-09-17. They have not been repeated on the current build. Nothing here
> is expected to have moved, but we have not re-read it, so we say so.
**The board was an SH-C31A.** The SH-C31G is the same microcontroller running the same
image, but we have not repeated these readings on one.

## 🔴 It reports the same USB ID as our own firmware

| | Our `v1.4` | **Candlelight 2.5** |
|---|---|---|
| VID:PID | `1D50:606F` | **`1D50:606F` — identical** |
| `bcdDevice` | `REV_0200` — ours, fixed | ⚠️ **carries his build version and moves every release — ⛔ do not identify by it** |
| Manufacturer | `DSD TECH` | `ElmueSoft (netcult.ch/elmue)` |
| Product | `SH-C31x` | `Candlelight 2.5 - Multiboard` |
| Feature bits | `0x5FB` | `0xE53B` |

**You cannot tell the two apart by VID:PID.** Any script, udev rule or driver binding that
keys on `1D50:606F` alone will match both. Use the **product string**, the `bcdDevice`
revision, or the feature bits.

On Windows, Device Manager shows the product string — look for **`Candlelight 2.5 - …`** rather than **`SH-C31x`**.

## 🔴 The CAN clock is different, so your bit timings are too

| | Our `v1.4` | **Candlelight 2.5** |
|---|---|---|
| CAN clock | **170 MHz** | **160 MHz** |

Bit timing is derived from that clock. **Normally this is not your problem:** a gs_usb host
asks the device for its clock and its timing limits and computes the prescaler and segments
from the answer, so both builds simply work. The Linux `gs_usb` driver does this, and so
does any correctly written host.

⛔ **It becomes your problem with software that assumes a fixed clock.** That software
programs timings computed for 170 MHz onto a 160 MHz device — the rate and the sample point
both come out wrong, and **the controller goes bus-off as soon as it sees traffic.** It does
not degrade gracefully into "a slightly different rate".

**So read the rate back after you bring the interface up.** On Linux:

```bash
ip -details link show can0 | grep -E 'bitrate|dbitrate'
```

## What it adds

These are Elmue's own extensions, and our build has none of them:

| | |
|---|---|
| `GET_STATE` | query the controller's current state |
| Board information | identify the board, its clock, whether a crystal is in use |
| Filters | hardware acceptance filtering |
| Pin control | read and drive MCU pins |
| Flash read/write | read and write the device's flash |
| Bus load | reported by the firmware |
| USB blob transfer | bulk transfers for the above |

## What it does not have

| | |
|---|---|
| `TRIPLE_SAMPLE` | absent |
| `USER_ID` | absent |
| `PAD_PKTS` | absent |
| `TERMINATION` | absent — the software command is rejected. **The 120 Ω switch on the board is hardware and works regardless** |
| `BERR_REPORTING` | absent as a capability bit — **but it pushes error frames to the host on its own** |

## Two things that will look like faults and are not

**① It reports three CAN channels. The board has one.**

The firmware is a multi-board build and advertises `Channels: 3`. **Our hardware has a
single CAN transceiver.** Channels 2 and 3 do not exist physically. Software that
enumerates channels will show three; use the first.

*(The Slcan 2.5 build on the same hardware reports `1`.)*

**② A host application that transmits without reading will lose frames.**

The firmware holds an internal frame pool. Ours holds 64 frames; **this one holds 71**.
Either way, an application that transmits continuously and never calls `recv` fills the
pool and then drops nearly everything after it.

**This is not a defect specific to this firmware** — our own build behaves the same way
with a slightly smaller pool. **Read while you write.**

## Crystal

The firmware reports `Quartz_In_Use = False`, which is correct: **neither the SH-C31A nor
the SH-C31G has a crystal fitted.** The MCU runs from its internal oscillator.

⛔ **Do not flash a variant built for a 25 MHz crystal onto these boards.** Upstream ships
several, and the `Multiboard` build named at the top of this page is the one for hardware
without a crystal.

## Going back to our firmware

Same DFU procedure, and the bootloader is in ROM and is never overwritten →
[`other-firmware.md`](other-firmware.md#flashing)
