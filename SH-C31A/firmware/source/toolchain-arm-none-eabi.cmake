# SPDX-FileCopyrightText: 2026 DongGuan DESHIDE TECHNOLOGY CO., LTD (DSD TECH)
# SPDX-License-Identifier: MIT
#
# Minimal CMake toolchain file for arm-none-eabi-gcc. Used instead of the one
# shipped upstream, which hard-codes a GCC 8 install path. Point it at your
# toolchain with the TOOLCHAIN_BIN_DIR environment variable, or put
# arm-none-eabi-gcc on PATH.

set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)
set(CMAKE_C_COMPILER_TARGET arm-none-eabi)

find_program(CMAKE_C_COMPILER
	NAMES ${CMAKE_C_COMPILER_TARGET}-gcc
	HINTS ENV TOOLCHAIN_BIN_DIR
	DOC "Path to the ARM toolchain binaries"
)
if(NOT CMAKE_C_COMPILER)
	message(FATAL_ERROR "arm-none-eabi-gcc not found. Set TOOLCHAIN_BIN_DIR or add it to PATH.")
endif()

set(CMAKE_ASM_COMPILER "${CMAKE_C_COMPILER}")

set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)

set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
