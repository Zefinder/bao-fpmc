#include <config.h>

// VM_IMAGE(baremetal_image, XSTR(../images/test/baremetal.bin));
VM_IMAGE(freertos_image, XSTR(../images/test/freertos.bin));
VM_IMAGE(freertos_image2, XSTR(../images/build/freertos_hyp.bin));

struct config config = {
    
    CONFIG_HEADER
    
    .vmlist_size = 2,
    .vmlist = {
        {
            .image = {
                .base_addr = 0,
                .load_addr = VM_IMAGE_OFFSET(freertos_image2),
                .size = VM_IMAGE_SIZE(freertos_image2)
            },

            .entry = 0,

            .platform = {
                .cpu_num = 1,
                
                .region_num = 1,
                .regions =  (struct vm_mem_region[]) {
                    {
                        .base = 0,
                        .size = 0x8000000
                    }
                },

            //    .ipc_num = 1,
            //     .ipcs = (struct ipc[]) {
            //         {
            //             .base = 0x70000000,
            //             .size = 0x00010000,
            //             .shmem_id = 0,
            //             .interrupt_num = 1,
            //             .interrupts = (irqid_t[]) {52}
            //         }
            //     },

                .dev_num = 2,
                .devs =  (struct vm_dev_region[]) {
                    {   
                        /* PL011 */
                        .pa = 0x9000000,
                        .va = 0xff000000,
                        .size = 0x10000, 
                        .interrupt_num = 1,
                        .interrupts = (irqid_t[]) {33}                         
                    },
                    {   
                        /* Timer */
                        .interrupt_num = 1,
                        .interrupts = (irqid_t[]) {27}                         
                    }
               },

                .arch = {
                    .gic = {
                       .gicd_addr = 0xf9010000,
                       .gicr_addr = 0xf9020000
                    }
                }
            },
        },
        {
            .image = {
                .base_addr = 0x0,
                .load_addr = VM_IMAGE_OFFSET(freertos_image),
                .size = VM_IMAGE_SIZE(freertos_image)
            },

            .entry = 0x0,

            .platform = {
                .cpu_num = 1,
                
                .region_num = 1,
                .regions =  (struct vm_mem_region[]) {
                    {
                        .base = 0x0,
                        .size = 0x8000000
                    }
                },

               .ipc_num = 1,
                .ipcs = (struct ipc[]) {
                    {
                        .base = 0x70000000,
                        .size = 0x00010000,
                        .shmem_id = 0,
                        .interrupt_num = 1,
                        .interrupts = (irqid_t[]) {52}
                    }
                },

                .dev_num = 2,
                .devs =  (struct vm_dev_region[]) {
                    {   
                        /* PL011 */
                        .pa = 0x9000000,
                        .va = 0xff000000,
                        .size = 0x10000, 
                        // .interrupt_num = 1,
                        // .interrupts = (irqid_t[]) {33}                         
                    },
                    {   
                        /* Timer */
                        .interrupt_num = 1,
                        .interrupts = (irqid_t[]) {27}                         
                    }
               },

                .arch = {
                    .gic = {
                        .gicd_addr = 0xf9010000,
                        .gicr_addr = 0xf9020000,
                    }
                }
            },
        }
    },
};
