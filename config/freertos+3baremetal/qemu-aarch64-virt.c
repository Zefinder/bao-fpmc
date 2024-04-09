#include <config.h>

VM_IMAGE(baremetal_image1, XSTR(../images/test/baremetal.bin));
VM_IMAGE(baremetal_image2, XSTR(../images/test/baremetal.bin));
VM_IMAGE(baremetal_image3, XSTR(../images/test/baremetal.bin));
VM_IMAGE(freertos_image, XSTR(../images/test/freertos.bin));

struct config config = {
    
    CONFIG_HEADER
    
    .vmlist_size = 4,
    .vmlist = {
        { 
            .image = {
                .base_addr = 0x50000000,
                .load_addr = VM_IMAGE_OFFSET(baremetal_image1),
                .size = VM_IMAGE_SIZE(baremetal_image1)
            },

            .entry = 0x50000000,

            .platform = {
                .cpu_num = 1,
                
                .region_num = 1,
                .regions =  (struct vm_mem_region[]) {
                    {
                        .base = 0x50000000,
                        .size = 0x4000000 
                    }
                },

                .dev_num = 2,
                .devs =  (struct vm_dev_region[]) {
                    {   
                        /* PL011 */
                        .pa = 0x9000000,
                        .va = 0x9000000,
                        .size = 0x10000,
                        // .interrupt_num = 1,
                        // .interrupts = (irqid_t[]) {33}                        
                    },
                    {   
                        /* Arch timer interrupt */
                        .interrupt_num = 1,
                        .interrupts = 
                            (irqid_t[]) {27}                         
                    }
                },

                .arch = {
                    .gic = {
                        .gicd_addr = 0x08000000,
                        .gicr_addr = 0x080A0000,
                    }
                }
            },
        },        
        { 
            .image = {
                .base_addr = 0x50000000,
                .load_addr = VM_IMAGE_OFFSET(baremetal_image2),
                .size = VM_IMAGE_SIZE(baremetal_image2)
            },

            .entry = 0x50000000,

            .platform = {
                .cpu_num = 1,
                
                .region_num = 1,
                .regions =  (struct vm_mem_region[]) {
                    {
                        .base = 0x50000000,
                        .size = 0x4000000 
                    }
                },

                .dev_num = 2,
                .devs =  (struct vm_dev_region[]) {
                    {   
                        /* PL011 */
                        .pa = 0x9000000,
                        .va = 0x9000000,
                        .size = 0x10000,
                        // .interrupt_num = 1,
                        // .interrupts = (irqid_t[]) {33}                        
                    },
                    {   
                        /* Arch timer interrupt */
                        .interrupt_num = 1,
                        .interrupts = 
                            (irqid_t[]) {27}                         
                    }
                },

                .arch = {
                    .gic = {
                        .gicd_addr = 0x08000000,
                        .gicr_addr = 0x080A0000,
                    }
                }
            },
        },
        { 
            .image = {
                .base_addr = 0x50000000,
                .load_addr = VM_IMAGE_OFFSET(baremetal_image3),
                .size = VM_IMAGE_SIZE(baremetal_image3)
            },

            .entry = 0x50000000,

            .platform = {
                .cpu_num = 1,
                
                .region_num = 1,
                .regions =  (struct vm_mem_region[]) {
                    {
                        .base = 0x50000000,
                        .size = 0x4000000 
                    }
                },

                .dev_num = 2,
                .devs =  (struct vm_dev_region[]) {
                    {   
                        /* PL011 */
                        .pa = 0x9000000,
                        .va = 0x9000000,
                        .size = 0x10000,
                        // .interrupt_num = 1,
                        // .interrupts = (irqid_t[]) {33}                        
                    },
                    {   
                        /* Arch timer interrupt */
                        .interrupt_num = 1,
                        .interrupts = 
                            (irqid_t[]) {27}                         
                    }
                },

                .arch = {
                    .gic = {
                        .gicd_addr = 0x08000000,
                        .gicr_addr = 0x080A0000,
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
                        .interrupt_num = 1,
                        .interrupts = (irqid_t[]) {33}                         
                    },
                    {   
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
