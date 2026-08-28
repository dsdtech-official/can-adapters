<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C31A on Linux — SocketCAN

**Firmware:** our `v1.4` gs_usb build, what the adapter ships with.
Nothing to install: the kernel `gs_usb` driver claims the adapter and presents it as a
standard CAN network interface. **CAN FD included.**

## Check the kernel picked it up

```bash
ip link show | grep can
```

A `can0` interface means the kernel driver has it. If nothing appears, check which
firmware you have → [`../firmware/`](../firmware/)

## Classic CAN

```bash
sudo ip link set can0 up type can bitrate 500000
candump can0
cansend can0 123#DEADBEEF
```

⚠️ **Every node on a bus must use the same bit rate**, and the bus must be terminated at
both ends and nowhere else → [`docs/termination.md`](../../docs/termination.md)

## CAN FD

Two rates: the **nominal** rate carries the arbitration field, the **data** rate carries
the payload once the bus has been won.

```bash
sudo ip link set can0 down
sudo ip link set can0 up type can bitrate 500000 dbitrate 2000000 fd on
```

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

Measured on this adapter, each rate read back and verified byte for byte over 64-byte
payloads:

| Data rate | |
|---|---|
| 1 M · 2 M · 2.5 M | ✅ 8/8 frames |
| 3.4 M | ✅ 8/8 |
| 5 M | ✅ 8/8 — the transceiver's ceiling |

A 180-second bidirectional soak at 2 Mbit/s moved **17548 frames with none lost**.

Nominal rates 10 k, 125 k, 250 k, 500 k and 1 M all carry traffic at 0.0000 % loss here.

## Listen without transmitting

`listen-only` asks the CAN controller for silent mode: it receives, and it does not drive
the bus — no frames of its own, and no acknowledgements.

```bash
sudo ip link set can0 down
sudo ip link set can0 up type can bitrate 500000 listen-only on
```

> ⚠️ **Prove it on a bench before you trust it on a vehicle.** Silent mode is a property of
> the controller and this is the standard way to ask for it, but we have not put an
> analyser on this adapter to confirm it stays quiet. If one stray acknowledgement would
> matter on the bus you are about to join, verify on a bus you own first.

## Take the bus down

```bash
sudo ip link set can0 down
```

`candump` and `cansend` come from **can-utils** (`sudo apt install can-utils`).
