# Imports
import sys
import importlib 
from analyse_utils import get_module_variables
import matplotlib.pyplot as plt
import numpy as np
from typing import Any

# Constants
width = 0.18

# TODO Create benchmark logs for them, values on paper...
interference_fpsched_min = [64, 64, 64]
interference_fpsched_max = [65, 65, 68]
interference_fpsched_avg = [64, 64, 64]

def generate_bar_diagram(solo_varnames: dict[str,Any], interference1_legacy_varnames: dict[str,Any], 
                         interference2_legacy_varnames: dict[str,Any], interference3_legacy_varnames: dict[str,Any]) -> None:
    execution = ('legacy', 'fpsched')
    execution_max = {
        'solo': (solo_varnames['max'], solo_varnames['max']),
        '1 interference': (interference1_legacy_varnames['max'], interference_fpsched_max[0]),
        '2 interferences': (interference2_legacy_varnames['max'], interference_fpsched_max[1]),
        '3 interferences': (interference3_legacy_varnames['max'], interference_fpsched_max[2]),
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
    ax.set_title('Prefetch time by number of interference, without and with scheduler')
    ax.set_xticks(x + 1.5 * width, execution)
    ax.legend(loc='upper left')
    ax.set_ylim(0, 400)


def main():
    # Setting path to root folder
    sys.path.append('../')

    # Import extracted log files 
    solo_log = importlib.import_module("extract.bench_solo_legacy-execution-legacy-24-04-22-1")
    
    interference1_legacy_log = importlib.import_module("extract.bench_interference1_legacy-execution-legacy-24-04-22-1")
    interference2_legacy_log = importlib.import_module("extract.bench_interference2_legacy-execution-legacy-24-04-22-1")
    interference3_legacy_log = importlib.import_module("extract.bench_interference3_legacy-execution-legacy-24-04-22-1")
    
    # interference1_fpsched_log = importlib.import_module("extract.bench_interference1_legacy-execution-legacy-24-04-22-1")
    # interference2_fpsched_log = importlib.import_module("extract.bench_interference2_legacy-execution-legacy-24-04-22-1")
    # interference3_fpsched_log = importlib.import_module("extract.bench_interference3_legacy-execution-legacy-24-04-22-1") 

    # Extract all variables 
    solo_varnames = get_module_variables(solo_log)
    interference1_legacy_varnames = get_module_variables(interference1_legacy_log)
    interference2_legacy_varnames = get_module_variables(interference2_legacy_log)
    interference3_legacy_varnames = get_module_variables(interference3_legacy_log)

    # Generate histogram
    # plt.figure()
    generate_bar_diagram(solo_varnames=solo_varnames,
                         interference1_legacy_varnames=interference1_legacy_varnames,
                         interference2_legacy_varnames=interference2_legacy_varnames,
                         interference3_legacy_varnames=interference3_legacy_varnames)
    plt.savefig('../graphs/comparison_legacy_fpsched.png')


if __name__ == '__main__':
    main()