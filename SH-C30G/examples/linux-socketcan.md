<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C30G on Linux — SocketCAN

**Firmware:** candlelight (what the adapter ships with).
Nothing to install: the kernel `gs_usb` driver claims the adapter and presents it as a
standard CAN network interface.

## Check the kernel picked it up

```bash
ip link show | grep can
```

A `can0` interface means candlelight and the kernel driver are working. If you get a
`/dev/ttyACM<n>` instead, the adapter is running a serial-port firmware rather than the one
it ships with → [`docs/identify-firmware.md`](../../docs/identify-firmware.md)

## Bring the bus up

```bash
sudo ip link set can0 up type can bitrate 500000
```

⚠️ **Every node on a bus must use the same bit rate**, and the bus must be terminated at
both ends and nowhere else → [`docs/termination.md`](../../docs/termination.md)

## Watch traffic

```bash
candump can0
```

## Send a frame

```bash
cansend can0 123#DEADBEEF
```

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
