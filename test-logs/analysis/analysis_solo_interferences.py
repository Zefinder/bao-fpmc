# Imports
import sys
import importlib 
from analyse_utils import *
import matplotlib.pyplot as plt
import numpy as np
from typing import Any

# Constants
width = 0.18

# Templates
elapsed_time_array_varname_template = elapsed_time_array_varname_template_generator.format(template='{data_size:d}kB_ns')
min_varname_template = min_varname_template_generator.format(template='{data_size:d}kB_ns')
max_varname_template = max_varname_template_generator.format(template='{data_size:d}kB_ns')


def generate_bar_diagram_200kB(solo_legacy_max_200kB: int,
                               interference1_legacy_max_200kB: int, 
                               interference2_legacy_max_200kB: int,
                               interference3_legacy_max_200kB: int,
                               solo_prem_max_200kB: int,
                               interference1_prem_max_200kB: int, 
                               interference2_prem_max_200kB: int,
                               interference3_prem_max_200kB: int) -> None:
    execution = ('legacy', 'fpsched')
    execution_max = {
        'solo': (solo_legacy_max_200kB / 1000, solo_prem_max_200kB/ 1000),
        '1 interference': (interference1_legacy_max_200kB / 1000, interference1_prem_max_200kB / 1000),
        '2 interferences': (interference2_legacy_max_200kB / 1000, interference2_prem_max_200kB / 1000),
        '3 interferences': (interference3_legacy_max_200kB / 1000, interference3_prem_max_200kB / 1000),
    }
    
    x = np.arange(len(execution))  # the label locations
    multiplier = 0

    fig, ax = plt.subplots(layout='constrained', figsize=(9, 8))

    for mode, value in execution_max.items():
        offset = width * multiplier
        rects = ax.bar(x + offset, value, width, label=mode)
        ax.bar_label(rects, padding=2)
        multiplier += 1
    
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Prefetch time (in µs)')
    ax.set_title('Prefetch time by number of interference, without and with scheduler\nprefetching 200kB')
    ax.set_xticks(x + 1.5 * width, execution)
    ax.legend(loc='upper left')
    ax.set_ylim(0, 400)


def plot_interference_curves(title: str,
                             solo_legacy_max: dict[str, Any],
                             interference_legacy_curve: dict[str, Any],
                             interference_prem_curve: dict[str, Any]):
    
    # Generate y values from the max
    x = [*range(1, len(solo_legacy_max) + 1)]
    y_solo = [solo_legacy_max[max_varname_template.format(data_size=data_size)] for data_size in x]
    y_interference_legacy = [interference_legacy_curve[max_varname_template.format(data_size=data_size)] for data_size in x]
    y_interference_prem = [interference_prem_curve[max_varname_template.format(data_size=data_size)] for data_size in x]
    
    plt.title(label=title)
    plt.plot(x, y_solo, label='Solo legacy')
    plt.plot(x, y_interference_legacy, label='Interference legacy')
    plt.plot(x, y_interference_prem, label='Interference PREM')
    plt.xlabel(xlabel='Prefetched data size (in kB)')
    plt.ylabel(ylabel='Prefetch time (in ns)')
    plt.legend()

def main():
    # Setting path to root folder
    sys.path.append('../')

    # Import extracted log files (big files so only max)
    # Legacy
    solo_legacy_max_varnames = get_variables_from_big_file('max_', '../extract/bench_solo_legacy-execution-solo-24-06-03-2.py')
    interference1_legacy_max_varnames = get_variables_from_big_file('max_', '../extract/bench_interference1_legacy-execution-solo-24-07-19-1.py')
    interference2_legacy_max_varnames = get_variables_from_big_file('max_', '../extract/bench_interference2_legacy-execution-solo-24-07-22-1.py')
    interference3_legacy_max_varnames = get_variables_from_big_file('max_', '../extract/bench_interference3_legacy-execution-solo-24-07-23-1.py')
    
    # PREM
    solo_prem_max_varnames = get_variables_from_big_file('max_', '../extract/bench_solo_legacy-execution-prem-solo-24-06-26-1.py')
    interference1_prem_max_varnames = get_variables_from_big_file('max_', '../extract/bench_interference1_legacy-execution-prem-solo-24-07-16-1.py')
    interference2_prem_max_varnames = get_variables_from_big_file('max_', '../extract/bench_interference2_legacy-execution-prem-solo-24-07-17-1.py')
    interference3_prem_max_varnames = get_variables_from_big_file('max_', '../extract/bench_interference3_legacy-execution-prem-solo-24-07-18-1.py')

    # Generate histogram
    plt.figure('200kB', figsize=(10, 10))
    generate_bar_diagram_200kB(solo_legacy_max_200kB=solo_legacy_max_varnames[max_varname_template.format(data_size=200)],
                               interference1_legacy_max_200kB=interference1_legacy_max_varnames[max_varname_template.format(data_size=200)],
                               interference2_legacy_max_200kB=interference2_legacy_max_varnames[max_varname_template.format(data_size=200)],
                               interference3_legacy_max_200kB=interference3_legacy_max_varnames[max_varname_template.format(data_size=200)],
                               solo_prem_max_200kB=solo_prem_max_varnames[max_varname_template.format(data_size=200)],
                               interference1_prem_max_200kB=interference1_prem_max_varnames[max_varname_template.format(data_size=200)], 
                               interference2_prem_max_200kB=interference2_prem_max_varnames[max_varname_template.format(data_size=200)],
                               interference3_prem_max_200kB=interference3_prem_max_varnames[max_varname_template.format(data_size=200)])
    plt.savefig('../graphs/comparison_legacy_fpsched_200kB.png')
    
    plt.figure('Interference 1', figsize=(15, 10))
    plot_interference_curves(title='Worst case execution time of the execution with 1 interfering core with and without PREM (in nanoseconds)',
                             solo_legacy_max=solo_legacy_max_varnames,
                             interference_legacy_curve=interference1_legacy_max_varnames,
                             interference_prem_curve=interference1_prem_max_varnames)
    plt.savefig('../graphs/comparison_prem_legacy_interference1.png')
    
    plt.figure('Interference 2', figsize=(15, 10))
    plot_interference_curves(title='Worst case execution time of the execution with 2 interfering cores with and without PREM (in nanoseconds)',
                             solo_legacy_max=solo_legacy_max_varnames,
                             interference_legacy_curve=interference2_legacy_max_varnames,
                             interference_prem_curve=interference2_prem_max_varnames)
    plt.savefig('../graphs/comparison_prem_legacy_interference2.png')
    
    plt.figure('Interference 3', figsize=(15, 10))
    plot_interference_curves(title='Worst case execution time of the execution with 3 interfering cores with and without PREM (in nanoseconds)',
                             solo_legacy_max=solo_legacy_max_varnames,
                             interference_legacy_curve=interference3_legacy_max_varnames,
                             interference_prem_curve=interference3_prem_max_varnames)
    plt.savefig('../graphs/comparison_prem_legacy_interference3.png')


if __name__ == '__main__':
    main()