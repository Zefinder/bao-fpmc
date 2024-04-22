#!/bin/bash
set -e

# Directories
EXEC_DIRECTORY=$(realpath .)
BAO_DIRECTORY="../bao-hypervisor/"
BAO_CONFIG_DIRECTORY="../config/"
BUILD_ESSENTIALS_DIRECTORY="../build-essentials/"

# Functions
function write_red() {
    printf "\033[0;31m%s\033[0m\n" "${1}"
}

function write_green() {
    printf "\033[0;32m%s\033[0m\n" "${1}"
}

function user_interaction_message {
    printf "\n\n"
    echo "-------------------------------------"
    echo "------ USER INTERACTION NEEDED ------"
    echo "-------------------------------------"
    printf "\n\n"
}

function prepare_sd {
    user_interaction_message
    write_green "Press a key when the SD card is pluged-in"
    read -n 1 -s -r

    # Warn the user
    echo "Note that all partitions must be deleted to install Bao and your OS."
    echo "If you haven't done it, you can still do it."
    write_red "Be sure to save everything that is on the card before continuing..."

    # Ask for mount file
    write_green "What is the SD card path? (e.g. /dev/sda when using an USB adapter (leave empty in that case))"
    write_red "Please, select the right device, if you delete your disk it's not my problem you have been warned"
    read -r device_name

    if [ -z "$device_name" ]
    then
        device_name="/dev/sda"
    fi

    # Ask if user wants to delete all partitions
    echo "To continue, there must be one empty partition (everything formatted)"
    write_green "Do you want to erase all partitions? (no if already done) [y/N]"
    echo "Note that the partition(s) must be mounted"
    read -r confirmation

    # To lower case
    confirmation="$(echo "$confirmation" | tr '[:upper:]' '[:lower:]')"

    # If yes we remove
    if [[ "$confirmation" == "y" ]]
    then
        erase_partitions_sd "$device_name"
    fi

    # Ask for formating
    write_green "Do you want to format? [Y/n]"
    read -r confirmation

    # To lower case
    confirmation="$(echo "$confirmation" | tr '[:upper:]' '[:lower:]')"

    # If empty or yes we format
    if [ -z "$confirmation" ] || [[ "$confirmation" == "y" ]]
    then
        write_green "What is the new partition name? (e.g. /dev/sda1 when using an USB adapter (leave empty in that case))"
        read -r partition_name
        if [ -z "$partition_name" ]
        then
            partition_name="/dev/sda1"
        fi

        # Check if partition mounted
        if df | grep -q "$partition_name"
        then 
            umount "$partition_name"
        fi

        format_sd "$partition_name"
    fi

    # Checkpoint to see if the SD card is remounted
    echo "It can sometimes not automatically mount the SD card, you will probably need to remove and reinsert it..."
    write_green "Press a key when it'll be mounted"
    read -n 1 -s -r

    # Asking for mounting point
    write_green "Enter the mounting point of the SD card (if /media/$USER/boot leave empty)"
    read -r sd_mounting_point

    if [ -z "$sd_mounting_point" ]
    then
        sd_mounting_point="/media/$USER/boot"
    fi
}

function erase_partitions_sd {
    local device_name=${1}

    # Unmount partition
    umount "$device_name"?*

    # Delete partitions
    write_red "Delete all partitions, so do:"
    echo "d to delete (until nothing is left) - w to write and exit"
    sudo fdisk "$device_name"

    echo ""
    write_red "Now we recreate the partitions, press in order:"
    echo "o to create a new DOS partition table"
    echo "n to create a new partition"
    echo "p for new primary partition"
    echo "press return for default partition number"
    echo "16384 for first sector"
    echo "press return for last sector"
    write_red "If it asks for removing signature, type y (for yes)"
    echo "a to make partition bootable"
    echo "t to change partition type"
    echo "c to set partition type to W95 FAT32"
    echo "w to write and exit" 
    sudo fdisk "$device_name"
}

function format_sd {
    local partition=${1}
    sudo mkfs.fat "$partition" -n boot
}

function run_minicom {
    local config_name=${1}
    local selected_main=${2}

    write_green "Do you want to run minicom now? [Y/n]"
    write_red "Be careful, if you type yes the command will be typed now!"

    read -r confirmation

    # To lower case
    confirmation="$(echo "$confirmation" | tr '[:upper:]' '[:lower:]')"

    if [ -z "$confirmation" ] || [[ "$confirmation" == "y" ]]
    then
        make minicom CONFIG="$config_name" SELECTED_MAIN="$selected_main"
    fi
}



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

selected_main=${3}

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
BAO_WRKDIR_PLAT=$BAO_WRKDIR/imgs/$PLATFORM
BAO_WRKDIR_IMGS=$BAO_WRKDIR_PLAT/$config_value
mkdir -p "$BAO_WRKDIR"
mkdir -p "$BAO_WRKDIR_SRC"
mkdir -p "$BAO_WRKDIR_IMGS"

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

# Ready for next step! Platform dependant
UBOOT_DIRECTORY="$BUILD_ESSENTIALS_DIRECTORY/u-boot"
TRUST_DIRECTORY="$BUILD_ESSENTIALS_DIRECTORY/arm-trusted-firmware"
RPI_FIRM_DIRECTORY="$BUILD_ESSENTIALS_DIRECTORY/rpi-firmware"
XILINX_FIRM_DIRECTORY="$BUILD_ESSENTIALS_DIRECTORY/zcu_firmware"

# Qemu aarch64
if [[ "$architecture_value" == "qemu-aarch64-virt" ]]
then
    # Verify if directories exist (or git clone)
    if [[ ! -d "$UBOOT_DIRECTORY" ]]
    then
        # Cloning U-boot
        git clone --depth 1 https://github.com/u-boot/u-boot.git "$UBOOT_DIRECTORY"
    fi 

    if [[ ! -d "$TRUST_DIRECTORY" ]]
    then
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

# Raspberry Pi 4
elif [[ "$architecture_value" == "rpi4" ]]
then
    # Verify if directories exist (or git clone)
    if [[ ! -d "$RPI_FIRM_DIRECTORY" ]]
    then
        # Cloning Raspberry firmware
        git clone --depth 1 https://github.com/raspberrypi/firmware.git "$RPI_FIRM_DIRECTORY"
    fi 

    if [[ ! -d "$UBOOT_DIRECTORY" ]]
    then
        # Cloning U-boot
        git clone --depth 1 https://github.com/u-boot/u-boot.git "$UBOOT_DIRECTORY"
    fi 

    if [[ ! -d "$TRUST_DIRECTORY" ]]
    then
        # Cloning ARM trusted firmware
        git clone --depth 1 https://github.com/bao-project/arm-trusted-firmware.git "$TRUST_DIRECTORY"
    fi

    # Build U-boot
    make rpi_4_defconfig -C "$UBOOT_DIRECTORY"
    make -C "$UBOOT_DIRECTORY"
    # Copy bin!
    cp "$UBOOT_DIRECTORY/u-boot.bin" "$BAO_WRKDIR_PLAT"

    # Build Arm trusted firmware
    make -C "$TRUST_DIRECTORY" PLAT=rpi4
    # Copy bin!
    cp "$TRUST_DIRECTORY/build/rpi4/release/bl31.bin" "$BAO_WRKDIR_PLAT"

    # Checkpoint: Prepare SD card
    prepare_sd

    # Finished preparation, begin copy
    write_red "Starting copy to SD card..."
    # Copy important files
    write_red "Copying rpi boot files..."
    cp -rf "$RPI_FIRM_DIRECTORY/boot/"* "$sd_mounting_point"

    write_red "Copying bl31.bin..."
    cp "$BAO_WRKDIR_PLAT/bl31.bin" "$sd_mounting_point"

    write_red "Copying u-boot.bin..."
    cp "$BAO_WRKDIR_PLAT/u-boot.bin" "$sd_mounting_point"

    write_red "Copying bao.bin..."
    cp "$BAO_WRKDIR_IMGS/bao.bin" "$sd_mounting_point"

    # TODO remove after tests
    write_red "Copying u-boot environment file..."
    cp "$EXEC_DIRECTORY/uboot-env/uboot.env" "$sd_mounting_point"

    write_red "Writing rpi config file..."
    # TODO include rpi config txt?
    # Add config.txt
    { echo "enable_uart=1"; echo "arm_64bit=1"; echo "enable_gic=1"; echo "armstub=bl31.bin"; echo "kernel=u-boot.bin"; } > "$sd_mounting_point/config.txt"
    write_red "Done!"

    # Unmount
    write_red "Unmounting..."
    umount "$sd_mounting_point"

    write_green "The SD card is ready to use!"

    # Run minicom if user wants it
    run_minicom "$config_value" "$selected_main"

# Xilinx ZCU102/4 (TODO Please verify that it works...)
elif [[ "$architecture_value" == "zcu102" || "$architecture_value" == "zcu104" ]]
then
    # Verify if directories exist (or git clone)
    if [[ ! -d "$XILINX_FIRM_DIRECTORY" ]]
    then
        # Cloning Xilinx firmware
        git clone --depth 1 https://github.com/Xilinx/soc-prebuilt-firmware.git "$XILINX_FIRM_DIRECTORY"
    fi

    if [[ ! -d "$UBOOT_DIRECTORY" ]]
    then
        # Cloning U-boot
        git clone --depth 1 https://github.com/u-boot/u-boot.git "$UBOOT_DIRECTORY"
    fi

    # In a subshell go to the Xilinx firmware directory and generate the boot binary file 
    (cd "$XILINX_FIRM_DIRECTORY/$PLATFORM-zynqmp" && bootgen -arch zynqmp -image bootgen.bif -w -o "$BAO_WRKDIR_PLAT/BOOT.BIN")

    # Build U-boot (TODO Ask address, needs to match the config one)
    mkimage -n bao_uboot -A arm64 -O linux -C none -T kernel -a 0x200000 -e 0x200000 -d "$BAO_WRKDIR_IMGS/bao.bin" "$BAO_WRKDIR_IMGS/bao.img"

    # Checkpoint: Prepare SD Card
    prepare_sd

    # Copying files to SD Card
    write_red "Starting copy to SD card..."
    write_red "Copying boot.bin"
    cp "$BAO_WRKDIR_PLAT/BOOT.BIN" "$sd_mounting_point"

    write_red "Copying bao.img"
    cp "$BAO_WRKDIR_IMGS/bao.img" "$sd_mounting_point"

    write_red "Unmounting..."
    umount "$sd_mounting_point"

    # Setup board, the board needs to boot from SD-Card
    write_red "The board must be configured to boot from the SD card"
    echo "To do so, the boot mode SW6 pins [4:1] must be 'off off off on' and the PS_mode[3:0] at 1110"
    write_green "Press a key when you are ready to continue"
    read -n 1 -s -r

    write_green "The SD card is ready to use!"

    # Run minicom if user wants it
    run_minicom "$config_value" "$selected_main"
fi