#!/bin/bash

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

ARCHITECTURES=("zcu102" "zcu104" "imx8qm" "tx2" "rpi4" "qemu-aarch64-virt" "fvp-a" "fvp-r" "fvp-a-aarch32" "fvp-r-aarch32" "qemu-riscv64-virt")

# Input arguments and exact regex
architecture_value=${1}
architecture_regex="\<${architecture_value}\>"

demo_value=${2}
if [ -z "${demo_value}" ]
then
    demo_value="baremetal"
fi

# Getting architecture
if [[ ! ${ARCHITECTURES[*]} =~ $architecture_regex ]]
then
    echo "Architecture does not exist"
    echo "List of supported architectures:"
    (IFS="|$IFS"; printf '%s\n' "${ARCHITECTURES[*]}")
    echo "Try \"./bao-demo.sh qemu-aarch64-virt\" for example..."
    exit 1
fi

# Choosing toolchain
if [[ "$architecture_value" == "qemu-riscv64-virt" ]]
then
    TOOLCHAIN=${RISCV64_TOOLCHAIN}
    ARCH=riscv64
elif [[ "$architecture_value" == "fvp-a-aarch32" ]] || [[ "$architecture_value" == "fvp-r-aarch32" ]]
then
    TOOLCHAIN=${AARCH32_EABI_TOOLCHAIN}
    ARCH=aarch32
else 
    TOOLCHAIN=${AARCH64_NONE_TOOLCHAIN}
    ARCH=aarch64
fi

export CROSS_COMPILE=$TOOLCHAIN
export PLATFORM=$architecture_value
export DEMO=$demo_value
export ARCH=$ARCH

make -j1 -C ../bao-demos/ 

if [[ "$architecture_value" == "qemu-riscv64-virt" ]] || [[ "$architecture_value" == "qemu-aarch64-virt" ]]
then
    # make PLATFORM="$architecture_value" DEMO="$demo_value" run -C ../bao-demos/
    make run -C ../bao-demos/ 
fi