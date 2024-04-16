# Imports
import os
from typing import Any

# Dictionaries with constants
image_information = {
    'zcu': {
        'baremetal': {
            'entry': 0x20000000,
            'ipc': 0x70000000,
            'uart': {
                'pa': 0xff000000,
                'va': 0xff000000,
                'interrupt_number': 53
            },
            'gic': {
                'gicd': 0xf9010000,
                'gicc': 0xf9020000
            }
        },
        'freertos': {
            'entry': 0x0,
            'ipc': 0x70000000,
            'uart': {
                'pa': 0xff000000,
                'va': 0xff000000,
                'interrupt_number': 53
            },
            'gic': {
                'gicd': 0xf9010000,
                'gicc': 0xf9020000
            }
        },
        'linux': {
            'entry': 0x00200000,
            'ipc': 0xf0000000,
            'uart': {
                'pa': 0xff000000,
                'va': 0xff000000,
                'interrupt_number': 53
            },
            'gic': {
                'gicd': 0xf9010000,
                'gicc': 0xf9020000
            }
        }
    },
    'rpi4': {
        'baremetal': {
            'entry': 0x200000,
            'ipc': 0x70000000,
            'uart': {
                'pa': 0xfe215000,
                'va': 0xfe215000,
                'interrupt_number': 125
            },
            'gic': {
                'gicd': 0xff841000,
                'gicc': 0xff842000
            }
        },
        'freertos': {
            'entry': 0x0,
            'ipc': 0x70000000,
            'uart': {
                'pa': 0xfe215000,
                'va': 0xff000000,
                'interrupt_number': 125
            },
            'gic': {
                'gicd': 0xf9010000,
                'gicc': 0xf9020000
            }
        },
        'linux': {
            'entry': 0x20000000,
            'ipc': 0xf0000000,
            'uart': {
                'pa': 0xfe215000,
                'va': 0xfe215000,
                'interrupt_number': 125
            },
            'gic': {
                'gicd': 0xff841000,
                'gicc': 0xff842000,
            }
        },
        'zephyr': {
            'entry': 0x80000000,
            'ipc': 0x70000000,
            'uart': {
                'pa': 0xfe215000,
                'va': 0xfe215000,
                'interrupt_number': 125
            },
            'gic': {
                'gicd': 0xff841000,
                'gicc': 0xff842000
            }
        }
    },
    'qemu-aarch64-virt': {
        'baremetal': {
            'entry': 0x50000000,
            'ipc': 0x70000000,
            'uart': {
                'pa': 0x9000000,
                'va': 0x9000000,
                'interrupt_number': 33
            },
            'gic': {
                'gicd': 0x08000000,
                'gicr': 0x080A0000
            }
        },
        'freertos': {
            'entry': 0x0,
            'ipc': 0x70000000,
            'uart': {
                'pa': 0x9000000,
                'va': 0xff000000,
                'interrupt_number': 33
            },
            'gic': {
                'gicd': 0xf9010000,
                'gicr': 0xf9020000
            }
        },
        'linux': {
            'entry': 0x60000000,
            'ipc': 0xf0000000,
            'uart': {
                'pa': 0x9000000,
                'va': 0x9000000,
                'interrupt_number': 33
            },
            'gic': {
                'gicd': 0x08000000,
                'gicr': 0x080A0000
            }
        },
        'zephyr': {
            'entry': 0x80000000,
            'ipc': 0x70000000,
            'uart': {
                'pa': 0x9000000,
                'va': 0x9000000,
                'interrupt_number': 33
            },
            'gic': {
                'gicd': 0x08000000,
                'gicr': 0x080A0000
            }
        }
    }
}

# Structure declarations 
config_file_structure = '''#include <config.h>

// List of used images
{images:s}

// Configuration struct
struct config config = {{
    
    CONFIG_HEADER
    
{shared_memory:s}
{vm_config:s}}};
'''
shared_memory_structure = '''    // Shared memory for IPC
    .shmemlist_size = {shmemlist_size:d},
    .shmemlist = (struct shmem[]) {{
{shmemlist_template:s}    }},
'''
vm_list_structure = '''    // VM configuration
    .vmlist_size = {vmlist_size:d},
    .vmlist = {{
{vm_config:s}    }},
'''
vm_element_structure = '''        {{
{image_description:s}
{entry_point:s}
{platform_description:s}        }},
'''
platform_structure = '''            // Platform description
            .platform = {{
                // CPU number
                .cpu_num = {cpu_number:s},
                
{region_description:s}
{ipc_description:s}
{device_description:s}
{architecture_description:s}            }}
'''
region_structure = '''                // Memory description
                .region_num = {region_num:d},
                .regions = (struct vm_mem_region[]) {{
{region_template:s}                }},
'''
ipc_structure = '''                // IPC description
                .ipc_num = {ipc_number:d},
                .ipcs = (struct ipc[]) {{
{ipc_template:s}                }},
'''
device_structure = '''                // Device description
                .dev_num = {dev_num:d},
                .devs = (struct vm_dev_region[]) {{
{device_template:s}                }},
'''

# Template declarations
image_declaration_template = 'VM_IMAGE({vm_name:s}, XSTR({vm_path:s}));'
shared_memory_template = '        [{index:d}] = {{.size = 0x{size:08x}}},'
image_template = '''            // Image description
            .image = {{
                .base_addr = 0x{base_addr:08x},
                .load_addr = VM_IMAGE_OFFSET({image_name:s}),
                .size = VM_IMAGE_SIZE({image_name:s})
            }},
'''
entry_point_template = '''            // Entry point
            .entry = 0x{address:08x},
'''
region_template = '''                    {{
                        .base = 0x{base:08x},
                        .size = 0x{size:08x}
                    }},
'''
ipc_template = '''                    {{
                        .base = 0x{base:08x},
                        .size = 0x{size:08x},
                        .shmem_id = {shmemid:d},
                        .interrupt_num = 1,
                        .interrupts = (irqid_t[]) {{{ipc_interrupt:d}}}
                    }},
'''
device_template_no_intr = '''                    {{
                        .pa = 0x{pa:08x},
                        .va = 0x{va:08x},
                        .size = 0x{size:08x},
                    }},
'''
device_template_intr = '''                    {{
                        .pa = 0x{pa:08x},
                        .va = 0x{va:08x},
                        .size = 0x{size:08x},
                        .interrupt_num = {interrupt_num:d},
                        .interrupts = (irqid_t[]) {{{dev_interrupts:s}}}
                    }},
'''
timer_template = '''                    {{
                        /* Arch timer interrupt */
                        .interrupt_num = 1,
                        .interrupts = (irqid_t[]) {{{timer_interrupt:d}}}
                    }}
'''
architecture_template = '''                // Architecture description
                .arch = {{
                    .gic = {{
                        .{gic1:s}_addr = 0x{gic1_addr:08x},
                        .{gic2:s}_addr = 0x{gic2_addr:08x}
                    }}
                }}
'''

ipc_interrupt_number = 52
timer_interrupt_number = 27


def shememlist_definition() -> list[int]:
    shmem_sizes = []
    
    # Ask if there is any shared memory for IPC
    shmemlist_size_str = input('How many shared memory do you want? They are used for IPC (by default 0)\n')
    try:
        shmemlist_size = int(shmemlist_size_str)
    except:
        shmemlist_size = 0
    
    # Ask the size for any shared memory
    if shmemlist_size != 0:
        for shmem_index in range(0, shmemlist_size):
            shmem_size_str = input(f'What is the size of the shared memory n°{shmem_index:d}? (type in hexadecimal without 0x) (by default 10000)\n')
            try:
                shmem_size = int(shmem_size_str, 16)
            except:
                shmem_size = 0x10000
            
            shmem_sizes.append(shmem_size)
            
    return shmem_sizes


def generate_shared_memory(shmem_sizes: list[int]) -> str:
    shared_memories = ''
    
    if len(shmem_sizes) == 0:
        completed_shared_memory = '    // No shared memory\n'
    else:
        for shmem_index in range(0, len(shmem_sizes)):
            shared_memories = shared_memory_template.format(index=shmem_index, size=shmem_sizes[shmem_index]) + '\n'
        
        completed_shared_memory = shared_memory_structure.format(shmemlist_size=len(shmem_sizes), shmemlist_template=shared_memories)
    return completed_shared_memory


def generate_image_config(base_address: int, image_name: str) -> str:
    completed_image = image_template.format(base_addr=base_address, image_name=image_name)
    return completed_image


def declare_regions(entry_point: str, platform_name: str, region_number: int) -> str:
    region_index = 0
    regions = ''
    
    while region_index < region_number:
        region_base = 0
        region_size = 0
        
        # If first region, then address given by the entry point (except for zcu's with Linux)
        if region_index == 0:
            if platform_name == 'zcu' and entry_point == 0x200000:
                region_base = 0
            else:
                region_base = entry_point
        
        # Else you ask for the base address (in hexa)
        else:
            region_base_str = input(f'What is the base address for region n°{region_index:d}? (type in hexadecimal without 0x) (by default 0)\n')
            try:
                region_base = max(int(region_base_str, 16), 0)
            except:
                region_base = 0
        
        # Ask for region size
        region_size_str = input(f'What is the size of region n°{region_index:d}? (type in hexadecimal without 0x) (by default 0)\n')
        try:
            region_size = max(int(region_size_str, 16), 0)
        except:
            region_size = 0
        
        # Append to regions
        regions += region_template.format(base=region_base, size=region_size)
        
        # Next one
        region_index += 1
    
    completed_region = region_structure.format(region_num=region_number, region_template=regions)
    return completed_region


def declare_ipc(ipc_number: int, shmem_sizes: list[int], os_information: dict[str, Any]) -> str:
    ipcs = ''
    ipc_index = 0
    
    while ipc_index < ipc_number:
        # Ask for which shared memory to use
        shmemid = -1
        while shmemid < 0:
            shmemid_str = input(f'Which shared memory do you want to use for IPC n°{ipc_index}? (from 0 to {ipc_number -1})\n')
            try:
                shmemid = int(shmemid_str)
            except:
                shmemid = -1
        
        # Get information from constant dict and shared memory list
        ipc_base = os_information['ipc']
        ipc_size = shmem_sizes[shmemid]
        
        # Append to IPC
        ipcs += ipc_template.format(base=ipc_base, size=ipc_size, shmemid=shmemid, ipc_interrupt=ipc_interrupt_number)

        # Next one!
        ipc_index += 1

    completed_ipc = ipc_structure.format(ipc_number=ipc_number, ipc_template=ipcs)
    return completed_ipc


def declare_devices(device_number: int, os_information: dict[str, Any]) -> str:
    devices = ''
    device_index = 0
    has_uart = 0
    
    while device_index < device_number:
        pa = -1
        va = -1
        size = -1
        interrupt_num = 0
        interrupts = []
        
        # If there is no UART yet, ask if the device is a UART
        if has_uart == 0:
            confirmation = input('Is the device an UART? [Y/n]\n')
            
            # If it is an UART, then auto add everything
            if confirmation.lower() != 'n':
                has_uart = 1
                pa = os_information['uart']['pa']
                va = os_information['uart']['va']
                
                confirmation = input('Does this UART has access to the RX interrupt? [Y/n]\n')
                
                # If RX then we add the interrupt
                if confirmation.lower() == 'n':
                    interrupt_num = 0
                else:
                    interrupt_num = 1
                    interrupts.append(str(os_information['uart']['interrupt_number']))
                    
        # Here if device is not UART or if UART already defined, pa should be -1
        if pa == -1:
            # Ask for physical address of device
            while pa == -1: 
                pa_str = input(f'What is the physical address of the device n°{device_index:d}? (type in hexadecimal without 0x)\n')
                try:
                    pa = max(int(pa_str, 16), -1)
                except:
                    pa = -1
                    
            # Ask for virtual address of device
            while va == -1:
                va_str = input(f'What is the virtual address of the device n°{device_index:d}? (type in hexadecimal without 0x)\n')
                try:
                    va = max(int(va_str, 16), -1)
                except:
                    va = -1
                        
            # Ask for number of interruptions
            interrupt_num_str = input(f'What is the number of interruptions associated to the device? (by default 0)\n')
            try:
                interrupt_num = max(int(interrupt_num_str), 0)
            except:
                interrupt_num = 0
            
            # If any interruptions, ask their id
            if interrupt_num > 0:
                interrupt_index = 0
                while interrupt_index < interrupt_num:
                    interrupt_id = -1
                    while interrupt_id == -1:
                        interrupt_id_str = input(f'What is the interruption number of interruption n°{interrupt_index}?\n')
                        try:
                            interrupt_id = max(int(interrupt_id_str), -1)
                        except:
                            interrupt_id = -1
                    
                    interrupts.append(str(interrupt_id))
                    interrupt_index += 1
        
        # Ask for size of device
        size_str = input(f'What is the size of device n°{device_index}? (type in hexadecimal without 0x) (by default 10000)\n')
        try:
            size = max(int(size_str, 16), 0)
        except:
            size = 0x10000
        
        # Append to devices
        if interrupt_num == 0:
            devices += device_template_no_intr.format(pa=pa, va=va, size=size)
        else:
            interrupts = ','.join(interrupts)
            devices += device_template_intr.format(pa=pa, va=va, size=size, interrupt_num=interrupt_num, dev_interrupts=interrupts)
        
        # Increment device
        device_index += 1
    
    # Add arch timer if wanted
    confirmation = input('Do you want the arch timer? [Y/n]\n')
    if confirmation.lower() != 'n':
        devices += timer_template.format(timer_interrupt=timer_interrupt_number)
        device_number += 1
    
    completed_device = device_structure.format(dev_num=device_number, device_template=devices)
    return completed_device


def generate_architecture_config(gic_registers: dict[str, int]) -> str:
    gic1 = list(gic_registers.keys())[0]
    gic2 = list(gic_registers.keys())[1]
    completed_architecture = architecture_template.format(gic1=gic1, gic1_addr=gic_registers[gic1], gic2=gic2, gic2_addr=gic_registers[gic2])
    return completed_architecture


def image_declaration(cpu_number: int, platform_name: str, shmem_sizes: list[int]) -> dict[int, dict[str, str]]:
    image_folder = os.path.join('..', 'images')
    
    declared_config = {}
    declared_images = {}

    platform_information = image_information[platform_name]
    used_cpu = 0
    image_name = ''
    image_index = 0
    
    # Ask if you want to add an image
    while (used_cpu == 0 or image_name) and used_cpu < cpu_number:
        image = {}
        image_name = input('What OS do you want to use? (if you do not need more, leave empty)\n')
        
        # If image name empty, we leave IFF there is at least one image
        if not image_name:
            if used_cpu == 0:
                print('You need to specify at least one image!')
            else:
                print('No more OS to add, going to next section...')
            continue
        
        # If image do not exist, ask if they want to use baremetal value
        elif image_name not in platform_information:
            confirmation = input('Image do not exist, if you want to continue, baremetal values will be used [y/N]\n')
            if confirmation.lower() == 'y':
                image['image_name'] = f'{image_name:s}_image{image_index:d}'
                image['configuration'] = 'baremetal'
            
            else:
                # Else we just reask
                continue
        
        # If image exist for the platform, we just add!                
        else:
            image['image_name'] = f'{image_name:s}_image{image_index:d}'
            image['configuration'] = image_name
        
        # Ask path to image
        image_path = ''
        while not image_path:
            image_path = input('What is the path of the image from the "images" folder?\n')
            if not os.path.exists(os.path.join(image_folder, image_path)):
                image_path = ''
                print('Image path do not exist, try again')
        image['image_path'] = os.path.join(image_folder, image_path)
        
        # Ask how many CPUs we want for this image
        max_cpu = cpu_number - used_cpu
        image_cpu_str = input(f'How many CPUs do you want for this image? (by default 1, max {max_cpu:d})\n')
        try:
            image_cpu = int(image_cpu_str)
        except:
            image_cpu = 1
            
        # Check that there are enough CPUs
        if image_cpu > max_cpu:
            print(f'You want to put too many CPUs... max value selected ({max_cpu:d})')
            image_cpu = max_cpu
        
        # Put CPU number in dict
        image['cpu_number'] = f'{image_cpu:d}'
        
        # Add image to declared images
        declared_images[image_index] = image
        
        # Increment used cpus and image index
        used_cpu += image_cpu
        image_index += 1
                
    print('It is now time to ask information for each OS image')
    for image_index in list(declared_images.keys()):
        image_config = {}
        
        image = declared_images[image_index]
        entry_point = platform_information[image['configuration']]['entry']
        
        print(f'For the image n°{image_index:d} named {image["image_name"]:s}...')
        
        # Set image name and path in config
        image_config['image_name'] = image["image_name"]
        image_config['image_path'] = image["image_path"]
        
        # Set the number of CPU of the image
        image_config['cpu_number'] = image['cpu_number']
        
        # Generate image string
        completed_image = generate_image_config(base_address=entry_point, image_name=image["image_name"])
        image_config['image'] = completed_image
        
        # Set entry point string
        image_config['entry'] = entry_point_template.format(address=entry_point)
        
        # Ask for region number
        region_number_str = input('How many region number do you want? (by default 1)\n')
        try:
            region_number = max(int(region_number_str), 1)
        except:
            region_number = 1
        
        completed_region = declare_regions(entry_point=entry_point, platform_name=platform_name, region_number=region_number)
        image_config['regions'] = completed_region
        
        # Ask for IPC (if any shared memory)
        if len(shmem_sizes) > 0: 
            ipc_number_str = input('How many IPC do you want? (by default 1)\n')
            try:
                ipc_number = max(int(ipc_number_str), 0)
            except:
                ipc_number = 1
            
            if ipc_number != 0:
                completed_ipc = declare_ipc(ipc_number=ipc_number, shmem_sizes=shmem_sizes, os_information=platform_information[image['configuration']])
                image_config['ipc'] = completed_ipc

        if 'ipc' not in image_config:
            image_config['ipc'] = '                // No IPC\n'
        
        # Ask for devices (do not count the arch timer)
        device_number_str = input('How many devices do you want? (DO NOT INCLUDE THE ARCH TIMER) (by default 1)\n')
        try: 
            device_number = max(int(device_number_str), 0)
        except:
            device_number = 1
        
        completed_device = declare_devices(device_number=device_number, os_information=platform_information[image['configuration']])
        image_config['devices'] = completed_device
        
        # Generate architecture
        completed_architectre = generate_architecture_config(gic_registers=platform_information[image['configuration']]['gic'])
        image_config['architecture'] = completed_architectre
        
        # Add image config to declared config
        declared_config[image_index] = image_config
            
    return declared_config


def generate_image_declaration(generation_config: dict[int, dict[str, str]]) -> str:
    completed_image_declaration = ''
    for image_index in generation_config:
        completed_image_declaration += image_declaration_template.format(vm_name=generation_config[image_index]['image_name'], vm_path=generation_config[image_index]['image_path']) + '\n'
    
    return completed_image_declaration


def generate_configuration(competed_image_declaration: str, completed_shared_memory: str, generation_config: dict[int, dict[str, str]]) -> str:
    vm_config = ''
    for image_configuration in generation_config.values():
        platform_description = platform_structure.format(cpu_number=image_configuration['cpu_number'],
                                                         region_description=image_configuration['regions'],
                                                         ipc_description=image_configuration['ipc'],
                                                         device_description=image_configuration['devices'],
                                                         architecture_description=image_configuration['architecture'])
        
        vm_config += vm_element_structure.format(image_description=image_configuration['image'],
                                    entry_point=image_configuration['entry'],
                                    platform_description=platform_description)
    
    vm_list = vm_list_structure.format(vmlist_size=len(generation_config), vm_config=vm_config)
    completed_configuration = config_file_structure.format(images=competed_image_declaration,
                                                           shared_memory=completed_shared_memory,
                                                           vm_config=vm_list)
    return completed_configuration


def main():
    # Welcome guest
    print("Welcome to the Bao's configuration generator")
    
    # Ask for platform name
    platform_name = ''
    config_platform_name = ''
    while not platform_name: 
        config_platform_name = input('Please enter the name of the platform you want to use (leave empty if you want to see suggestions):\n')
              
        if config_platform_name.lower() not in image_information:
            # Reset platform name
            platform_name = ''
            
            # Show all platforms
            print(f'Valid platforms are {", ".join(list(image_information.keys())):s}. ZCU can be both 102 or 104. More platforms can be added in the future...')
        else:
            if config_platform_name.lower() == 'zcu':
                zcu_number = 0
                while zcu_number != 102 or zcu_number != 104:
                    zcu_number_str = input('Which ZCU do you want to use? (102 or 104)\n')
                    try:
                        zcu_number = int(zcu_number_str)
                    except:
                        zcu_number = 0
                
                platform_name = config_platform_name + str(zcu_number)
            else: 
                platform_name = config_platform_name

    # Ask for config name
    config_name = ''
    while not config_name: 
        config_name = input('Please enter your configuration name:\n')
    
    # Create path to config file
    config_dir_path = os.path.join(os.getcwd(), '..', 'config', config_name)
    config_file_path = os.path.join(config_dir_path, platform_name + '.c')
    
    # Check if config file already exists
    if os.path.exists(config_file_path):
        # Asks if want to override it 
        confirmation = input('Do you want to override it? [y/N]\n')
        if confirmation.lower() != 'y':
            print("Alright, we don't touch it! Quitting...")
            exit(0)
        
        # Delete the file
        os.remove(config_file_path)
    else:
        # Create if directory does not exist
        if not os.path.exists(config_dir_path):
            os.mkdir(config_dir_path)
            
    # Ask number of CPU
    cpu_number_str = input('How many CPUs do you have? (by default 4)\n')
    try:
        cpu_number = int(cpu_number_str)
    except:
        cpu_number = 4
    
    # Ask everything about shared memory
    shmem_sizes = shememlist_definition()
    
    # Generate shared memory config
    completed_shared_memory = generate_shared_memory(shmem_sizes=shmem_sizes)
    
    # Ask everything about OSes
    generation_config = image_declaration(cpu_number=cpu_number, platform_name=config_platform_name, shmem_sizes=shmem_sizes)
    
    # Generate image declaration
    competed_image_declaration = generate_image_declaration(generation_config=generation_config)

    # Generate configuration string
    completed_configuration = generate_configuration(competed_image_declaration=competed_image_declaration, completed_shared_memory=completed_shared_memory, generation_config=generation_config)
    
    # Create and write the configuration file (overriding mode)
    configuration_file = open(config_file_path, 'w')
    
    # Write configuration
    configuration_file.write(completed_configuration)
    
    # Close file and thank user
    configuration_file.close()
    print('Configuration file generated, please verify it and do not hesitate to add things to it, this is just a base configuration')
    
if __name__ == '__main__':
    main()