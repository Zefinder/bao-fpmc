#!/bin/bash

# Directories
EXEC_DIRECTORY=$(realpath .)
BAO_DIRECTORY="../bao-hypervisor/"
BAO_CONFIG_DIRECTORY="../config/"

# Toolchains
TOOLCHAIN_DIRECTORY="${EXEC_DIRECTORY}/../toolchains/"
AARCH64_NONE_TOOLCHAIN="arm-gnu-toolchain-13.2.Rel1-x86_64-aarch64-none-elf/bin/aarch64-none-elf-"
AARCH32_EABI_TOOLCHAIN="arm-gnu-toolchain-13.2.Rel1-x86_64-arm-none-eabi/bin/arm-none-eabi-"
RISCV64_TOOLCHAIN="riscv64-unknown-elf-toolchain-10.2.0-2020.12.8-x86_64-linux-ubuntu14/bin/riscv64-unknown-elf-"

# Supported architectures
ARCHITECTURES=("zcu102" "zcu104" "imx8qm" "tx2" "rpi4" "qemu-aarch64-virt" "fvp-a" "fvp-r" "fvp-a-aarch32" "fvp-r-aarch32" "qemu-riscv64-virt")

# Input arguments and exact regex
architecture_value=${1}
architecture_regex="\<${architecture_value}\>"

# TODO Remove
config_value=${2}
if [ -z "${config_value}" ]
then
    # Baremetal alone is used for testing...
    config_value="baremetal"
fi

# 

# Getting architecture
if [[ ! ${ARCHITECTURES[*]} =~ $architecture_regex ]]
then
    echo "Architecture does not exist"
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

export CROSS_COMPILE=$TOOLCHAIN
export PLATFORM=$architecture_value
export ARCH=$ARCH_SELECTED

# Create directories
export BAO_WRKDIR=$EXEC_DIRECTORY/wrkdir
export BAO_WRKDIR_SRC=$BAO_WRKDIR/srcs
export BAO_WRKDIR_BIN=$BAO_WRKDIR/bin
export BAO_WRKDIR_PLAT=$BAO_WRKDIR/imgs/$PLATFORM
export BAO_WRKDIR_IMGS=$BAO_WRKDIR_PLAT/$config_value
mkdir -p "$BAO_WRKDIR"
mkdir -p "$BAO_WRKDIR_SRC"
mkdir -p "$BAO_WRKDIR_BIN"
mkdir -p "$BAO_WRKDIR_IMGS"

# Copy images
# TODO this need to be a copy from variables...
cp ../images/test/baremetal.bin "$BAO_WRKDIR_IMGS"

# Copy config for Bao build
mkdir -p "$BAO_WRKDIR_IMGS"/config
cp -L "$BAO_CONFIG_DIRECTORY"/"$config_value"/"$PLATFORM".c\
    "$BAO_WRKDIR_IMGS"/config/"$config_value".c

# Build Bao
make -C $BAO_DIRECTORY\
    PLATFORM="$PLATFORM"\
    CONFIG_REPO="$BAO_WRKDIR_IMGS"/config\
    CONFIG="$config_value"\
    CPPFLAGS=-DBAO_DEMOS_WRKDIR_IMGS="$BAO_WRKDIR_IMGS"



# if [[ "$architecture_value" == "qemu-riscv64-virt" ]] || [[ "$architecture_value" == "qemu-aarch64-virt" ]]
# then
#     # make PLATFORM="$architecture_value" DEMO="$demo_value" run -C ../bao-demos/
#     make run -C ../bao-demos/ 
# fi