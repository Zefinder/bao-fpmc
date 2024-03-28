#!/bin/bash

# Directories
EXEC_DIRECTORY=$(realpath .)
BAO_DIRECTORY="../bao-hypervisor/"
BAO_CONFIG_DIRECTORY="../config/"
BUILD_ESSENTIALS_DIRECTORY="../build-essentials/"
IMAGES_DIRECTORY="../images"

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

# Getting architecture
if [[ ! ${ARCHITECTURES[*]} =~ $architecture_regex ]]
then
    echo "Architecture not set or does not exist"
    echo "List of supported architectures:"
    (IFS="|$IFS"; printf '%s\n' "${ARCHITECTURES[*]}")
    echo "Try \"./modified-bao-demo.sh qemu-aarch64-virt\" for example..."
    exit 1
fi

# Verifying config
config_value=${2}
if [ -z "${config_value}" ]
then
    echo "Configuration was not set..."
    exit 1
fi

if [ ! -d "$BAO_CONFIG_DIRECTORY/$config_value" ]
then 
    echo "Configuration does not exist... (Or you forgot to put it in the 'configs' folder)"
    exit 2
fi

# Verifying images
if [ -z "${3}" ]
then
    echo "No image set..."
    exit 1
fi

IFS=', ' read -r -a system_images <<< "${3}"
for image in "${system_images[@]}"
do
    if [ ! -f "$IMAGES_DIRECTORY/$image" ]
    then
        echo "Image $image does not exist"
        exit 2
    fi
done

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

# Create useful Bao directories
BAO_WRKDIR=$EXEC_DIRECTORY/wrkdir
BAO_WRKDIR_SRC=$BAO_WRKDIR/srcs
BAO_WRKDIR_BIN=$BAO_WRKDIR/bin
BAO_WRKDIR_PLAT=$BAO_WRKDIR/imgs/$PLATFORM
BAO_WRKDIR_IMGS=$BAO_WRKDIR_PLAT/$config_value
mkdir -p "$BAO_WRKDIR"
mkdir -p "$BAO_WRKDIR_SRC"
mkdir -p "$BAO_WRKDIR_BIN"
mkdir -p "$BAO_WRKDIR_IMGS"

# Copy images
for image in "${system_images[@]}"
do
    cp "$IMAGES_DIRECTORY/$image" "$BAO_WRKDIR_IMGS"
done


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

# Copy Bao image to working directory
cp "$BAO_DIRECTORY/bin/$architecture_value/$config_value/bao.bin" "$BAO_WRKDIR_IMGS/bao.bin"

# Qemu aarch64
if [[ "$architecture_value" == "qemu-aarch64-virt" ]]
then
    # Verify if directory exist (or create and git clone)
    QEMU_ESSENTIALS="$BUILD_ESSENTIALS_DIRECTORY/$architecture_value"
    UBOOT_DIRECTORY="$QEMU_ESSENTIALS/u-boot"
    TRUST_DIRECTORY="$QEMU_ESSENTIALS/arm-trusted-firmware"
    if [[ ! -d "$QEMU_ESSENTIALS" ]]
    then
        # Cloning U-boot
        git clone --depth 1 https://github.com/u-boot/u-boot.git "$UBOOT_DIRECTORY"

        # Cloning ARM trusted firmware
        git clone --depth 1 https://github.com/bao-project/arm-trusted-firmware.git "$TRUST_DIRECTORY"
    fi

    # Build U-boot
    make qemu_arm64_defconfig -C "$UBOOT_DIRECTORY"
    # Some configs
    echo "CONFIG_SYS_TEXT_BASE=0x60000000" >> "$UBOOT_DIRECTORY/.config"
    echo "CONFIG_TFABOOT=y" >> "$UBOOT_DIRECTORY/.config"
    # Make
    make -C "$UBOOT_DIRECTORY"
    # Copy bin!
    cp "$UBOOT_DIRECTORY/u-boot.bin" "$BAO_WRKDIR_PLAT"

    # Build Arm trusted firmware
    make -C "$TRUST_DIRECTORY" PLAT=qemu bl1 fip BL33="$BAO_WRKDIR_PLAT/u-boot.bin" QEMU_USE_GIC_DRIVER=QEMU_GICV3
    # Copying, formatting 
    dd if="$TRUST_DIRECTORY/build/qemu/release/bl1.bin" of="$BAO_WRKDIR_PLAT/flash.bin"
    dd if="$TRUST_DIRECTORY/build/qemu/release/fip.bin" of="$BAO_WRKDIR_PLAT/flash.bin" seek=64 bs=4096 conv=notrunc

    # Running QEMU
    qemu-system-aarch64 -nographic\
    -M virt,secure=on,virtualization=on,gic-version=3 \
    -cpu cortex-a53 -smp 4 -m 4G\
    -bios "$BAO_WRKDIR_PLAT/flash.bin" \
    -device loader,file="$BAO_WRKDIR_IMGS/bao.bin",addr=0x50000000,force-raw=on\
    -device virtio-net-device,netdev=net0\
    -netdev user,id=net0,net=192.168.42.0/24,hostfwd=tcp:127.0.0.1:5555-:22\
    -device virtio-serial-device -chardev pty,id=serial3 -device virtconsole,chardev=serial3
fi

# if [[ "$architecture_value" == "qemu-riscv64-virt" ]] || [[ "$architecture_value" == "qemu-aarch64-virt" ]]
# then
#     # make PLATFORM="$architecture_value" DEMO="$demo_value" run -C ../bao-demos/
#     make run -C ../bao-demos/ 
# fi