# Imports
import sys
import importlib 
from analyse_utils import *
import matplotlib.pyplot as plt
import numpy as np
from typing import Any

# Constants
frequency = 1000 # Hz
min_data_size = 1
max_data_size = 512
data_size_increment = 1
break_point = 312
width = 0.18

elapsed_time_array_varname_template = elapsed_time_array_varname_template_generator.format(template='{name:s}_ns')
min_varname_template = min_varname_template_generator.format(template='{name:s}_ns')
max_varname_template = max_varname_template_generator.format(template='{name:s}_ns')


def generate_microbench_bargraph(microbench_log_varname: dict[str, Any]) -> None:
    execution = ['microbenchmarks']
    execution_max = {
        'hypercall': (microbench_log_varname[max_varname_template.format(name='hypercall')]),
        'IPI': (microbench_log_varname[max_varname_template.format(name='ipi')]),
        'arbitration (prio 0)': (microbench_log_varname[max_varname_template.format(name='request_prio0')]),
        'arbitration (prio 1)': (microbench_log_varname[max_varname_template.format(name='request_prio2')]),
        'arbitration (prio 2)': (microbench_log_varname[max_varname_template.format(name='request_prio4')]),
        'arbitration (prio 3)': (microbench_log_varname[max_varname_template.format(name='request_prio6')]),
        'revoke (prio 0)': (microbench_log_varname[max_varname_template.format(name='revoke_prio0')]),
        'revoke (prio 1)': (microbench_log_varname[max_varname_template.format(name='revoke_prio2')]),
        'revoke (prio 2)': (microbench_log_varname[max_varname_template.format(name='revoke_prio4')]),
        'revoke (prio 3)': (microbench_log_varname[max_varname_template.format(name='revoke_prio6')]),
    }
    
    x = np.arange(len(execution))  # the label locations
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained', figsize=(9, 8))

    for mode, value in execution_max.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, value, width, label=mode)
        ax.bar_label(rects, padding=2)
        multiplier += 1
    
    # Add some text for labels, title and custom x-axis tick labels, etc...
    plt.tick_params(bottom=False, labelbottom=False)
    ax.set_ylabel('Execution time (in ns)')
    ax.set_title('Worst case execution time for important PREM steps (in nanoseconds)')
    ax.legend(loc='upper right')
    

def main():
    # Setting path to root folder
    sys.path.append('../')

    # Import extracted log files 
    microbench_log = importlib.import_module('extract.bench_interference3_nop-execution-microbenchmarks-24-06-25-2')
    
    # Extract variables
    microbench_log_varname = get_module_variables(microbench_log)
    
    # Plot curves with solo and interference 
    plt.figure('microbench bars', figsize=(16, 10))
    generate_microbench_bargraph(microbench_log_varname=microbench_log_varname)
    plt.savefig('../graphs/wcet_microbenchmarks.png')
    

if __name__ == '__main__':
    main()