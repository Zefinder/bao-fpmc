# Imports
import sys
import importlib 
from analyse_utils import get_module_variables
import matplotlib.pyplot as plt
import numpy as np
from typing import Any

# Constants
frequency = 1000 # Hz
min_data_size = 20
max_data_size = 440
data_size_increment = 20

elapsed_time_array_varname_template = 'elapsed_time_array_{data_size:d}kB_{nop_number:d}nop'
min_varname_template = 'min_{data_size:d}kB_{nop_number:d}nop'
max_varname_template = 'max_{data_size:d}kB_{nop_number:d}nop'

# Functions
def get_best_min_nop_number(nop_log_varnames: dict[str,Any], data_size: int) -> np.intp:
    filtered_varnames = [v for k, v in nop_log_varnames.items() if k.startswith('min_' + str(data_size) + 'kB')]
    return np.argmin(filtered_varnames)


def get_best_max_nop_number(nop_log_varnames: dict[str,Any], data_size: int) -> np.intp:
    filtered_varnames = [v for k, v in nop_log_varnames.items() if k.startswith('max_' + str(data_size) + 'kB')]
    return np.argmin(filtered_varnames)


def get_best_avg_nop_number(nop_log_varnames: dict[str,Any], data_size: int) -> np.intp:
    filtered_varnames = [np.average(v) for k, v in nop_log_varnames.items() if k.startswith('elapsed_time_array_' + str(data_size) + 'kB')]
    return np.argmin(filtered_varnames)


def generate_colormesh(title: str, x: list[int], y: list[int], z: list[list[int]], cmap: str = 'viridis', vmin: int | None = None, vmax: int | None = None) -> None:
    # Set plot title
    plt.title(title)
    
    # Set X axis
    plt.xticks(x)
    plt.xlabel('Number of interfering core')
    
    # Set Y axis
    plt.yticks(y)
    plt.ylabel('Prefetch data size (kB)')
    
    # Create mesh
    c = plt.pcolormesh(x, y, z, cmap=cmap, vmax=vmax)
    plt.colorbar(c)
    
    
def generate_max_line_graph(no_interference_log_varname: dict[str,Any],
                            nop_log_varnames: dict[str,Any],
                            title: str) -> None:
    # Plot worst execution time against data size
    # Generate X range 
    x = [*range(min_data_size, max_data_size + 1, data_size_increment)]
    
    y_no_interference = []
    y_no_nop = []
    y_optimal_nop = []
    # Get y values
    for data_size in x:
        y_no_interference.append(no_interference_log_varname[max_varname_template.format(data_size=data_size, nop_number=0)])
        y_no_nop.append(nop_log_varnames[max_varname_template.format(data_size=data_size, nop_number=0)])
        y_optimal_nop.append(nop_log_varnames[max_varname_template.format(data_size=data_size, nop_number=get_best_max_nop_number(nop_log_varnames, data_size))])
    
    # Set plot title
    plt.title(title)
    
    plt.xticks(x)
    plt.plot(x, y_no_interference, label='No interference')
    plt.plot(x, y_no_nop, label='0 NOP')
    plt.plot(x, y_optimal_nop, label='Optimal NOP')
    plt.legend()
    

def generate_max_total_comparison(no_interference_log_varname: dict[str,Any],
                                  nop1_log_varnames: dict[str,Any],
                                  nop2_log_varnames: dict[str,Any],
                                  nop3_log_varnames: dict[str,Any],
                                  title: str) -> None:
    # Plot worst execution time against data size
    # Generate X range 
    x = [*range(min_data_size, max_data_size + 1, data_size_increment)]
    
    y_no_interference = []
    y_no_nop1 = []
    y_optimal_nop1 = []
    y_no_nop2 = []
    y_optimal_nop2 = []
    y_no_nop3 = []
    y_optimal_nop3 = []
    # Get y values
    for data_size in x:
        y_no_interference.append(no_interference_log_varname[max_varname_template.format(data_size=data_size, nop_number=0)])
        
        # 1 Interference
        y_no_nop1.append(nop1_log_varnames[max_varname_template.format(data_size=data_size, nop_number=0)])
        y_optimal_nop1.append(nop1_log_varnames[max_varname_template.format(data_size=data_size, nop_number=get_best_max_nop_number(nop1_log_varnames, data_size))])
        
        # 2 Interferences
        y_no_nop2.append(nop2_log_varnames[max_varname_template.format(data_size=data_size, nop_number=0)])
        y_optimal_nop2.append(nop2_log_varnames[max_varname_template.format(data_size=data_size, nop_number=get_best_max_nop_number(nop2_log_varnames, data_size))])
        
        # 3 Interferences
        y_no_nop3.append(nop3_log_varnames[max_varname_template.format(data_size=data_size, nop_number=0)])
        y_optimal_nop3.append(nop3_log_varnames[max_varname_template.format(data_size=data_size, nop_number=get_best_max_nop_number(nop3_log_varnames, data_size))])
    
    # Set plot title
    plt.title(title)
    
    plt.xticks(x)
    plt.plot(x, y_no_interference, label='No interference')
    
    plt.plot(x, y_no_nop1, label='0 NOP (1 interference)')
    plt.plot(x, y_optimal_nop1, label='Optimal NOP (1 interference)')
    
    plt.plot(x, y_no_nop2, label='0 NOP (2 interference)')
    plt.plot(x, y_optimal_nop2, label='Optimal NOP (2 interferences)')
    
    plt.plot(x, y_no_nop3, label='0 NOP (3 interference)')
    plt.plot(x, y_optimal_nop3, label='Optimal NOP (3 interferences)')
    
    plt.legend()
    

def generate_min_total_comparison(no_interference_log_varname: dict[str,Any],
                                  nop1_log_varnames: dict[str,Any],
                                  nop2_log_varnames: dict[str,Any],
                                  nop3_log_varnames: dict[str,Any],
                                  title: str) -> None:
    # Plot worst execution time against data size
    # Generate X range 
    x = [*range(min_data_size, max_data_size + 1, data_size_increment)]
    
    y_no_interference = []
    y_no_nop1 = []
    y_optimal_nop1 = []
    y_no_nop2 = []
    y_optimal_nop2 = []
    y_no_nop3 = []
    y_optimal_nop3 = []
    # Get y values
    for data_size in x:
        y_no_interference.append(no_interference_log_varname[min_varname_template.format(data_size=data_size, nop_number=0)])
        
        # 1 Interference
        y_no_nop1.append(nop1_log_varnames[min_varname_template.format(data_size=data_size, nop_number=0)])
        y_optimal_nop1.append(nop1_log_varnames[min_varname_template.format(data_size=data_size, nop_number=get_best_min_nop_number(nop1_log_varnames, data_size))])
        
        # 2 Interferences
        y_no_nop2.append(nop2_log_varnames[min_varname_template.format(data_size=data_size, nop_number=0)])
        y_optimal_nop2.append(nop2_log_varnames[min_varname_template.format(data_size=data_size, nop_number=get_best_min_nop_number(nop2_log_varnames, data_size))])
        
        # 3 Interferences
        y_no_nop3.append(nop3_log_varnames[min_varname_template.format(data_size=data_size, nop_number=0)])
        y_optimal_nop3.append(nop3_log_varnames[min_varname_template.format(data_size=data_size, nop_number=get_best_min_nop_number(nop3_log_varnames, data_size))])
    
    # Set plot title
    plt.title(title)
    
    plt.xticks(x)
    plt.plot(x, y_no_interference, label='No interference')
    
    plt.plot(x, y_no_nop1, label='0 NOP (1 interference)')
    plt.plot(x, y_optimal_nop1, label='Optimal NOP (1 interference)')
    
    plt.plot(x, y_no_nop2, label='0 NOP (2 interference)')
    plt.plot(x, y_optimal_nop2, label='Optimal NOP (2 interferences)')
    
    plt.plot(x, y_no_nop3, label='0 NOP (3 interference)')
    plt.plot(x, y_optimal_nop3, label='Optimal NOP (3 interferences)')
    
    plt.legend()
    

def generate_min_line_graph(no_interference_log_varname: dict[str,Any],
                            nop_log_varnames: dict[str,Any],
                            title: str) -> None:
    # Plot worst execution time against data size
    # Generate X range 
    x = [*range(min_data_size, max_data_size + 1, data_size_increment)]
    
    y_no_interference = []
    y_no_nop = []
    y_optimal_nop = []
    # Get y values
    for data_size in x:
        y_no_interference.append(no_interference_log_varname[min_varname_template.format(data_size=data_size, nop_number=0)])
        y_no_nop.append(nop_log_varnames[min_varname_template.format(data_size=data_size, nop_number=0)])
        y_optimal_nop.append(nop_log_varnames[min_varname_template.format(data_size=data_size, nop_number=get_best_min_nop_number(nop_log_varnames, data_size))])
    
    # Set plot title
    plt.title(title)
    plt.xticks(x)
    plt.plot(x, y_no_interference, label='No interference')
    plt.plot(x, y_no_nop, label='0 NOP')
    plt.plot(x, y_optimal_nop, label='Optimal NOP')
    plt.legend()
    
    
def generate_avg_line_graph(no_interference_log_varname: dict[str,Any],
                            nop_log_varnames: dict[str,Any],
                            title: str) -> None:
    # Plot worst execution time against data size
    # Generate X range 
    x = [*range(min_data_size, max_data_size + 1, data_size_increment)]
    
    y_no_interference = []
    y_no_nop = []
    y_optimal_nop = []
    # Get y values
    for data_size in x:
        y_no_interference.append(np.average(no_interference_log_varname[elapsed_time_array_varname_template.format(data_size=data_size, nop_number=0)]))
        y_no_nop.append(np.average(nop_log_varnames[elapsed_time_array_varname_template.format(data_size=data_size, nop_number=0)]))
        y_optimal_nop.append(np.average(nop_log_varnames[elapsed_time_array_varname_template.format(data_size=data_size, nop_number=get_best_avg_nop_number(nop_log_varnames, data_size))]))
    
    # Set plot title
    plt.title(title)
    plt.xticks(x)
    plt.plot(x, y_no_interference, label='No interference')
    plt.plot(x, y_no_nop, label='0 NOP')
    plt.plot(x, y_optimal_nop, label='Optimal NOP')
    plt.legend()
    

def generate_max_colormesh(no_interference_log_varname: dict[str,Any],
                           nop1_log_varnames: dict[str,Any],
                           nop2_log_varnames: dict[str,Any],
                           nop3_log_varnames: dict[str,Any]) -> None:    
    # Generate X range
    x = [*range(0, 4)]
    
    # Generate Y range
    y = [*range(min_data_size, max_data_size + 1, data_size_increment)]
    
    # Get all values for min
    z = []
    for data_size in y:
        values = []
        
        # For no interference no search
        values.append(no_interference_log_varname[max_varname_template.format(data_size=data_size, nop_number=0)])
        
        # For other interferences, get the best nop value
        values.append(nop1_log_varnames[max_varname_template.format(data_size=data_size, nop_number=get_best_max_nop_number(nop1_log_varnames, data_size))])
        values.append(nop2_log_varnames[max_varname_template.format(data_size=data_size, nop_number=get_best_max_nop_number(nop2_log_varnames, data_size))])
        values.append(nop3_log_varnames[max_varname_template.format(data_size=data_size, nop_number=get_best_max_nop_number(nop3_log_varnames, data_size))])
        
        z.append(values)
    
    # Set plot title and generate plot
    title = 'Minimum of worst execution time (in µs) for the\noptimal number of NOP during prefetch'
    generate_colormesh(title=title, x=x, y=y, z=z, cmap='terrain', vmax=550)
    
    
def generate_max_nop_colormesh(nop1_log_varnames: dict[str,Any],
                               nop2_log_varnames: dict[str,Any],
                               nop3_log_varnames: dict[str,Any]) -> None:
    # Generate X range
    x = [*range(1, 4)]
    
    # Generate Y range
    y = [*range(min_data_size, max_data_size + 1, data_size_increment)]
    
    # Get all values for min
    z = []
    for data_size in y:
        values = []
        values.append(get_best_max_nop_number(nop1_log_varnames, data_size))
        values.append(get_best_max_nop_number(nop2_log_varnames, data_size))
        values.append(get_best_max_nop_number(nop3_log_varnames, data_size))
        
        z.append(values)
        
    # Set plot title and generate plot
    title = 'Optimal number of NOP to get minimal worst\nvalues during prefetch'
    generate_colormesh(title=title, x=x, y=y, z=z, cmap='Paired')
    

def generate_min_colormesh(no_interference_log_varname: dict[str,Any],
                           nop1_log_varnames: dict[str,Any],
                           nop2_log_varnames: dict[str,Any],
                           nop3_log_varnames: dict[str,Any]) -> None:
    # Generate X range
    x = [*range(0, 4)]
    
    # Generate Y range
    y = [*range(min_data_size, max_data_size + 1, data_size_increment)]
    
    # Get all values for min
    z = []
    for data_size in y:
        values = []
        
        # For no interference no search
        values.append(no_interference_log_varname[min_varname_template.format(data_size=data_size, nop_number=0)])
        
        # For other interferences, get the best nop value
        values.append(nop1_log_varnames[min_varname_template.format(data_size=data_size, nop_number=get_best_min_nop_number(nop1_log_varnames, data_size))])
        values.append(nop2_log_varnames[min_varname_template.format(data_size=data_size, nop_number=get_best_min_nop_number(nop2_log_varnames, data_size))])
        values.append(nop3_log_varnames[min_varname_template.format(data_size=data_size, nop_number=get_best_min_nop_number(nop3_log_varnames, data_size))])
        
        z.append(values)
        
    # Set plot title and generate plot
    title = 'Minimum of best execution time (in µs) for the\noptimal number of NOP during prefetch'
    generate_colormesh(title=title, x=x, y=y, z=z, cmap='terrain', vmax=550)
    
    
def generate_min_nop_colormesh(nop1_log_varnames: dict[str,Any],
                               nop2_log_varnames: dict[str,Any],
                               nop3_log_varnames: dict[str,Any]) -> None:
    # Generate X range
    x = [*range(1, 4)]
    
    # Generate Y range
    y = [*range(min_data_size, max_data_size + 1, data_size_increment)]
    
    # Get all values for min
    z = []
    for data_size in y:
        values = []
        values.append(get_best_min_nop_number(nop1_log_varnames, data_size))
        values.append(get_best_min_nop_number(nop2_log_varnames, data_size))
        values.append(get_best_min_nop_number(nop3_log_varnames, data_size))
        
        z.append(values)
        
    # Set plot title and generate plot
    title = 'Optimal number of NOP to get minimal best\nvalues during prefetch'
    generate_colormesh(title=title, x=x, y=y, z=z, cmap='Paired')
    
    
def generate_avg_colormesh(no_interference_log_varname: dict[str,Any],
                           nop1_log_varnames: dict[str,Any],
                           nop2_log_varnames: dict[str,Any],
                           nop3_log_varnames: dict[str,Any]) -> None:    
    # Generate X range
    x = [*range(0, 4)]
    
    # Generate Y range
    y = [*range(min_data_size, max_data_size + 1, data_size_increment)]
    
    # Get all values for min
    z = []
    for data_size in y:
        values = []
        
        # For no interference no search
        values.append(np.average(no_interference_log_varname[elapsed_time_array_varname_template.format(data_size=data_size, nop_number=0)]))
        
        # For other interferences, get the best nop value
        values.append(np.average(nop1_log_varnames[elapsed_time_array_varname_template.format(data_size=data_size, nop_number=get_best_avg_nop_number(nop1_log_varnames, data_size))]))
        values.append(np.average(nop2_log_varnames[elapsed_time_array_varname_template.format(data_size=data_size, nop_number=get_best_avg_nop_number(nop2_log_varnames, data_size))]))
        values.append(np.average(nop3_log_varnames[elapsed_time_array_varname_template.format(data_size=data_size, nop_number=get_best_avg_nop_number(nop3_log_varnames, data_size))]))
        
        z.append(values)
        
    # Set plot title and generate plot
    title = 'Minimum of average execution time (in µs) for the\noptimal number of NOP during prefetch'
    generate_colormesh(title=title, x=x, y=y, z=z, cmap='terrain', vmax=550)


def main():
    # Setting path to root folder
    sys.path.append('../')

    # Import extracted log files 
    no_interference_log = importlib.import_module('extract.bench_solo_legacy-execution-nop-24-05-07-1')
    nop1_log = importlib.import_module('extract.bench_interference1_nop-execution-nop-24-05-14-1')
    nop2_log = importlib.import_module('extract.bench_interference2_nop-execution-nop-24-05-14-1')
    nop3_log = importlib.import_module('extract.bench_interference3_nop-execution-nop-24-05-13-2')
    
    # Extract variables
    no_interference_log_varname = get_module_variables(no_interference_log)
    nop1_log_varnames = get_module_variables(nop1_log)
    nop2_log_varnames = get_module_variables(nop2_log)
    nop3_log_varnames = get_module_variables(nop3_log)
    
    # Generate color mesh with max difference
    plt.figure('Max difference', figsize=(10, 11))
    generate_max_colormesh(no_interference_log_varname=no_interference_log_varname,
                           nop1_log_varnames=nop1_log_varnames,
                           nop2_log_varnames=nop2_log_varnames,
                           nop3_log_varnames=nop3_log_varnames)
    plt.savefig('../graphs/bench_max_nop_diff.png')
    
    # Generate color mesh with optimal number of nop
    plt.figure('Min NOP number for worst', figsize=(10, 11))
    generate_max_nop_colormesh(nop1_log_varnames=nop1_log_varnames,
                               nop2_log_varnames=nop2_log_varnames,
                               nop3_log_varnames=nop3_log_varnames)
    plt.savefig('../graphs/bench_max_nop_number.png')
    
    # Generate color mesh with min difference
    plt.figure('Min difference', figsize=(10, 11))
    generate_min_colormesh(no_interference_log_varname=no_interference_log_varname,
                           nop1_log_varnames=nop1_log_varnames,
                           nop2_log_varnames=nop2_log_varnames,
                           nop3_log_varnames=nop3_log_varnames)
    plt.savefig('../graphs/bench_min_nop_diff.png')
    
    # Generate color mesh with optimal number of nop
    plt.figure('Min NOP number for best', figsize=(10, 11))
    generate_min_nop_colormesh(nop1_log_varnames=nop1_log_varnames,
                               nop2_log_varnames=nop2_log_varnames,
                               nop3_log_varnames=nop3_log_varnames)
    plt.savefig('../graphs/bench_min_nop_number.png')
    
    # Generate color mesh with min difference
    plt.figure('Avg difference', figsize=(10, 11))
    generate_avg_colormesh(no_interference_log_varname=no_interference_log_varname,
                           nop1_log_varnames=nop1_log_varnames,
                           nop2_log_varnames=nop2_log_varnames,
                           nop3_log_varnames=nop3_log_varnames)
    plt.savefig('../graphs/bench_avg_nop_diff.png')
    
    # 1 Interference comparison
    plt.figure('Max nop1 difference', figsize=(12, 8))
    generate_max_line_graph(no_interference_log_varname=no_interference_log_varname,
                            nop_log_varnames=nop1_log_varnames,
                            title='Worst execution time improvement for 1 interference')
    plt.savefig('../graphs/bench_max_nop1_impact.png')
    
    plt.figure('Min nop1 difference', figsize=(12, 8))
    generate_min_line_graph(no_interference_log_varname=no_interference_log_varname,
                            nop_log_varnames=nop1_log_varnames,
                            title='Best execution time improvement for 1 interference')
    plt.savefig('../graphs/bench_min_nop1_impact.png')
    
    plt.figure('Avg nop1 difference', figsize=(12, 8))
    generate_avg_line_graph(no_interference_log_varname=no_interference_log_varname,
                            nop_log_varnames=nop1_log_varnames,
                            title='Average execution time improvement for 1 interference')
    plt.savefig('../graphs/bench_avg_nop1_impact.png')
    
    # 2 Interference comparison
    plt.figure('Max nop2 difference', figsize=(12, 8))
    generate_max_line_graph(no_interference_log_varname=no_interference_log_varname,
                            nop_log_varnames=nop2_log_varnames,
                            title='Worst execution time improvement for 2 interferences')
    plt.savefig('../graphs/bench_max_nop2_impact.png')
    
    plt.figure('Min nop2 difference', figsize=(12, 8))
    generate_min_line_graph(no_interference_log_varname=no_interference_log_varname,
                            nop_log_varnames=nop2_log_varnames,
                            title='Best execution time improvement for 2 interferences')
    plt.savefig('../graphs/bench_min_nop2_impact.png')
    
    plt.figure('Avg nop2 difference', figsize=(12, 8))
    generate_avg_line_graph(no_interference_log_varname=no_interference_log_varname,
                            nop_log_varnames=nop2_log_varnames,
                            title='Average execution time improvement for 2 interferences')
    plt.savefig('../graphs/bench_avg_nop2_impact.png')
    
    # 3 Interferences comparison
    plt.figure('Max nop3 difference', figsize=(12, 8))
    generate_max_line_graph(no_interference_log_varname=no_interference_log_varname,
                            nop_log_varnames=nop3_log_varnames,
                            title='Worst execution time improvement for 3 interferences')
    plt.savefig('../graphs/bench_max_nop3_impact.png')
    
    plt.figure('Min nop3 difference', figsize=(12, 8))
    generate_min_line_graph(no_interference_log_varname=no_interference_log_varname,
                            nop_log_varnames=nop3_log_varnames,
                            title='Best execution time improvement for 3 interferences')
    plt.savefig('../graphs/bench_min_nop3_impact.png')
    
    plt.figure('Avg nop3 difference', figsize=(12, 8))
    generate_avg_line_graph(no_interference_log_varname=no_interference_log_varname,
                            nop_log_varnames=nop3_log_varnames,
                            title='Average execution time improvement for 3 interferences')
    plt.savefig('../graphs/bench_avg_nop3_impact.png')
    
    # Compare everything at the same time 
    plt.figure('Total max comparison', figsize=(12, 8))
    generate_max_total_comparison(no_interference_log_varname=no_interference_log_varname,
                                  nop1_log_varnames=nop1_log_varnames,
                                  nop2_log_varnames=nop2_log_varnames,
                                  nop3_log_varnames=nop3_log_varnames,
                                  title='Worst execution time improvement for all 3 interferences')
    plt.savefig('../graphs/bench_all_max_nop_impact.png')
    
    # Compare everything at the same time 
    plt.figure('Total min comparison', figsize=(12, 8))
    generate_min_total_comparison(no_interference_log_varname=no_interference_log_varname,
                                  nop1_log_varnames=nop1_log_varnames,
                                  nop2_log_varnames=nop2_log_varnames,
                                  nop3_log_varnames=nop3_log_varnames,
                                  title='Worst execution time improvement for all 3 interferences')
    plt.savefig('../graphs/bench_all_min_nop_impact.png')
        
if __name__ == '__main__':
    main()
