PLATFORM=
CONFIG=
SELECTED_MAIN=
BUILD ?= "both"
DEMO_PLATFORM ?= "qemu-aarch64-virt"
DEMO_CONFIG ?= "baremetal"

all:
	./launch-bao.sh $(PLATFORM) $(CONFIG) $(SELECTED_MAIN)

build-image:
	./build-images.sh $(PLATFORM) $(BUILD)

demo:
	./bao-demo.sh $(DEMO_PLATFORM) $(DEMO_CONFIG)

minicom:
	./launch-minicom.sh $(CONFIG) $(SELECTED_MAIN)

clean: clean-image
	rm -rf ../build-essentials/$(PLATFORM)
	rm -rf ./wrkdir

clean-demo:
	make clean -C ../bao-demos PLATFORM=$(DEMO_PLATFORM) DEMO=$(DEMO_CONFIG)
	make distclean -C ../bao-demos PLATFORM=$(DEMO_PLATFORM) DEMO=$(DEMO_CONFIG)

clean-image:
	rm -rf ../freertos-bao-fpmc/build
	rm -rf ../baremetal-bao-fpmc/build
	rm -rf ../images/build/*
	make clean -C ../bao-hypervisor