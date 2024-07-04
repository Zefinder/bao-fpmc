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


def generate_microbench_max_bargraph(microbench_log_varname: dict[str, Any]) -> None:
    execution_max = {
        'hypercall': (microbench_log_varname[max_varname_template.format(name='hypercall')]),
        'IPI': (microbench_log_varname[max_varname_template.format(name='ipi')]),
        'request (prio 0)': (microbench_log_varname[max_varname_template.format(name='request_prio0')]),
        'request (prio 1)': (microbench_log_varname[max_varname_template.format(name='request_prio2')]),
        'request (prio 2)': (microbench_log_varname[max_varname_template.format(name='request_prio4')]),
        'request (prio 3)': (microbench_log_varname[max_varname_template.format(name='request_prio6')]),
        'revoke (prio 0)': (microbench_log_varname[max_varname_template.format(name='revoke_prio0')]),
        'revoke (prio 1)': (microbench_log_varname[max_varname_template.format(name='revoke_prio2')]),
        'revoke (prio 2)': (microbench_log_varname[max_varname_template.format(name='revoke_prio4')]),
        'revoke (prio 3)': (microbench_log_varname[max_varname_template.format(name='revoke_prio6')]),
    }
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained', figsize=(12, 11))

    for mode, value in execution_max.items():
        offset = width * multiplier
        rects = ax.bar(offset, value, width, label=mode)
        ax.bar_label(rects, padding=2)
        
        if 'hypercall' in mode or 'IPI' in mode or 'request (prio 3)' in mode:
            multiplier += .5
        
        multiplier += 1
    
    # Add some text for labels, title and custom x-axis tick labels, etc...
    ax.set_ylabel('Execution time (in ns)')
    ax.set_title('Worst case execution time for important PREM steps (in nanoseconds)')
    ax.set_xticks([0, 1.5 * width, 4.5 * width, 9 * width], ['hypercall', 'IPI', 'request', 'revoke'])
    ax.set_ylim(0, 6500)
    ax.legend(loc='upper right')
    
    
def generate_microbench_min_bargraph(microbench_log_varname: dict[str, Any]) -> None:
    execution_max = {
        'hypercall': (microbench_log_varname[min_varname_template.format(name='hypercall')]),
        'IPI': (microbench_log_varname[min_varname_template.format(name='ipi')]),
        'request (prio 0)': (microbench_log_varname[min_varname_template.format(name='request_prio0')]),
        'request (prio 1)': (microbench_log_varname[min_varname_template.format(name='request_prio2')]),
        'request (prio 2)': (microbench_log_varname[min_varname_template.format(name='request_prio4')]),
        'request (prio 3)': (microbench_log_varname[min_varname_template.format(name='request_prio6')]),
        'revoke (prio 0)': (microbench_log_varname[min_varname_template.format(name='revoke_prio0')]),
        'revoke (prio 1)': (microbench_log_varname[min_varname_template.format(name='revoke_prio2')]),
        'revoke (prio 2)': (microbench_log_varname[min_varname_template.format(name='revoke_prio4')]),
        'revoke (prio 3)': (microbench_log_varname[min_varname_template.format(name='revoke_prio6')]),
    }
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained', figsize=(12, 11))

    for mode, value in execution_max.items():
        offset = width * multiplier
        rects = ax.bar(offset, value, width, label=mode)
        ax.bar_label(rects, padding=2)
        
        if 'hypercall' in mode or 'IPI' in mode or 'request (prio 3)' in mode:
            multiplier += .5

        multiplier += 1
    
    # Add some text for labels, title and custom x-axis tick labels, etc...
    ax.set_ylabel('Execution time (in ns)')
    ax.set_title('Best case execution time for important PREM steps (in nanoseconds)')
    ax.set_xticks([0, 1.5 * width, 4.5 * width, 9 * width], ['hypercall', 'IPI', 'request', 'revoke'])
    ax.legend(loc='upper right')
    
    
def generate_microbench_avg_bargraph(microbench_log_varname: dict[str, Any]) -> None:
    execution_max = {
        'hypercall': (np.average(microbench_log_varname[elapsed_time_array_varname_template.format(name='hypercall')])),
        'IPI': (np.average(microbench_log_varname[elapsed_time_array_varname_template.format(name='ipi')])),
        'request (prio 0)': (np.average(microbench_log_varname[elapsed_time_array_varname_template.format(name='request_prio0')])),
        'request (prio 1)': (np.average(microbench_log_varname[elapsed_time_array_varname_template.format(name='request_prio2')])),
        'request (prio 2)': (np.average(microbench_log_varname[elapsed_time_array_varname_template.format(name='request_prio4')])),
        'request (prio 3)': (np.average(microbench_log_varname[elapsed_time_array_varname_template.format(name='request_prio6')])),
        'revoke (prio 0)': (np.average(microbench_log_varname[elapsed_time_array_varname_template.format(name='revoke_prio0')])),
        'revoke (prio 1)': (np.average(microbench_log_varname[elapsed_time_array_varname_template.format(name='revoke_prio2')])),
        'revoke (prio 2)': (np.average(microbench_log_varname[elapsed_time_array_varname_template.format(name='revoke_prio4')])),
        'revoke (prio 3)': (np.average(microbench_log_varname[elapsed_time_array_varname_template.format(name='revoke_prio6')])),
    }
    
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained', figsize=(12, 11))

    for mode, value in execution_max.items():
        offset = width * multiplier
        rects = ax.bar(offset, value, width, label=mode)
        ax.bar_label(rects, padding=2)
        
        if 'hypercall' in mode or 'IPI' in mode or 'request (prio 3)' in mode:
            multiplier += .5

        multiplier += 1
    
    # Add some text for labels, title and custom x-axis tick labels, etc...
    # plt.tick_params(bottom=False, labelbottom=False)
    ax.set_ylabel('Execution time (in ns)')
    ax.set_title('Average execution time for important PREM steps (in nanoseconds)')
    ax.set_xticks([0, 1.5 * width, 4.5 * width, 9 * width], ['hypercall', 'IPI', 'request', 'revoke'])
    ax.legend(loc='upper right')
            

def main():
    # Setting path to root folder
    sys.path.append('../')

    # Import extracted log files 
    microbench_log = importlib.import_module('extract.bench_interference3_nop-execution-microbenchmarks-24-07-03-1')
    microbench_solo_log = importlib.import_module('extract.bench_solo_legacy-execution-microbenchmarks-24-07-03-1')
    
    # Extract variables
    microbench_log_varname = get_module_variables(microbench_log)
    microbench_solo_log_varname = get_module_variables(microbench_solo_log)
    
    # Plot max time in bars
    plt.figure('microbench max bars')
    generate_microbench_max_bargraph(microbench_log_varname=microbench_log_varname)
    plt.savefig('../graphs/wcet_microbenchmarks_max.png')
    
    # Plot min time in bars 
    plt.figure('microbench min bars')
    generate_microbench_min_bargraph(microbench_log_varname=microbench_log_varname)
    plt.savefig('../graphs/wcet_microbenchmarks_min.png')
    
    # Plot average time in bars 
    plt.figure('microbench avg bars')
    generate_microbench_avg_bargraph(microbench_log_varname=microbench_log_varname)
    plt.savefig('../graphs/wcet_microbenchmarks_avg.png')
    
    # Plot max time in bars
    plt.figure('microbench solo max bars')
    generate_microbench_max_bargraph(microbench_log_varname=microbench_solo_log_varname)
    plt.savefig('../graphs/wcet_microbenchmarks_solo_max.png')
    
    # Plot min time in bars 
    plt.figure('microbench solo min bars')
    generate_microbench_min_bargraph(microbench_log_varname=microbench_solo_log_varname)
    plt.savefig('../graphs/wcet_microbenchmarks_solo_min.png')
    
    # Plot average time in bars 
    plt.figure('microbench solo avg bars')
    generate_microbench_avg_bargraph(microbench_log_varname=microbench_solo_log_varname)
    plt.savefig('../graphs/wcet_microbenchmarks_solo_avg.png')
    

if __name__ == '__main__':
    main()