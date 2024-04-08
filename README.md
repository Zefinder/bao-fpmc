# Fixed Priority Memory Centric scheduling over Bao

## Copyright Notice
- [Bao](https://github.com/bao-project/bao-hypervisor "Bao lightweight static partitioning hypervisor on GitHub"): All files inside folders `bao-hypervisor`, `bao-demos` and `images/test` are licensed according to the specified license (See `README.md` and `LICENCE` for more information). Credit for the Fixed Priority Memory Centric scheduler implementation go to [Gero Schwäricke](https://github.com/gschwaer)
- [FreeRTOS](https://github.com/FreeRTOS/FreeRTOS-Kernel "'Classic' FreeRTOS distribution (but here only Kernel)"): All files inside the folder `freertos-bao-fpmc/freertos` are licensed according to the specified license (See `LICENSE.md` for more information)

## How to setup
It is recommended to clone this repository with all its submodules, using:
```
git clone --recurse-submodules https://github.com/Zefinder/bao-fpmc.git
```

The script `init.sh` will clone Bao repositories (the hypervisor and the demo) and create the directories used by the scripts in the `launch` folder. However, note that the `toolchains` folder is created but is empty. This is because you need to download it (or them) manually... Just untar the toolchain in the `toolchains` folder and everything should work. According to Bao's documentation, the needed toolchains are:
- For Armv8 (Aarch64) targets, use the **aarch64-none-elf-** toolchain ([Arm Developper](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads))
- For Armv7 and Armv8 (Aarch32) targets, use the **arm-none-eabi-** toolchain ([Arm Developper](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads))
- For RISC-V targets, use the **riscv64-unknown-elf-** toolchain ([SiFive's Freedom Tools](https://github.com/sifive/freedom-tools/releases))

Installing the three of them takes around 3.5 GB.

---

You will then need to install images by yourself in the `images` directory. Images use the `.bin` format, not `.elf`! You can probably generate the a binary file from the elf executable with
```
objcopy -O binary my_image.bin my_image.elf
```

or adding a rule in your makefile, for example:
```makefile
hey.bin: hey.elf
  $(objcopy) -O binary $@ $<
```

## How to test if the Bao demo repo works
Nothing more simple, just use `make demo` in the `launch` folder. By default, the target platform is Qemu for `aarch64` and the chosen demo is `baremetal`. You can change the platform with the PLATFORM option, and the demo with the DEMO option. Using `qemu-aarch64-virt` or `qemu-riscv64-virt` will use qemu and will not require any target device. Note that the demo uses the toolchains, so it is a great way to see if the toolchain is correctly setup.

Besides using it as a toolchain check, you can also inspire you from their config files (`bao-demos/demos/[interesting config]/configs`). All possible configs are there, you don't need to install anything after running the `init.sh` script.

You can clean all demo files using `make clean-demo`.

## How do I use Bao 
First of all, you need to have one or more images in the `images` folder. As said earlier, they need to be in **binary format** (`.bin`)! Be sure to have them in that format and in the correct folder. 

You then need to write a Bao config file in the `config` folder. This config file must be named after the **platform name** and put inside another folder with the **configuration name**.

Here is an example of what you can get before launching Bao:
```
.
├── config
│   ├── baremetal
│   │   └── fvp-a.c
│   │   └── zuc104.c
│   ├── dual_freertos_baremetal
│   │   └── rpi4.c
│   └── dual_freertos_linux
│       └── qemu-aarch64-virt.c
└── images
    └── test
        ├── baremetal.bin
        ├── freertos.bin
        └── linux.bin
```

To write the config file, you can refer to the ones in the `bao-demos/demos` folder or by watching [this presentation](https://www.youtube.com/watch?v=6c8_MG-OHYo) from 24:00 to understand what are each components used for. They will probably also release some documentation so make sure to check that out. The path to the `images` folder from the config file is `../images` and will retrieve the images automatically there. There is no need to copy them in another folder! Bao's compilation will include them automatically from the configuration file. 

Now you are ready to launch the script using the makefile! There are 2 required arguments: 
- PLATFORM: the execution platform
- CONFIG: the configuration name

There are two configurations and two images for testing. The images are taken from the [Bao demo repository](https://github.com/bao-project/bao-demos). To launch the first configuration (`baremetal`), type
```
make PLATFORM=qemu-aarch64-virt CONFIG=baremetal
```

To launch the second configuration, type
```
make PLATFORM=qemu-aarch64-virt CONFIG=test_dual
```

No further user installation is needed, the script automatically clones the required repositories for the targetted platform. To clean everything, use `make clean`

## How do I use the FreeRTOS included in this repository
If you forgot to use the `--recurse-submodules` when cloning the repository, you will have some problems when building the FreeRTOS image, as it is using the Bao's baremetal guest and the FreeRTOS repository as submodules. You can simply do
```
git submodule update --init --recursive
```

To build the image, just use the `build-image` rule of the makefile in the `launch` folder. It requires the targetted platform to work, the image will be copied in `images/build`. You can use both `build-image` and `all` to build and launch bao's compilation: 
```
make build-image all PLATFORM=qemu-aarch64-virt CONFIG=test_freertos IMAGES="build/freertos_hyp.bin"
```

## Side notes for running on true targets
If you want to use a true target and not QEMU, you will probably have a SD card to boot. This SD card must be cleared, all partitions removed and formatted. If you use the `make` command, you will be asked if you want to do it before putting Bao on it (it's so kind!). However, Ubuntu will not automatically mount the newly created partitions, to manually mount it, here is the command `sudo mkdosfs -F32 [DEVICE_NAME]`. This can be used to erase all partitions again and restart from the very beginning. 

## There is a Linux configuration but not linux binary
If you want to use the Linux image, please compile it yourself using the guide on [Bao demo](https://github.com/bao-project/bao-demos)'s repository. The image is not long to build with 24 CPUs