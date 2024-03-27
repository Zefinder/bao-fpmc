#!/bin/bash

# Getting needed repositories for all installations (basically Bao)
if [ ! -d "bao-hypervisor" ]
then
    git clone https://github.com/bao-project/bao-hypervisor.git
    rm -d bao-hypervisor/ci
    git submodule add -f git@github.com:bao-project/bao-ci.git bao-hypervisor/ci
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

