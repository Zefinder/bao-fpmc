# Imports
import os

# Dictionaries with constants
image_information = {
    'zcu': {
        'baremetal': {
            'entry': 0x20000000,
            'gic': {
                'gicd': 0xf9010000,
                'gicc': 0xf9020000
            }
        },
        'freertos': {
            'entry': 0x0,
            'gic': {
                'gicd': 0xf9010000,
                'gicc': 0xf9020000
            }
        },
        'linux': {
            'entry': 0x00200000,
            'gic': {
                'gicd': 0xf9010000,
                'gicc': 0xf9020000
            }
        }
    },
    'rpi4': {
        'baremetal': {
            'entry': 0x200000,
            'gic': {
                'gicd': 0xff841000,
                'gicc': 0xff842000
            }
        },
        'freertos': {
            'entry': 0x0,
            'gic': {
                'gicd': 0xf9010000,
                'gicc': 0xf9020000
            }
        },
        'linux': {
            'entry': 0x20000000,
            'gic': {
                'gicd': 0xff841000,
                'gicc': 0xff842000
            }
        },
        'zephyr': {
            'entry': 0x80000000,
            'gic': {
                'gicd': 0xff841000,
                'gicc': 0xff842000
            }
        }
    },
    'qemu-aarch64-virt': {
        'baremetal': {
            'entry': 0x50000000,
            'gic': {
                'gicd': 0x08000000,
                'gicc': 0x080A0000
            }
        },
        'freertos': {
            'entry': 0x0,
            'gic': {
                'gicd': 0xf9010000,
                'gicc': 0xf9020000
            }
        },
        'linux': {
            'entry': 0x60000000,
            'gic': {
                'gicd': 0x08000000,
                'gicc': 0x080A0000
            }
        },
        'zephyr': {
            'entry': 0x80000000,
            'gic': {
                'gicd': 0x08000000,
                'gicc': 0x080A0000
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
    
{body:s}
}}
'''

shared_memory_structure = '''    // Shared memory for IPC
    .shmemlist_size = {shmemlist_size:s},
    .shmemlist = (struct shmem[]) {{
{shmemlist_template:s}
    }},
'''

vm_list_structure = '''    // VM configuration
    .vmlist_size = {vmlist_size:d},
    .vmlist = {{
{vm_config:s}
    }},
'''

platform_structure = '''            // Platform description
            .platform = {{
                // CPU number
                .cpu_num = {cpu_number:d},
                
{region_description:s}

{ipc_description:s}

{device_description:s}

{architecture_description:s}
            }}
'''

region_structure = '''                // Memory description
                .region_num = {region_num:d},
                .regions = (struct vm_mem_regions[]) {{
{region_template:s}
                }},
'''

# Template declarations
image_declaration_template = 'VM_IMAGE({vm_name:s}, XSTR({vm_path:s})),'
shared_memory_template = '[{index:d}] = {{.size = 0x{size:08x}}},'
image_template = '''            // Image description
            .image = {{
                .base_addr = 0x{base_addr:08x},
                .load_addr = VM_IMAGE_OFFSET({image_name:s}),
                .size = VM_IMAGE_SIZE({image_name:s})
            }},
'''
entry_point_template = '            .entry = 0x{address:08x},'
region_template = '''                    {{
                        .base = 0x{base:08x},
                        .size = 0x{size:08x}
                    }},
'''

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
            shmem_size_str = input(f'What is the size of the shared memory n°{shmem_index:d}? (type in hexadecimal without 0x) (by default 1000)\n')
            try:
                shmem_size = int(shmem_size_str, 16)
            except:
                shmem_size = 0x1000
            
            shmem_sizes.append(shmem_size)
            
    return shmem_sizes


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
            region_base_str = input(f'What is the base address for region n°{region_index:d}? (type in hexadecimal without 0x) (default 0)\n')
            try:
                region_base = max(int(region_base_str, 16), 0)
            except:
                region_base = 0
        
        # Ask for region size
        region_size_str = input(f'What is the size of region n°{region_index:d}? (type in hexadecimal without 0x) (default 0)\n')
        try:
            region_size = max(int(region_size_str, 16), 0)
        except:
            region_size = 0
        
        regions += region_template.format(base=region_base, size=region_size)
        region_index += 1
    
    completed_region = region_structure.format(region_num=region_number, region_template=regions)
    return completed_region


def declare_ipc(ipc_number: int) -> str:

    return ''


def declare_devices(device_number: int) -> str:

    return '                // No devices'


def image_declaration(cpu_number: int, platform_name: str, shmem_sizes: list[int]) -> dict[int, dict[str, str]]:
    image_folder = os.path.join(os.getcwd(), '..', 'images')
    
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
        image['image_path'] = image_path
        
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
        image = declared_images[image_index]
        entry_point = platform_information[image['configuration']]['entry']
        
        print(f'For the image n°{image_index:d} named {image["image_name"]:s}...')
        
        # Generate image string
        completed_image = generate_image_config(base_address=entry_point, image_name=image["image_name"])
        declared_config['image'] = completed_image
        
        # Set entry point string
        declared_config['entry'] = entry_point_template.format(address=entry_point)
        
        # Ask for region number
        region_number_str = input('How many region number do you want? (by default 1)\n')
        try:
            region_number = max(int(region_number_str), 1)
        except:
            region_number = 1
        
        completed_region = declare_regions(entry_point=entry_point, platform_name=platform_name, region_number=region_number)
        declared_config['regions'] = completed_region
        
        # Ask for IPC (if any shared memory)
        if len(shmem_sizes) > 0: 
            ipc_number_str = input('How many IPC do you want? (by default 1)\n')
            try:
                ipc_number = max(int(ipc_number_str), 0)
            except:
                ipc_number = 1
            
            if ipc_number != 0:
                completed_ipc = declare_ipc(ipc_number)
                declared_config['ipc'] = completed_ipc

        if 'ipc' not in declared_config:
            declared_config['ipc'] = '                // No IPC'
        
        # Ask for devices (do not count the arch timer)
        device_number_str = input('How many devices do you want? (DO NOT INCLUDE THE ARCH TIMER) (by default 1)')
        try: 
            device_number = max(int(device_number_str), 0)
        except:
            device_number = 1
        
        completed_device = declare_devices(device_number)
        declared_config['devices'] = completed_device
    
    print(declared_config['image'], declared_config['entry'], platform_structure.format(cpu_number=cpu_number, region_description=declared_config['regions'], ipc_description=declared_config['ipc'], device_description=declared_config['devices'], architecture_description='                // Architecture not done yet'), sep='\n')
        
    return declared_config


def main():
    # Welcome guest
    print("Welcome to the Bao's configuration generator")
    
    # Ask for platform name
    platform_name = ''
    while not platform_name: 
        platform_name = input('Please enter the name of the platform you want to use (leave empty if you want to see suggestions):\n')
        if platform_name not in image_information:
            # Reset platform name
            platform_name = ''
            
            # Show all platforms
            print(f'Valid platforms are {list(image_information.keys()):s}. More can be added in the future...')

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
    
    # Ask everything about OSes
    declared_images = image_declaration(cpu_number=cpu_number, platform_name=platform_name, shmem_sizes=shmem_sizes)
    
    
    # print(config_file_structure.format(images='', body=vm_list_structure.format(vmlist_size=1, image_structure=image_structure.format())))

if __name__ == '__main__':
    main()