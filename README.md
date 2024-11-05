# Fixed Priority Memory Centric scheduling over Bao

## Copyright Notice
- [Bao](https://github.com/bao-project/bao-hypervisor "Bao lightweight static partitioning hypervisor on GitHub"): All files inside directorys `bao-hypervisor`, `bao-demos` and `images/test` are licensed according to the specified license (See `README.md` and `LICENCE` for more information). Credits for the Fixed Priority Memory Centric scheduler implementation go to [Gero Schwäricke](https://github.com/gschwaer)
- [FreeRTOS](https://github.com/FreeRTOS/FreeRTOS-Kernel "'Classic' FreeRTOS distribution (but here only Kernel)"): All files inside the directory `freertos-bao-fpmc/freertos` are licensed according to the specified license (See `LICENSE.md` for more information)

## Prerequisites

We assume that the host is on a Linux distribution with sudo access. If you are not, please do or install manually everything that needs to be installed (See Appendix III).

## How to setup
It is recommended to clone this repository with all its submodules, using:
```
git clone --recurse-submodules https://github.com/Zefinder/bao-fpmc.git
```

The script `init.sh` will clone the [Bao demo](https://github.com/bao-project/bao-demos)'s repository, create all mandatory directories used by the scripts in the `launch` directory, install all mandatory packages to compile everything manually and ask you if you want to install some packets to used in `launch` (`make`, `qemu` and `minicom`). Note that the `toolchains` directory is created but is empty. This is because you need to download it (or them) manually... Just untar the toolchain in the `toolchains` directory and everything should work. According to Bao's documentation, the needed toolchains are:
- For Armv8 (Aarch64) targets, use the **aarch64-none-elf-** toolchain ([Arm Developper](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads))
- For Armv7 and Armv8 (Aarch32) targets, use the **arm-none-eabi-** toolchain ([Arm Developper](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads))
- For RISC-V targets, use the **riscv64-unknown-elf-** toolchain ([SiFive's Freedom Tools](https://github.com/sifive/freedom-tools/releases))

Installing the three of them takes around 3.5 GB.

If you want to pull all changes, there is a `pull_changes.sh` that will pull all changes made to the submodules.

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
Nothing more simple, just use `make demo` in the `launch` directory. By default, the target platform is Qemu for `aarch64` and the chosen demo is `baremetal`. You can change the platform with the PLATFORM option, and the demo with the DEMO option. Using `qemu-aarch64-virt` or `qemu-riscv64-virt` will use qemu and will not require any target device. Note that the demo uses the toolchains, so it is a great way to see if the toolchain is correctly setup.

Besides using it as a toolchain check, you can also inspire you from their config files (`bao-demos/demos/[interesting config]/configs`). All possible configs are there, you don't need to install anything after running the `init.sh` script.

You can clean all demo files using `make clean-demo`.

## How do I use Bao 
First of all, you need to have one or more images in the `images` directory. As said earlier, they need to be in **binary format** (`.bin`)! Be sure to have them in that format and in the correct directory. 

You then need to write a Bao config file in the `config` directory. This config file must be named after the **platform name** and put inside another directory with the **configuration name**.

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

To write the config file, you can refer to the ones in the `bao-demos/demos` directory or by watching [this presentation](https://www.youtube.com/watch?v=6c8_MG-OHYo) from 24:00 to understand what are each components used for. They will probably also release some documentation so make sure to check that out. The path to the `images` directory from the config file is `../images` and will retrieve the images automatically there. There is no need to copy them in another directory! Bao's compilation will include them automatically from the configuration file. 

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

To build the image, just use the `build-image` rule of the makefile in the `launch` directory. There are three mandatory arguments:
- PLATFORM, the target platform to compile for
- SELECTED_MAIN, the main application you want to use
- BUILD, which os to build (take the values baremetal, freertos or both)

It sounded like a good idea to not have one big `main.c` with `#ifndef` and `#if` preprocessor instructions to compile or not some parts of the main function, some tasks, etc... making the file and the project unreadable. The `freertos-bao-fpmc` repository is now divided in 4 parts: **architecture specific**, **baremetal**, **FreeRTOS kernel** and **main applications**. Each main application has a directory with **at least** one `source.mk` and a `.c` file with a `main_app()` function defined. The `source.mk` file must define `spec_c_srs` (and `spec_s_srcs` if any) with all the `.c` (respectively `.S`) files to compile **and must contain the file where the main_app() function is**!

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

### PREM tasks and IPI in FreeRTOS
You might want to use PREM tasks to either test them or to implement some real time tasks. This implementation of PREM (using Bao) use hypercalls and IPI to know when to start and when to stop. It means that IPI handlers are implemented inside PREM. Enabling IPI handlers is disabled by default since you can't use them for anything else. If you want to use PREM you have 2 choices: 
- Reimplement IPI to make PREM work (good luck I guess)
- Use the default handlers, compiling with `DEFAULT_IPI=y` (any other value provoke an error)

Hence if you want to compile `test-fpsched` on Raspberry4, you will type 
```
make build-image PLATFORM=rpi4 CONFIG=test_prem SELECTED_MAIN=test-fpsched BUILD=freertos DEFAULT_IPI=y
```

There is also the memory offset after prefetch option that you can specify during build. This one will require `MEMORY_REQUEST_WAIT`. The best example is to compile `test-prem`:
```
make build-image PLATFORM=rpi4 CONFIG=test_prem SELECTED_MAIN=execution-solo BUILD=freertos DEFAULT_IPI=y MEMORY_REQUEST_WAIT=y
```

## How do I create a configuration file
If you've seen the configuration files that are in the `config` directory, you are probably wondering where to start and what to modify (and this is a legitimate question). First of all, I recommend you to go watch Bao's demonstration on youtube (link in [Bao](https://github.com/bao-project/bao-hypervisor)'s repository) to understand what is what and why are they useful to Bao.

If you want to **manually create** your configuration file, you can use configurations that alredy exist in the repository and configurations that are in `demos/[configuration]/configs` of Bao's demo repository and them modify them. You can also use the Appendices that are at the end of this README to know what is the entry point and what are the GIC registers' addresses. These values can be changed depending on the OS and depending on the OS configuration (for example, a baremetal target can begin at `0x300000` because you've modified the linker file to start there). The values I used are the one for Bao's guests from Bao's demo repository, that means that if you fork their guest OS without changing the starting point, you will have no problems (I hope...). 

If you **don't want** to do that, this is understandable, this is why there is a file in the `launch` directory that allows configuration generation: `generate_config.py`. Just launch it and you will be asked for a few things: 
- Targetted platform (for now only qemu-aarch64-virt, rpi4, zcu102 and zcu104)
- Configuration name
- Total CPU number of the platform (by default 4 but we never know)
- The number of shared memory you want and their size
- If you want to use colors
- The OS you want to put
  - For that OS how many cores
  - The image path
  - The number of colors you want
  - The preferred core to execute on
  - The number of regions, location in virtual memory and size
  - The number of IPC and which shared memory to use
  - The number of devices, their addresses (physical and virtual), size and interruptions

The generation is done for the guests OSes in Bao's demo repository. There is no GUI, it's ugly but it does the job. You can change the structure file at any time, feel free to add things that you need (like place_phys for some OSes)

To launch it, go in the `launch` directory and type 
```
python3 generate_config.py
```

## Running benchmarks on FreeRTOS 
There is a benchmark unit for FreeRTOS `benchmark.h` that you can use to measure the time of some function. The results given by this benchmark unit is in Python format and throughout the tests, the unit will print things. If you want to use the data with Python, I highly recommend you to use either not printing or printing as a comment for example `# wow!`. The min and max are also shown as well as the integer average. As no floating points can be used, you will have to compute the average by yourself, but using Python is not a problem: 
```py
average = sum(elapsed_time_array) / len(elapsed_time_array)
```

## How do I generate log files ?
Log files are generated for true targets only (you can easily log to a file using QEMU if you really want to not run it on a true target). When you run the make `all` rule of the `launch` directory on a true target (for example rpi4), at the end of the formatting, you will be asked if you want to run the minicom command. If you say yes, it will try to open minicom with the following versioning file format `[config name]-[selected main]-[date]-[test number].log`. The script will assume that the target is located in /dev/ttyUSB0. The SELECTED_MAIN is not mandatory but allows more details in the log's name

**REMARK**: if you say yes, it will **directly** try to open minicom! Also to exit minicom, press Ctrl+A-x

You can also use the `minicom` rule of the makefile of the `launch` directory, you will only need to enter the configuration name and optionally the selected main. For example:
```
make minicom CONFIG=bench-solo-legacy SELECTED_MAIN=execution-fpsched
```

If you want to extract the Python code from the log file, you can use the Python script in `test-logs`, it will create a new directory if it doesn't exist and extract the code from all log files. If the Python file already exists, it won't be replaced. Note that this directory with all the Python files is in the `.gitignore`.

You can also use these logs (to make graphs for instance) in the `analysis` directory. The file `analysis_utils.py` contains a function to exctract all variables from a file and returns them in a `dict`. **Note** that if you use already present analysis files, the log files they use can be compressed in a `.tar.gz` file (e.g. `bench_2tasks_legacy-execution-2tasks-24-04-24-1.tar.gz`). You will have to uncompress them to analyse them and generate the grapĥs

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

## Appendix III - Manually install image build dependencies
In order to generate an image that can run on true platforms, you will need to install a few things that depend on the running platform. If you are here, it means that you don't have sudo rights or that you are one of these purists that **must** install things manually (computers might be dangerous). 

The first step is to create a directory called `build-essentials` in this root directory (`bao-fpmc`). It's at this place that you will need to install the few firmwares you will need. The following figure will show what firmware are mandatory for which platform (checkbox checked = needed, empty = useless).

| baremetal target  | ARM trusted firmware\* |      U-boot\*      | Xilinx firmware\*  |        SCFW        |        SECO        |  NXP's mkimage\*   |        L4T         |        FVP         |     OpenSBI\*      |
| :---------------- | :--------------------: | :----------------: | :----------------: | :----------------: | :----------------: | :----------------: | :----------------: | :----------------: | :----------------: |
| zcu102 and zcu104 |                        | :white_check_mark: | :white_check_mark: |                    |                    |                    |                    |                    |                    |
| imx8qm            |   :white_check_mark:   | :white_check_mark: |                    | :white_check_mark: | :white_check_mark: | :white_check_mark: |                    |                    |                    |
| tx2               |   :white_check_mark:   |                    |                    |                    |                    |                    | :white_check_mark: |                    |                    |
| rpi4              |   :white_check_mark:   | :white_check_mark: |                    |                    |                    |                    |                    |                    |                    |
| qemu-aarch64-virt |   :white_check_mark:   | :white_check_mark: |                    |                    |                    |                    |                    |                    |                    |
| fvp-a-aarch64     |   :white_check_mark:   | :white_check_mark: |                    |                    |                    |                    |                    | :white_check_mark: |                    |
| fvp-a-aarch32     |   :white_check_mark:   | :white_check_mark: |                    |                    |                    |                    |                    | :white_check_mark: |                    |
| fvp-r-aarch64     |                        |                    |                    |                    |                    |                    |                    | :white_check_mark: |                    |
| fvp-r-aarch32     |                        |                    |                    |                    |                    |                    |                    | :white_check_mark: |                    |
| qemu-riscv64-virt |                        |                    |                    |                    |                    |                    |                    |                    | :white_check_mark: |

The firmware marked with \* are a git repository to clone (you can use the `--depth 1` to only clone the commit you need and not the whole history). 

For `NXP i.MX8QM` (`imx8qm`), you will need SCFW from `https://www.nxp.com/lgfiles/NMG/MAD/YOCTO/imx-sc-firmware-[version].bin` and SECO from `https://www.nxp.com/lgfiles/NMG/MAD/YOCTO/imx-seco-[version].bin`. You will also need to install them (`chmod +x [file] ; ./[file]`). Also clone the NXP's mkimage from the **imx branch**!

For `Nvidia TX2`, you will need L4T 5.1 (or later) from ` https://developer.nvidia.com/embedded/l4t/r32_release_v5.1/r32_release_v5.1/t186/tegra186_linux_r32.5.1_aarch64.tbz2`

For `FVP-A` and `FVP-R`, you will need to download the binary you need and untar it (from `https://developer.arm.com/-/media/Files/downloads/ecosystem-models/FVP_Base_RevC-2xAEMvA_[version]_Linux64.tgz` for `FVP-A` and from `https://developer.arm.com/-/media/Files/downloads/ecosystem-models/FVP_Base_AEMv8R_[version]_Linux64.tgz` for `FVP-R`). 

If you are unsure of something, you can always go to [Bao demo](https://github.com/bao-project/bao-demos)'s repository and check firmware versions. Exports and make are handled by the launch script