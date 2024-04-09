PLATFORM=
CONFIG=
DEMO_PLATFORM ?= "qemu-aarch64-virt"
DEMO_CONFIG ?= "baremetal"

all:
	./launch-bao.sh $(PLATFORM) $(CONFIG)

build-image:
	./build-freertos.sh $(PLATFORM)

demo:
	./bao-demo.sh $(DEMO_PLATFORM) $(DEMO_CONFIG)

clean:
	make clean -C ../bao-hypervisor
	rm -rf ../build-essentials/$(PLATFORM)
	rm -rf ./wrkdir

clean-demo:
	make clean -C ../bao-demos PLATFORM=$(DEMO_PLATFORM) DEMO=$(DEMO_CONFIG)
	make distclean -C ../bao-demos PLATFORM=$(DEMO_PLATFORM) DEMO=$(DEMO_CONFIG)

clean-image:
	rm -rf ../freertos-bao-fpmc/build