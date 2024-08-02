#!/bin/bash
set -e 

# Basic git pull
git pull origin tests

# Go to each submodule and pull
(cd bao-hypervisor && git switch tests && git pull origin tests)
(cd freertos-bao-fpmc && git switch tests && git pull origin tests)
(cd baremetal-bao-fpmc && git switch tests && git pull origin tests)
