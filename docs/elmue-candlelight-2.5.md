<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# ElmueSoft Candlelight 2.5 on the SH-C31A and SH-C31G

Third-party firmware by **ElmueSoft**. Licence, download, thanks and support boundaries are
on [`other-firmware.md`](other-firmware.md) — **read that first**. This page is what
changes on your bench once you have flashed it.

**File:** `STM32G431-Candlelight2.5-Multiboard.dfu` · 38 215 bytes ·
`sha256 7adae1c1…4561d7`

Everything below was read off one of our own boards, not from a datasheet.
**The board was an SH-C31A.** The SH-C31G is the same microcontroller running the same
image, but we have not repeated these readings on one.

## 🔴 It reports the same USB ID as our own firmware

| | Our `v1.4` | **Candlelight 2.5** |
|---|---|---|
| VID:PID | `1D50:606F` | **`1D50:606F` — identical** |
| `bcdDevice` | `REV_0200` | **`REV_2608`** |
| Manufacturer | `DSD TECH` | `ElmueSoft (netcult.ch/elmue)` |
| Product | `SH-C31x` | `Candlelight 2.5 - Multiboard` |
| Feature bits | `0x5FB` | `0xE53B` |

**You cannot tell the two apart by VID:PID.** Any script, udev rule or driver binding that
keys on `1D50:606F` alone will match both. Use the **product string**, the `bcdDevice`
revision, or the feature bits.

On Windows the device path shows it directly — look for `REV_2608` instead of `REV_0200`.

## 🔴 The CAN clock is different, so your bit timings are too

| | Our `v1.4` | **Candlelight 2.5** |
|---|---|---|
| CAN clock | **170 MHz** | **160 MHz** |

Bit timing is derived from that clock. **A prescaler and segment configuration that gives
you an exact rate on our firmware will not necessarily give you the same rate here**, and
the set of rates that land exactly is a different set.

**Read the rate back after you bring the interface up.** On Linux:

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
