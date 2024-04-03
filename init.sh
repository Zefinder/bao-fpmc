#!/bin/bash

# Getting needed repositories for all installations (basically modified Bao)
if [ ! -d "bao-hypervisor" ]
then
    git clone --recurse-submodules https://github.com/Zefinder/bao-hypervisor
fi 

if [ ! -d "bao-demos" ]
then
    git clone https://github.com/bao-project/bao-demos.git
fi

# Creating directories for building repos and images
if [ ! -d "build-essentials" ]
then
    mkdir build-essentials
fi

if [ ! -d "images" ]
then
    mkdir images
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