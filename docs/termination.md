<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Termination — when to switch the 120 Ω resistor OFF

**This is the single most common cause of "it doesn't work" reports.**

## The rule

A CAN bus needs **exactly two** 120 Ω terminating resistors, one at **each physical end**
of the bus. Not one. Not three.

| Your situation | Adapter's 120 Ω |
|---|---|
| Connecting to a **vehicle**, machine, or any existing bus | **OFF** — that bus is already terminated at both ends |
| Adapter + **one** other device on a short bench cable, and that device is terminated | **ON** — your adapter is the second end |
| Adapter + **one** other device, neither terminated | **ON**, and terminate the other end too |
| Adapter tapped into the **middle** of an existing bus | **OFF** |

## What goes wrong

**Three or more terminators** (≈40 Ω or less total): the dominant bits cannot be driven
hard enough. Symptoms: nothing received at all, or a flood of error frames, or
transmissions that never get acknowledged. Adding your adapter to a car with its
termination ON is the classic case.

**One or zero terminators** (≈120 Ω or open): reflections on the cable corrupt bit
sampling. Symptoms: works at 125 kbit but fails at 500 kbit or 1 Mbit; works with a
10 cm cable but not a 2 m one; intermittent CRC errors.

## How to check

With everything **powered off**, measure resistance between CAN_H and CAN_L:

| Measured | Meaning |
|---|---|
| **~60 Ω** | Correct — two 120 Ω resistors in parallel |
| ~120 Ω | Only one terminator — add one at the far end |
| ~40 Ω | Three terminators — switch one off |
| open / very high | None — add two |

## Other things that look like a termination fault

- **Bitrate mismatch.** Every node on a CAN bus must use the same bitrate. A wrong
  bitrate looks identical to a wiring fault from the host side.
- **CAN_H and CAN_L swapped.** No damage, but no communication.
- **No common ground.** The 3-pin terminal has GND for a reason. Connect it.
- **A bus with only one node.** Classic CAN needs at least one other node to acknowledge
  a frame; a lone transmitter will retry forever. Use loopback or listen-only mode to
  test a single adapter.
