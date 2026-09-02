<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# LEDs — what the three lights mean

Every adapter in this repository has three LEDs: **one red, two green** — and on every
one of them the red is power, and the greens are TX and RX.

| Light | Colour | Driven by | Says |
|---|---|---|---|
| **Power** | red | the 3.3 V rail, directly | The board has USB power |
| **TX** | green | the firmware, one wink per frame **sent** | |
| **RX** | green | the firmware, one wink per frame **received** | |

The red one is wired anode to 3.3 V through a resistor, cathode to ground. No pin of the
microcontroller touches it, so it lights whenever the on-board regulator has power —
including in bootloader mode, and with no firmware at all. **It tells you the adapter has
power and nothing else.**

## What the two green ones actually do

| Situation | Both greens |
|---|---|
| The moment you plug it in | flicker alternately for about half a second, then go out |
| Plugged in, nothing has opened the CAN channel | **dark** |
| Bootloader (DFU) mode | **dark** — the CAN firmware is not running |
| Channel open, bus idle | **lit, steady** |
| Channel open, traffic | lit, winking dark for 30 ms per frame |
| Channel closed again, or the host suspends the port | dark |

Two rows in that table account for most of the "my adapter's lights are wrong" reports.

**① Dark green LEDs are normal.** They are not power lights — the red one is. They stay
out until an application opens the channel: `ip link set can0 up` on Linux, or whatever
your Windows software calls *connect* / *open*. Red on and both greens out is a healthy
idle adapter.

**② Steady green means open, not stuck.** Once the channel is open both greens sit lit
and *wink off* on activity, which is the opposite of what most people expect. An idle open
adapter looks like two solid green lights.

Under a real load the wink stops tracking frames. A wink is 30 ms dark, and the next one
cannot start for 45 ms, so anything faster than about 20 frames per second settles into a
flicker of roughly 30 ms dark and 15 ms lit — steady, and no longer proportional to the
bus load.

## Which green is TX and which is RX

Both greens are the same part, so colour will not separate them. Hold the board **component
side up with the USB plug pointing left**:

**SH-C30A and SH-C30L** — the two greens sit one above the other, a little right of centre.
The red one is off to their right, towards the screw terminal.

| | |
|---|---|
| upper green | **TX** |
| lower green | **RX** |

**SH-C31A** — all three sit in one vertical line, a little right of centre.

| | |
|---|---|
| top green | **RX** |
| middle green | **TX** |
| bottom red | **power** |

**SH-C30G and SH-C31G** are the same layout as each other: the three sit in one vertical
line near the edge furthest from the screw terminal. Hold the board with **the screw
terminal on the right**:

| | |
|---|---|
| top green | **RX** |
| middle green | **TX** |
| bottom red | **power** |

**The boards are not all laid out the same way.** Do not carry the habit from one to
another.

If you would rather confirm it than count LEDs: open the channel with nothing else
connected to the CAN terminal and transmit a frame. Only the TX light responds — with no
second node there is nothing to receive, and nothing to acknowledge the frame either, so
the controller keeps retrying and the TX light keeps winking.

On **every** board the schematic calls them `LED1` (red, power), `LED2` (green, TX) and
`LED3` (green, RX) — [SH-C30A](../SH-C30A/hardware/) · [SH-C30G](../SH-C30G/hardware/) · [SH-C30L](../SH-C30L/hardware/) · [SH-C31A](../SH-C31A/hardware/) · [SH-C31G](../SH-C31G/hardware/).

## Identify

The gs_usb protocol has an *identify* request, for picking one adapter out of several on a
bench. While it is active the two greens alternate at 100 ms each until you switch it off.
On Linux the `gs_usb` driver exposes it through `ethtool -p can0`; other hosts expose it
only if their software chooses to.

## When the greens never light at all

Two shipped firmware builds drive the wrong pins for these boards. Both are cosmetic — CAN
traffic is unaffected — and both are fixed in the current build.

| Board | Symptom | |
|---|---|---|
| **SH-C30A** | neither green ever lights, whatever you do | Fixed in **v2.1** |
| **SH-C31A** | TX winks, **RX never does** | Fixed in **v1.4** |

Adapters reach you through distribution, so a recently bought one can still be older stock.
Neither is a hardware fault, and reflashing is optional — see
[SH-C30A firmware](../SH-C30A/firmware/) · [SH-C31A firmware](../SH-C31A/firmware/).
