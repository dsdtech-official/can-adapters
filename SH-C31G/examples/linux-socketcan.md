<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C31G on Linux — SocketCAN

Nothing to install: the kernel `gs_usb` driver claims the adapter and presents it as a
standard CAN network interface.

> ## Before anything else: **which firmware is on this adapter?**
>
> SH-C31G has shipped with **two different firmwares**, both of which are in the field
> today, and **you cannot tell them apart by looking at the board**.
>
> 🔴 **This is not a cosmetic difference.** The older firmware **reports `listen-only`
> support and does not honour it** — ask it to stay silent and it transmits and
> acknowledges anyway. On a vehicle or a customer's bus that is a real hazard.
> It also has no CAN FD. **Identify first.**

## Check the kernel picked it up

```bash
ip link show | grep can
```

A `can0` interface means the kernel driver has it. If nothing appears, check which
firmware you have → [`../firmware/`](../firmware/)

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

| `bcdDevice` | `product` | This is |
|---|---|---|
| `0200` | `SH-C31x` | the firmware a **new** adapter ships with |
| `0000` | `canable2 gs_usb` | an adapter made **before September 2026** |
| `0000` · `0100` | `candleLight USB to CAN adapter` · `SH-C30x` | ⚠️ **not this product** — that is an SH-C30A |

📖 **The full table, what differs between the two, and the rules for reading any of
it are in [`README.md`](README.md)** — one place, so there is only one to keep right.

> 🔴🔴 **If you have the older one, read this twice.**
> `ip link set can0 up type can bitrate 500000 listen-only on` **succeeds and does not
> make the adapter silent.** It transmits and acknowledges anyway — no error, no warning.
> If you need a guaranteed silent node, use an adapter on the current firmware, or verify
> with a witness node on a bus you own. **It also has no CAN FD**, so the kernel refuses
> `fd on` outright, and **an echo is not proof of transmission on it**.
>
> **An RX LED that never lights while traffic is clearly arriving is a strong hint.**

> 🔴 **And if you have the current one:** closing the channel does **not** discard
> queued frames. `ip link set can0 down` with frames still queued, then up again, and they
> go out — into whatever bus you are attached to by then. **Drain before you take the
> interface down.** The older firmware discards them instead. ⛔ **Do not carry a
> workaround for one over to the other.**


## Classic CAN

```bash
sudo ip link set can0 up type can bitrate 500000
candump can0
cansend can0 123#DEADBEEF
```

⚠️ **Every node on a bus must use the same bit rate**, and the bus must be terminated at
both ends and nowhere else → [`docs/termination.md`](../../docs/termination.md)

> ⚠️ **`cansend` returning does not mean the frame reached the bus.** With no other node
> to acknowledge, the controller retransmits indefinitely, the transmit error counter
> climbs to 128 and the controller goes error-passive; it never reaches bus-off. Nothing
> is printed. To see it:
>
> ```bash
> ip -details -statistics link show can0 | grep -A2 -E 'state|bus_error'
> candump can0,#FFFFFFFF          # error frames as well as data frames
> ```
>
> 🔴 **On the older firmware, an echo is not proof either** — see [`README.md`](README.md).

Measured on the current firmware **on an SH-C31A** — same image, no isolation in
the signal path (see the provenance note under CAN FD) — each rate read back and each
frame verified:

| Nominal rate | |
|---|---|
| 10 k · 125 k · 250 k · 500 k · 1 M | ✅ **0.0000 % loss**, no transmit errors |

> Those same 125 k and 250 k rates **cannot be opened from python-can's `gs_usb`
> backend** on this board. That is a limit of the host library's bit-timing solver, not of
> the adapter — see [`python-gsusb.py`](python-gsusb.py).

## CAN FD

🔴 **Current firmware only.** On the older one the kernel refuses `fd on`, because it does not report
the capability. That is not a configuration problem and there is no flag that works
around it.

Two rates: the **nominal** rate carries the arbitration field, the **data** rate carries
the payload once the bus has been won.

```bash
sudo ip link set can0 down
sudo ip link set can0 up type can bitrate 500000 dbitrate 2000000 fd on
```

> 🔴 **That `down` then `up` is exactly the sequence the firmware table warns about.**
> On the current firmware, frames still queued when you take the interface down are **not discarded** —
> they go out after you bring it back up, at the new bit rate. Drain the interface before
> reconfiguring it.

Send a 64-byte frame with bit rate switching — `##` marks an FD frame, and the digit after
it is the flag field, where `1` is BRS:

```bash
cansend can0 123##1112233445566778899AABBCCDDEEFF00112233445566778899AABBCCDDEEFF0011223344556677
```

`candump can0` shows FD frames without any extra flag.

> 🔴 **Always read the rate back.** `ip link set ... up` exits `0` even when it could not
> hit the rate you asked for. Asking for `dbitrate 4000000` gives **3 953 488** — the
> divisors cannot land on 4 Mbit/s exactly, and nothing complains.
>
> ```bash
> ip -details link show can0 | grep -E 'bitrate|dbitrate'
> ```
>
> Same arithmetic, same trap, at **800 kbit/s** nominal: this board's 170 MHz clock cannot
> produce exactly 800 k either. If you must share a bus with a node that is at *exactly*
> 800 k, check the read-back on both ends before you trust it.

Measured on the current firmware **on an SH-C31A**, each rate read back and verified
byte for byte over 64-byte payloads:

| Data rate | |
|---|---|
| 1 M · 2 M · 2.5 M | ✅ 8/8 frames |
| 3.4 M | ✅ 8/8 |
| 5 M | ✅ 8/8 — the transceiver's ceiling |

A 180-second bidirectional soak at 2 Mbit/s moved **17548 frames with none lost**.

> **On provenance:** both tables above were taken on an **SH-C31A** — same microcontroller,
> same image, but **no isolation in the signal path**. What has been run on the SH-C31G
> itself is CAN FD with the isolation in circuit, including an extended soak. Every part in
> this board's signal path is rated for 5 Mbit/s. We will publish a sweep taken on this
> board when we have one.

### 🔴 The FD failure you will actually hit: mismatched sample points

Both ends of an FD link must agree on the **data-phase sample point**, not just on the
data rate. The sample point is computed by the **host**, from the bit-timing limits the
device reports — there is no such setting in the firmware.

Measured: with the two ends **12 percentage points apart**, FD traffic went **0 out of
50** and the receiver went error-passive — while **classic frames over the same wiring,
same session, went 50 out of 50**.

> ⛔ **So never use classic traffic to prove the bus is healthy before blaming CAN FD.**
> It proves nothing about the data phase. Read the sample point back on both ends:
>
> ```bash
> ip -details link show can0 | grep -E 'sample-point|dsample-point'
> ```

## Throughput: there is a limit on frames in flight

The adapter holds a fixed pool of frame objects. Push more unacknowledged frames at it
than the pool holds and the extra ones are **dropped silently** — no overflow bit, no
error frame, no error counter. Measured ceiling on the current firmware: **30 frames in
flight**. A host that keeps more than that outstanding will lose frames and will not be
told.

## Take the bus down

```bash
sudo ip link set can0 down
```

🔴 **On the current firmware, drain first** — see the note under [Identify the firmware](#identify-the-firmware).

---

`candump` and `cansend` come from **can-utils** (`sudo apt install can-utils`).

