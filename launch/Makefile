PLATFORM ?= "qemu-aarch64-virt"
CONFIG=
IMAGES=
DEMO ?= "baremetal"

all:
	./launch-bao.sh $(PLATFORM) $(CONFIG) $(IMAGES)

demo:
	./bao-demo.sh $(PLATFORM) $(DEMO)

clean:
	@rm -rf ./wrkdir
# Add clean for all other repo?

clean-demo:
	make clean -C ../bao-demos PLATFORM=$(PLATFORM) DEMO=$(DEMO)
	make distclean -C ../bao-demos PLATFORM=$(PLATFORM) DEMO=$(DEMO)