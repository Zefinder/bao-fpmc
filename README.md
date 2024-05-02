# Fixed Priority Memory Centric scheduling over Bao

## Copyright Notice
- [Bao](https://github.com/bao-project/bao-hypervisor "Bao lightweight static partitioning hypervisor on GitHub"): All files inside folders `bao-hypervisor`, `bao-demos` and `images/test` are licensed according to the specified license (See `README.md` and `LICENCE` for more information). Credits for the Fixed Priority Memory Centric scheduler implementation go to [Gero Schwäricke](https://github.com/gschwaer)
- [FreeRTOS](https://github.com/FreeRTOS/FreeRTOS-Kernel "'Classic' FreeRTOS distribution (but here only Kernel)"): All files inside the folder `freertos-bao-fpmc/freertos` are licensed according to the specified license (See `LICENSE.md` for more information)

## Prerequisites

We assume that the host is on a Linux distribution with sudo access. If you are not, please do or install manually everything that needs to be installed (See Appendix at the end (TODO)).

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

## How do I use the FreeRTOS (and baremetal) included in this repository
If you forgot to use the `--recurse-submodules` when cloning the repository, you will have some problems when building the FreeRTOS image, as it is using the Bao's baremetal guest and the FreeRTOS repository as submodules. You can simply do
```
git submodule update --init --recursive
```

To build the image, just use the `build-image` rule of the makefile in the `launch` folder. There are three mandatory arguments:
- PLATFORM, the target platform to compile for
- SELECTED_MAIN, the main application you want to use
- BUILD, which os to build (take the values baremetal, freertos or both)

It sounded like a good idea to not have one big `main.c` with `#ifndef` and `#if` preprocessor instructions to compile or not some parts of the main function, some tasks, etc... making the file and the project unreadable. The `freertos-bao-fpmc` repository is now divided in 4 parts: **architecture specific**, **baremetal**, **FreeRTOS kernel** and **main applications**. Each main application has a folder with **at least** one `source.mk` and a `.c` file with a `main_app()` function defined. The `source.mk` file must define `spec_c_srs` (and `spec_s_srcs` if any) with all the `.c` (respectively `.S`) files to compile **and must contain the file where the main_app() function is**!

If you want to build for qemu aarch64 with the main application `execution-fpsched` for FreeRTOS, you will type:
```
make build-image PLATFORM=qemu-aarch64-virt SELECTED_MAIN=execution-fpsched BUILD=freertos
```

To clean the images, use:
```
make clean-image
```

Of course, you can build the image and run the launcher in the same command. Using the latter example with configuration `bench_solo_legacy`, you would type:
```
make clean-image build-image all PLATFORM=qemu-aarch64-virt SELECTED_MAIN=execution-fpsched CONFIG=bench_solo_legacy BUILD=freertos
```

For baremetal, it is basically the same thing but the function is called `task()`, the makefile variable are `task_c_srcs` and `task_s_srcs`. Note that SELECTED_MAIN is also the selector for the baremetal task function.

## How do I create a configuration file
If you've seen the configuration files that are in the `config` folder, you are probably wondering where to start and what to modify (and this is a legitimate question). First of all, I recommend you to go watch Bao's demonstration on youtube (link in [Bao](https://github.com/bao-project/bao-hypervisor)'s repository) to understand what is what and why are they useful to Bao.

If you want to **manually create** your configuration file, you can use configurations that alredy exist in the repository and configurations that are in `demos/[configuration]/configs` of Bao's demo repository and them modify them. You can also use the Appendices that are at the end of this README to know what is the entry point and what are the GIC registers' addresses. These values can be changed depending on the OS and depending on the OS configuration (for example, a baremetal target can begin at `0x300000` because you've modified the linker file to start there). The values I used are the one for Bao's guests from Bao's demo repository, that means that if you fork their guest OS without changing the starting point, you will have no problems (I hope...). 

If you **don't want** to do that, this is understandable, this is why there is a file in the `launch` folder that allows configuration generation: `generate_config.py`. Just launch it and you will be asked for a few things: 
- Targetted platform (for now only qemu-aarch64-virt, rpi4, zcu102 and zcu104)
- Configuration name
- Total CPU number of the platform (by default 4 but we never know)
- The number of shared memory you want and their size
- The OS you want to put
  - For that OS how many cores
  - The image path
  - The number of regions, location in virtual memory and size
  - The number of IPC and which shared memory to use
  - The number of devices, their addresses (physical and virtual), size and interruptions

The generation is done for the guests OSes in Bao's demo repository. There is no GUI, it's ugly but it does the job. You can change the structure file at any time, feel free to add things that you need (like place_phys for some OSes)

To launch it, go in the `launch` folder and type 
```
python3 generate_config.py
```

## Running benchmarks on FreeRTOS 
There is a benchmark unit for FreeRTOS `benchmark.h` that you can use to measure the time of some function. The results given by this benchmark unit is in python format and throughout the tests, the unit will print things. If you want to use the data with python, I highly recommend you to use either not printing or printing as a comment for example `# wow!`. The min and max are also shown as well as the integer average. As no floating points can be used, you will have to compute the average by yourself, but using python is not a problem: 
```py
average = sum(elapsed_time_array) / len(elapsed_time_array)
```

## How do I generate log files ?
Log files are generated for true targets only (you can easily log to a file using QEMU if you really want to not run it on a true target). When you run the make `all` rule of the `launch` folder on a true target (for example rpi4), at the end of the formatting, you will be asked if you want to run the minicom command. If you say yes, it will try to open minicom with the following versioning file format `[config name]-[selected main]-[date]-[test number].log`. The script will assume that the target is located in /dev/ttyUSB0. The SELECTED_MAIN is not mandatory but allows more details in the log's name

**REMARK**: if you say yes, it will **directly** try to open minicom! Also to exit minicom, press Ctrl+A-x

You can also use the `minicom` rule of the makefile of the `launch` folder, you will only need to enter the configuration name and optionally the selected main. For example:
```
make minicom CONFIG=bench-solo-legacy SELECTED_MAIN=execution-fpsched
```

If you want to extract the python code from the log file, you can use the python script in `test-logs`, it will create a new folder if it doesn't exist and extract the code from all log files. If the python file already exists, it won't be replaced. Note that this folder with all the python files is in the `.gitignore`.

## Side notes for running on true targets
If you want to use a true target and not QEMU, you will probably have a SD card to boot. This SD card must be cleared, all partitions removed and formatted. If you use the `make` command, you will be asked if you want to do it before putting Bao on it (it's so kind!). However, Ubuntu will not automatically mount the newly created partitions, to manually mount it, here is the command `sudo mkdosfs -F32 [DEVICE_NAME]`. This can be used to erase all partitions again and restart from the very beginning. 

## There is a Linux configuration but not linux binary
If you want to use the Linux image, please compile it yourself using the guide on [Bao demo](https://github.com/bao-project/bao-demos)'s repository. The image is not long to build with 24 CPUs

# Appendices 

## Appendix I - Entry points
Entry points are not the same for all platforms and for all OSes. For a manual configuration, it is always good to know them to boot. Note that if you have multiple times the same OS, the entry point will be the same! The given `.entry` and `.base_addr` are VM addresses and not physical addresses. Also, for all platforms **EXCEPT** zcu's, the entry point is also the base memory address. For Linux on a zcu (102 or 104), the entry point address is `0x200000` for some reason... 

The following figure compiles the different entry points in [Bao demo](https://github.com/bao-project/bao-demos)'s repository.


|                   | baremetal  | freertos   | linux      | zephyr       |
| ----------------- | ---------- | ---------- | ---------- | ------------ |
| zcu102 and zcu104 | 0x20000000 | 0x0        | 0x00200000 |              |
| imx8qm            | 0x80200000 | 0x0        | 0x80200000 |              |
| tx2               | 0xa0000000 | 0x0        | 0x90000000 |              |
| rpi4              | 0x200000   | 0x0        | 0x20000000 | 0x80000000   |
| qemu-aarch64-virt | 0x50000000 | 0x0        | 0x60000000 | 0x80000000   |
| fvp-a-aarch64     | 0x90000000 | 0x0        | 0xa0000000 | 0x90000000   |
| fvp-a-aarch32     | 0x90000000 | 0x0        | 0xa0000000 | 0x20000000   |
| fvp-r-aarch64     | 0x10000000 | 0x10000000 | 0x20000000 | 0x24000000\* |
| fvp-r-aarch32     | 0x10000000 | 0x10000000 | 0x20000000 | 0x24000000   |
| qemu-riscv64-virt | 0x80200000 | 0x0        | 0x90200000 |              |

\* For this configuration, the region base address will be `0x20000000`.

## Appendix II - GIC register addresses
It is mandatory to enter the GIC register addresses for all aarch platforms. These values for baremetal are given in [Bao demo](https://github.com/bao-project/bao-demos)'s repository and the following figure compiles them. If a register address is not mandatory, there will be a blank space. For every other target OS, the address will probably be in a config file.


| baremetal target  |    GICD    |    GICR    |    GICC    |
| :---------------- | :--------: | :--------: | :--------: |
| zcu102 and zcu104 | 0xF9010000 |            | 0xF9020000 |
| imx8qm            | 0xF9010000 | 0xF9020000 |            |
| tx2               | 0x03881000 |            | 0x03882000 |
| rpi4              | 0xff841000 |            | 0xff842000 |
| qemu-aarch64-virt | 0x08000000 | 0x080A0000 |            |
| fvp-a-aarch64     | 0x2F000000 | 0x2F100000 |            |
| fvp-a-aarch32     | 0x2F000000 | 0x2F100000 |            |
| fvp-r-aarch64     | 0xAF000000 | 0xAF100000 |            |
| fvp-r-aarch32     | 0xAF000000 | 0xAF100000 |            |

Note that these addresses may or may not differ for another OS, but you really need to look at the config file!
