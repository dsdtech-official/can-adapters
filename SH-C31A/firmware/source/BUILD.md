<!-- SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH) -->
<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Building SH-C31A firmware v1.5 from source

The SH-C31A firmware is the open-source gs_usb firmware for CANable 2.0-class boards,
[`tymmothy/candleLight_fw_canable_v2_fd`](https://github.com/tymmothy/candleLight_fw_canable_v2_fd),
plus one patch of ours: [`SH-C31A-firmware-v1.5.patch`](SH-C31A-firmware-v1.5.patch).

## What you need

| | Version we used |
|---|---|
| Arm GNU Toolchain (`arm-none-eabi-gcc`) | **14.3.Rel1** |
| CMake | 3.31 |
| Ninja | any recent |
| git | any recent |

## Steps

```sh
git clone https://github.com/tymmothy/candleLight_fw_canable_v2_fd.git
cd candleLight_fw_canable_v2_fd
git checkout 49d96c6
git apply /path/to/SH-C31A-firmware-v1.5.patch

cmake -S . -B build -G Ninja \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_TOOLCHAIN_FILE=/path/to/toolchain-arm-none-eabi.cmake \
      -DCMAKE_C_FLAGS="-DCONFIG_LEDS_SH_C31A -DCONFIG_STRINGS_SH_C31X -DCONFIG_CLK170_SH_C31A -DCONFIG_BOOT0_DEFAULT_OFF_SH_C31A"
cmake --build build --target canable2_fw
```

The image is `build/canable2_fw.bin`. Flash it at `0x08000000`.

## What the four switches do

| Switch | Effect |
|---|---|
| `CONFIG_LEDS_SH_C31A` | LED pins of the SH-C31A board |
| `CONFIG_STRINGS_SH_C31X` | USB strings `SH-C31x` / `DSD TECH` |
| `CONFIG_CLK170_SH_C31A` | CAN kernel clock 170 MHz |
| `CONFIG_BOOT0_DEFAULT_OFF_SH_C31A` | **Everything new in v1.5** (see the release notes). Leave it out and the same patch builds v1.4 |

## Checking your build against ours

With the toolchain above, the build is byte-for-byte reproducible on our build host:

```
0fc71ea983eb59d0d8d16f8340433487884220a7c5a784602e4abaeebb5212f3  canable2_fw.bin   (v1.5, 21876 bytes)
8030b69bb7111947db2c7fdd954f17d5ad45d967f6af01418879f402f2b8804e  canable2_fw.bin   (v1.4, 19992 bytes -- without CONFIG_BOOT0_DEFAULT_OFF_SH_C31A)
```

The first line is the same file as `SH-C31A_canable2_v1.5.bin` in the release. The `.hex` and
`.dfu` files in the release carry exactly these bytes in a different container.

A different compiler version will most likely produce different bytes. We have only checked
reproducibility with the toolchain listed above.

## Licence

The upstream project and this patch are MIT-licensed. The binary also contains
STMicroelectronics' STM32 HAL and USB device library under their own licences. See the
repository's `THIRD-PARTY-NOTICES.md`.
