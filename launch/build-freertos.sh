#!/bin/bash
set -e

# Toolchains
EXEC_DIRECTORY=$(realpath .)
TOOLCHAIN_DIRECTORY="${EXEC_DIRECTORY}/../toolchains/"
AARCH64_NONE_TOOLCHAIN="arm-gnu-toolchain-13.2.Rel1-x86_64-aarch64-none-elf/bin/aarch64-none-elf-"
AARCH32_EABI_TOOLCHAIN="arm-gnu-toolchain-13.2.Rel1-x86_64-arm-none-eabi/bin/arm-none-eabi-"
RISCV64_TOOLCHAIN="riscv64-unknown-elf-toolchain-10.2.0-2020.12.8-x86_64-linux-ubuntu14/bin/riscv64-unknown-elf-"

IMAGE_BUILD_DIRECTORY="../images/build"

# Supported architectures
ARCHITECTURES=("zcu102" "zcu104" "imx8qm" "tx2" "rpi4" "qemu-aarch64-virt" "fvp-a" "fvp-r" "fvp-a-aarch32" "fvp-r-aarch32" "qemu-riscv64-virt")

# Input arguments and exact regex
architecture_value=${1}
architecture_regex="\<${architecture_value}\>"

# Getting architecture
if [[ ! ${ARCHITECTURES[*]} =~ $architecture_regex ]]
then
    echo "Architecture not set or does not exist"
    echo "List of supported architectures:"
    (IFS="|$IFS"; printf '%s\n' "${ARCHITECTURES[*]}")
    echo "Try \"./modified-bao-demo.sh qemu-aarch64-virt\" for example..."
    exit 1
fi

# Choosing toolchain
TOOLCHAIN=${TOOLCHAIN_DIRECTORY}
if [[ "$architecture_value" == "qemu-riscv64-virt" ]]
then
    TOOLCHAIN=${TOOLCHAIN}${RISCV64_TOOLCHAIN}
    ARCH_SELECTED=riscv64
elif [[ "$architecture_value" == "fvp-a-aarch32" ]] || [[ "$architecture_value" == "fvp-r-aarch32" ]]
then
    TOOLCHAIN=${TOOLCHAIN}${AARCH32_EABI_TOOLCHAIN}
    ARCH_SELECTED=aarch32
else 
    TOOLCHAIN=${TOOLCHAIN}${AARCH64_NONE_TOOLCHAIN}
    ARCH_SELECTED=aarch64
fi

# Exporting variables
export CROSS_COMPILE=$TOOLCHAIN
export PLATFORM=$architecture_value
export ARCH=$ARCH_SELECTED

# Build freertos (TODO Change)
make -C ../freertos-over-bao STD_ADDR_SPACE=y

# Create build dir if it doesn't exist
if [ ! -d $IMAGE_BUILD_DIRECTORY ]
then
    mkdir "$IMAGE_BUILD_DIRECTORY"
fi

# Copy image
cp "../freertos-over-bao/build/$PLATFORM/freertos.bin" "$IMAGE_BUILD_DIRECTORY/freertos_hyp.bin"