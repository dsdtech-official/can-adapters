<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# SH-C31A on Linux — SocketCAN

**Firmware:** candlelight (what the adapter ships with).
Nothing to install: the kernel `gs_usb` driver claims the adapter and presents it as a
standard CAN network interface.

## Check the kernel picked it up

```bash
ip link show | grep can
```

A `can0` interface means candlelight and the kernel driver are working. If you get a
`/dev/ttyACM<n>` instead, the adapter is running slcan — see
[`python-slcan.py`](python-slcan.py).

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

Useful on a live vehicle bus, where an unexpected transmission is not welcome. The adapter
never sends anything, not even acknowledgements:

```bash
sudo ip link set can0 down
sudo ip link set can0 up type can bitrate 500000 listen-only on
```

## Take the bus down

```bash
sudo ip link set can0 down
```

`candump` and `cansend` come from **can-utils** (`sudo apt install can-utils`).
