#!/bin/bash
set -e

# Toolchains
EXEC_DIRECTORY=$(realpath .)
TOOLCHAIN_DIRECTORY="${EXEC_DIRECTORY}/../toolchains/"

# Find the toolchains
for entry in "$TOOLCHAIN_DIRECTORY"/*
do
    if [[ $entry == *"aarch64-none-elf"* ]]
    then
        aarch64_none_dir=$entry
    elif [[ $entry == *"arm-none-eabi"* ]]
    then 
        aarch32_eabi_dir=$entry
    elif [[ $entry == *"riscv64"* ]]
    then 
        riscv64_dir=$entry
    fi
done

AARCH64_NONE_TOOLCHAIN=$aarch64_none_dir"/bin/aarch64-none-elf-"
AARCH32_EABI_TOOLCHAIN=$aarch32_eabi_dir"/bin/arm-none-eabi-"
RISCV64_TOOLCHAIN=$riscv64_dir"/bin/riscv64-unknown-elf-"

FREERTOS_DIRECTORY="../freertos-bao-fpmc/"
BAREMETAL_DIRECTORY="../baremetal-bao-fpmc"
IMAGE_BUILD_DIRECTORY="../images/build"

# Supported architectures
ARCHITECTURES=("zcu102" "zcu104" "imx8qm" "tx2" "rpi4" "qemu-aarch64-virt" "fvp-a" "fvp-r" "fvp-a-aarch32" "fvp-r-aarch32" "qemu-riscv64-virt")

# Input arguments and exact regex
architecture_value=${1}
architecture_regex="\<${architecture_value}\>"
build_value=${2}
build_freertos=0
build_baremetal=0

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
if [[ "$architecture_value" == "qemu-riscv64-virt" ]]
then
    TOOLCHAIN=${RISCV64_TOOLCHAIN}
    ARCH_SELECTED=riscv64
elif [[ "$architecture_value" == "fvp-a-aarch32" ]] || [[ "$architecture_value" == "fvp-r-aarch32" ]]
then
    TOOLCHAIN=${AARCH32_EABI_TOOLCHAIN}
    ARCH_SELECTED=aarch32
else 
    TOOLCHAIN=${AARCH64_NONE_TOOLCHAIN}
    ARCH_SELECTED=aarch64
fi

# Looking which image to build
if [[ "$build_value" == "both" ]]
then
    build_freertos=1
    build_baremetal=1
elif [[ "$build_value" == "freertos" ]]
then 
    build_freertos=1
elif [[ "$build_value" == "baremetal" ]]
then
    build_baremetal=1
else
    echo "Build value incorrect, valid values: baremetal, freertos, both..."
    exit 1
fi

# Create build dir if it doesn't exist
if [ ! -d $IMAGE_BUILD_DIRECTORY ]
then
    mkdir "$IMAGE_BUILD_DIRECTORY"
fi

# Exporting variables
export CROSS_COMPILE=$TOOLCHAIN
export PLATFORM=$architecture_value
export ARCH=$ARCH_SELECTED

# Build freertos
if [[ $build_freertos == 1 ]]
then
    make -C "$FREERTOS_DIRECTORY" STD_ADDR_SPACE=y
    cp "$FREERTOS_DIRECTORY/build/$PLATFORM/freertos.bin" "$IMAGE_BUILD_DIRECTORY/freertos_hyp.bin"
fi 

# Build baremetal
if [[ $build_baremetal == 1 ]]
then
    make -C "$BAREMETAL_DIRECTORY"
    cp "$BAREMETAL_DIRECTORY/build/$PLATFORM/baremetal.bin" "$IMAGE_BUILD_DIRECTORY/baremetal_hyp.bin"
fi
