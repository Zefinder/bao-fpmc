# Imports
import sys
import os
from numpy import random, ndarray, dtype, int_
from typing import Any

# Constants
freertos_str = 'freertos'
baremetal_str = 'baremetal'
both_str = 'both'

freertos_path = os.path.join('..', 'freertos-bao-fpmc', 'src', 'inc', 'appdata.h')
baremetal_path = os.path.join('..', 'baremetal-bao-fpmc', 'src', 'inc', 'appdata.h')

data_size = 1024
value_min = 0
value_max = 2**8

appdata_h_template = """/* THIS FILE HAS BEEN GENERATED, ALL MODIFICATIONS WILL BE OVERRIDEN WHEN REGENERATING IT */
#ifndef __APPDATA_H__
#define __APPDATA_H__

uint8_t appdata[MAX_DATA_SIZE] = {{ 
    {data:s}
}};

#endif
"""

# Functions
def generate_random_data() -> ndarray[Any, dtype[int_]]:
    return random.randint(low=value_min, high=value_max, size=(data_size))


def generate_file(path: str):
    random_data = generate_random_data()
    data_str = ''
    
    # Concatenate all values in string
    nl_counter = 0
    for value in random_data:
        data_str += f'0x{value:02X}, '
        nl_counter += 1
        
        if nl_counter == 16:
            nl_counter = 0
            data_str += '\n\t'
        
    
    # Remove last space and comma
    data_str = data_str[:-2]
    
    # Add to template
    appdata_h_file = appdata_h_template.format(data=data_str)
    
    # If file exist then override it
    file = open(path, 'w')
    file.write(appdata_h_file)


def generate_freertos():
    generate_file(freertos_path)
    
    
def generate_baremetal():
    generate_file(baremetal_path)


def main():
    # The 1st argument will tell if we generate random data for baremetal, FreeRTOS or both
    argv = sys.argv
    if len(argv) != 2:
        print('There must be exactly one argument for the data generator')
        print(f'Possible values are {freertos_str:s}, {baremetal_str:s} or {both_str:s}')
        exit(1)
        
    target = argv[1].lower()
    if target == freertos_str:
        generate_freertos()
    elif target == baremetal_str:
        generate_baremetal()
    elif target == both_str:
        generate_freertos()
        generate_baremetal()
    else:
        print('Invalid argument...')
        print(f'Possible values are {freertos_str:s}, {baremetal_str:s} or {both_str:s}')
        exit(1)

if __name__ == '__main__':
    main()