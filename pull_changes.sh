#!/bin/bash
set -e 

# Basic git pull
git pull

# Go to each submodule and pull
(cd bao-hypervisor && git switch main && git pull)
(cd freertos-bao-fpmc && git switch master && git pull)
(cd baremetal-bao-fpmc && git switch master && git pull)
