# Fixed Priority Memory Centric scheduling over Bao

## Copyright Notice
- [Bao](https://github.com/bao-project/bao-hypervisor "Bao lightweight static partitioning hypervisor on GitHub"): The folders `bao-hypervisor` and `bao-demos` are licenced according to the specified license (See `README.md` and `LICENCE` for more information)

## How to setup
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
truc.bin: truc.elf
  $(objcopy) -O binary $@ $<
```

## How to test if the Bao demo works
Nothing more simple, just use `make demo` in the `launch` folder. By default, the target platform is Qemu for `aarch64` and the chosen demo is `baremetal`. You can change the platform with the PLATFORM option, and the demo with the DEMO option. Using `qemu-aarch64-virt` or `qemu-riscv64-virt` will use qemu and will not require any target device. Note that the demo uses the toolchains, so it is a great way to see if the toolchain is correctly setup.

You can clean all demo files using `make clean-demo`.

## 