#!/bin/bash

if [ ! -d "bao-demos" ]
then
    git clone https://github.com/bao-project/bao-demos.git
fi

# Creating directories for building repos and images
if [ ! -d "build-essentials" ]
then
    mkdir build-essentials
fi

# Creating toolchain directory
if [ ! -d "toolchains" ]
then
    mkdir toolchains
fi

if [ ! -d "images" ]
then
    mkdir images
fi

# Check if Make is installed
if ! dpkg -s make &>/dev/null; then
    echo "It seems that you don't have Make installed on your system. You will need Make to build dependencies."
    echo "Do you want to install Make? [Y/n]"
    read -r confirmation

    # Convert confirmation to lower case
    confirmation=$(echo "$confirmation" | tr '[:upper:]' '[:lower:]')

    # If empty or 'y', install Make
    if [[ -z "$confirmation" ]] || [[ "$confirmation" == "y" ]]; then
        echo "Installing Make..."
        sudo apt install make
    fi
fi




# Installing Qemu if user wants
dpkg -s qemu-system >> /dev/null
if [[ $? == 1 ]]
then
    echo "It seems that you don't have Qemu installed on your system. Qemu is quite useful for debuging before launching on a true target."
    echo "Do you want to install Qemu? [Y/n]"
    read -r confirmation

    # To lower case
    confirmation="$(echo "$confirmation" | tr '[:upper:]' '[:lower:]')"

    # If empty or y
    if [ -z "$confirmation" ] || [[ "$confirmation" == "y" ]]
    then
        echo "Installing Qemu..."
        sudo apt install qemu-system
    fi
fi

# Installing minicom if user wants
dpkg -s minicom >> /dev/null
if [[ $? == 1 ]]
then
    echo "It seems that you don't have minicom installed on your system. Minicom  is useful to create console for devices having no display."
    echo "Do you want to install minicom? [Y/n]"
    read -r confirmation

    # To lower case
    confirmation="$(echo "$confirmation" | tr '[:upper:]' '[:lower:]')"

    # If empty or y
    if [ -z "$confirmation" ] || [[ "$confirmation" == "y" ]]
    then
        echo "Installing minicom..."
        sudo apt install minicom
    fi
fi
