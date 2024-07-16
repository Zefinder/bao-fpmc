#include <config.h>

// List of used images
VM_IMAGE(freertos_image0, XSTR(../images/build/freertos_hyp.bin));
VM_IMAGE(baremetal_image1, XSTR(../images/build/baremetal_hyp.bin));


// Configuration struct
struct config config = {
    
    CONFIG_HEADER
    
    // No shared memory

    // VM configuration
    .vmlist_size = 2,
    .vmlist = {
        {
            // CPU affinity
            .cpu_affinity = 0b0001,

            // Image description
            .image = {
                .base_addr = 0x00000000,
                .load_addr = VM_IMAGE_OFFSET(freertos_image0),
                .size = VM_IMAGE_SIZE(freertos_image0)
            },

            // Entry point
            .entry = 0x00000000,

            // Platform description
            .platform = {
                // CPU number
                .cpu_num = 1,
                
                // Memory description
                .region_num = 1,
                .regions = (struct vm_mem_region[]) {
                    {
                        .base = 0x00000000,
                        .size = 0x08000000
                    },
                },

                // No IPC

                // Device description
                .dev_num = 2,
                .devs = (struct vm_dev_region[]) {
                    {
                        .pa = 0xfe215000,
                        .va = 0xff000000,
                        .size = 0x00010000,
                    },
                    {
                        /* Arch timer interrupt */
                        .interrupt_num = 1,
                        .interrupts = (irqid_t[]) {27}
                    }
                },

                // Architecture description
                .arch = {
                    .gic = {
                        .gicd_addr = 0xf9010000,
                        .gicc_addr = 0xf9020000
                    }
                }
            }
        },
        {
            // Image description
            .image = {
                .base_addr = 0x00200000,
                .load_addr = VM_IMAGE_OFFSET(baremetal_image1),
                .size = VM_IMAGE_SIZE(baremetal_image1)
            },

            // Entry point
            .entry = 0x00200000,

            // Platform description
            .platform = {
                // CPU number
                .cpu_num = 1,
                
                // Memory description
                .region_num = 1,
                .regions = (struct vm_mem_region[]) {
                    {
                        .base = 0x00200000,
                        .size = 0x04000000
                    },
                },

                // No IPC

                // Device description
                .dev_num = 2,
                .devs = (struct vm_dev_region[]) {
                    {
                        .pa = 0xfe215000,
                        .va = 0xfe215000,
                        .size = 0x00010000,
                    },
                    {
                        /* Arch timer interrupt */
                        .interrupt_num = 1,
                        .interrupts = (irqid_t[]) {27}
                    }
                },

                // Architecture description
                .arch = {
                    .gic = {
                        .gicd_addr = 0xff841000,
                        .gicc_addr = 0xff842000
                    }
                }
            }
        },
    },
};
