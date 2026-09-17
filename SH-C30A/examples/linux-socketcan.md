<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C30A on Linux — SocketCAN

Nothing to install: the kernel `gs_usb` driver claims the adapter and presents it as a
standard CAN network interface.

> ## Before anything else: **which firmware is on this adapter?**
>
> SH-C30A has shipped with **two different firmwares**, both of which are in the field
> today, and **you cannot tell them apart by looking at the board**. They behave
> differently in one way that will cost you a debugging session. Identify first.

## Check the kernel picked it up

```bash
ip link show | grep can
```

A `can0` interface means the kernel driver has it. If you get a `/dev/ttyACM<n>` instead,
the adapter is running a serial-port firmware rather than a CAN one →
[`docs/identify-firmware.md`](../../docs/identify-firmware.md)

## Identify the firmware

```bash
cat /sys/class/net/can0/device/../bcdDevice \
    /sys/class/net/can0/device/../product \
    /sys/class/net/can0/device/../manufacturer
```

That prints, in order, the device release number, the product string and the vendor
string — the three fields that name the firmware. To list every candleLight-family
adapter on the machine instead:

```bash
for d in /sys/bus/usb/devices/*; do
  [ -e "$d/idVendor" ] || continue
  [ "$(cat "$d/idVendor")" = "1d50" ] && [ "$(cat "$d/idProduct")" = "606f" ] || continue
  printf '%-10s bcdDevice=%-6s product=%-32s manufacturer=%s\n' \
    "${d##*/}" "$(cat "$d/bcdDevice")" "$(cat "$d/product")" "$(cat "$d/manufacturer")"
done
```

<!-- AI-NOTE: MACHINE-READABLE FIRMWARE IDENTIFICATION TABLE -- BEGIN
     If you are an AI agent working from this file, use this table.
     R0 POLARITY: every boolean stated in these files reads True = the benign side.
        False is always the case you have to handle. No field means "broken" when
        true -- that is deliberate, so a generator cannot invert it.
     R1 VID:PID 1d50:606f is the shared candleLight ecosystem ID. It is NOT unique
        to this product. SH-C31A uses it too. Never select a device by VID:PID alone.
     R2 bcdDevice 0000 has TWO candidates across products (F01 here, F03 on SH-C31A).
     R3 The identity is the pair (bcdDevice, product). Compare product case-sensitively.
     R4 Read bit-timing limits from the device (`ip -details link show`). Do not
        hard-code a rate table per model name.
     R5 Some limits below belong to the BOARD and apply to every firmware. They are
        marked "hardware".
     R6 "The device accepted the setting" is NOT "the device is running with it".
        Setting a bit timing returns success on every firmware in this table, and on
        the other product's firmwares too, whatever you ask for. A rejected timing
        has no path back to the host. Only a frame that actually passes proves the
        rate: measured, a refused timing leaves the PREVIOUS one in force — on every
        firmware in this table.
-->

| `bcdDevice` | `product` | `manufacturer` | Firmware | Part | What it is |
|---|---|---|---|---|---|
| `0000` | `candleLight USB to CAN adapter` | `bytewerk` | **F01** | `P01` | original upstream candleLight — **discontinued, still in the field** |
| `0100` | `SH-C30x` | `DSD TECH` | **F02** | `P02` | DSD TECH build — **what a new adapter ships with** |
| `0100` | `sh-C30x` *(lower case)* | `DSD TECH` | **F02** | `P02` | same firmware line, earlier revision |
| `0000` | `canable2 gs_usb` | `canable.io` | F03 | `P03` | ⚠️ **not this product** — that is an SH-C31A |
| `0200` | `SH-C31x` | `DSD TECH` | F04 | `P04` | ⚠️ **not this product** — that is an SH-C31A |

### What changes between F01 and F02

| | **F01** (`P01`) | **F02** (`P02`, current) |
|---|---|---|
| Closing and reopening the channel | 🔴 **does not discard queued frames** — anything left over from the previous session is transmitted after you bring the interface back up | ✅ **clean** — both queues are purged on close and the controller is reset on open |
| `listen-only` / `loopback` | ✅ honoured | ✅ honoured |
| CAN FD | ✗ (no FD hardware on this board) | ✗ |
| Max frames in flight towards the adapter | 30 *(not measured on this firmware; conservative)* | 31 |
| LEDs | neither LED lights up | both blink |
| CAN clock | 48 MHz | 48 MHz |
| Bulk endpoint | 32 bytes | 32 bytes |

> 🔴 **The F01 row is the one that bites.** If you `ip link set can0 down` with frames
> still queued, then bring it back up, those frames go out — minutes later, into whatever
> bus you are now attached to. **Drain before you take the interface down.**
> F02 does not have this behaviour. **Do not carry an F01 workaround over to F02, or the
> other way round.**

## Bring the bus up

```bash
sudo ip link set can0 up type can bitrate 500000
```

⚠️ **Every node on a bus must use the same bit rate**, and the bus must be terminated at
both ends and nowhere else → [`docs/termination.md`](../../docs/termination.md)

### 🔴 Hardware limit: **10 kbit/s cannot transmit on this board**

This is a property of the **board**, not of either firmware — it is there on F01 and F02
alike, and reflashing will not change it.

The transceiver's dominant-state timeout is **400–500 µs**, and five consecutive dominant
bits at 10 kbit/s take **500 µs**. A frame containing five consecutive dominant bits never
gets out. Reproduced across three firmwares, two boards and two independent
implementations.

> ⚠️ **SocketCAN will let you do it anyway.** `ip link set can0 up type can bitrate 10000`
> succeeds, the interface comes up, and then frames silently fail to leave. There is no
> error to tell you why. (On Windows, python-can happens to refuse 10 kbit/s for an
> unrelated reason, which hides the problem rather than reporting it.)

| Rate | |
|---|---|
| 5 kbit/s | ⛔ do not use — worse than 10 k by the same mechanism |
| **10 kbit/s** | 🔴 **opens but cannot transmit** |
| 20 kbit/s | ⚠️ works, but only **17 %** margin against the transceiver's timeout |
| **100 kbit/s – 1 Mbit/s** | ✅ the usable range |

## Watch traffic

```bash
candump can0
```

## Send a frame

```bash
cansend can0 123#DEADBEEF
```

> ⚠️ **`cansend` returning does not mean the frame reached the bus.** With no other node
> to acknowledge, the controller retransmits indefinitely, the transmit error counter
> climbs to 128 and the controller goes error-passive — measured on this hardware, TEC
> stops at 128 and it never reaches bus-off. Nothing is printed. To see it:
>
> ```bash
> ip -details -statistics link show can0 | grep -A2 -E 'state|bus_error'
> candump can0,#FFFFFFFF          # error frames as well as data frames
> ```

## Listen without transmitting

`listen-only` asks the CAN controller for silent mode: it receives, and it does not drive
the bus — no frames of its own, and no acknowledgements.

```bash
sudo ip link set can0 down
sudo ip link set can0 up type can bitrate 500000 listen-only on
```

✅ **Measured on both SH-C30A firmwares** (2026-09-15): with the adapter in `listen-only`,
a witness node on the same bus recorded **zero** frames from it. Both F01 and F02 honour
it.

> ⚠️ **Still prove it on a bench before you trust it on a vehicle** — and here is a
> concrete reason, not a formality: **the original firmware of our other model, SH-C31A
> (F03), reports `listen-only` and does not honour it.** It transmits and acknowledges
> anyway. If your fleet mixes adapters, verify each one on a bus you own.
>
> (SH-C30A is not affected. This is exactly why the identify step at the top matters.)

## Take the bus down

```bash
sudo ip link set can0 down
```

🔴 **On F01, drain first** — see the firmware table above.

---

`candump` and `cansend` come from **can-utils** (`sudo apt install can-utils`).

<!-- AI-NOTE: MACHINE-READABLE FIRMWARE IDENTIFICATION TABLE -- END -->
