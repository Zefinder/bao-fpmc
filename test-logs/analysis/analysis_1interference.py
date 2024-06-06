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

elapsed_time_array_varname_template = elapsed_time_array_varname_template_generator.format(template='{data_size:d}kB_ns')
min_varname_template = min_varname_template_generator.format(template='{data_size:d}kB_ns')
max_varname_template = max_varname_template_generator.format(template='{data_size:d}kB_ns')


def estimate_coefficients(x, y):
    # Number of observations/points 
    n = np.size(x) 

    # Mean of x and y vector 
    m_x = np.mean(x) 
    m_y = np.mean(y) 

    # Calculating cross-deviation and deviation about x 
    SS_xy = np.sum(y*x) - n*m_y*m_x 
    SS_xx = np.sum(x*x) - n*m_x*m_x 

    # Calculating regression coefficients 
    b_1 = SS_xy / SS_xx 
    b_0 = m_y - b_1*m_x 
    
    return (b_0, b_1) 


def generate_solo_interference_curve(solo_log_max_varnames: dict[str,Any],
                                         interference1_log_max_varnames: dict[str,Any]) -> None:
    # Generate x 
    x = [*range(min_data_size, max_data_size + 1, data_size_increment)]
    
    # For all sizes get the y value
    y_solo = [solo_log_max_varnames[max_varname_template.format(data_size=data_size)] for data_size in x]
    y_interference1 = [interference1_log_max_varnames[max_varname_template.format(data_size=data_size)] for data_size in x]
    
    # Set plot title
    plt.title('Worst case execution time for solo and one interference with respect to prefetched data size (in nanoseconds)')
    plt.xticks([*range(0, max_data_size + 1, 20)])
    plt.plot(x, y_solo, label='No interference')
    plt.plot(x, y_interference1, label='1 interference')
    plt.xlabel('Prefetched data size')
    plt.ylabel('Execution time')
    plt.legend()
    
    
def generate_solo_interference_ratio(solo_log_max_varnames: dict[str,Any],
                                         interference1_log_max_varnames: dict[str,Any]) -> None:
    # Generate x 
    x = [*range(min_data_size, max_data_size + 1, data_size_increment)]
    
    # For all sizes get the y value
    y_solo = [solo_log_max_varnames[max_varname_template.format(data_size=data_size)] for data_size in x]
    y_interference1 = [interference1_log_max_varnames[max_varname_template.format(data_size=data_size)] for data_size in x]
    y_ratio = [y_interference1[i] / y_solo[i] for i in range(0, len(y_solo))]
    
    # Set plot title
    plt.title('Ratio between worst case execution time of one interference and solo')
    plt.xticks([*range(0, max_data_size + 1, 20)])
    plt.xlabel('Prefetched data size')
    plt.ylim(2.1, 3.8)
    plt.plot(x, y_ratio)
    

def generate_solo_interference_difference(solo_log_max_varnames: dict[str,Any],
                                               interference1_log_max_varnames: dict[str,Any]) -> None:
    # Generate x 
    x = [*range(min_data_size, max_data_size + 1, data_size_increment)]
    
    # For all sizes get the y value
    y_solo = [solo_log_max_varnames[max_varname_template.format(data_size=data_size)] for data_size in x]
    y_interference1 = [interference1_log_max_varnames[max_varname_template.format(data_size=data_size)] for data_size in x]
    y_ratio = [(y_interference1[i] - y_solo[i]) / 1000 for i in range(0, len(y_solo))]
    
    # Set plot title
    plt.title('Difference between worst case execution time of one interference and solo (in microseconds)')
    plt.xticks([*range(0, max_data_size + 1, 20)])
    plt.plot(x, y_ratio)
    plt.xlabel('Prefetched data size')


def generate_solo_interference_regressed_curve(solo_log_max_varnames: dict[str,Any],
                                                    interference1_log_max_varnames: dict[str,Any]) -> None:
    # Generate x 
    x = np.array([*range(min_data_size, max_data_size + 1, data_size_increment)])
    
    # For all sizes get the y value for solo
    y_solo = np.array([solo_log_max_varnames[max_varname_template.format(data_size=data_size)] for data_size in x])
    y_interference1 = np.array([interference1_log_max_varnames[max_varname_template.format(data_size=data_size)] for data_size in x])

    # Make predictions
    b_solo = estimate_coefficients(x=x, y=y_solo)
    b_interference1_1 = estimate_coefficients(x=x[:break_point], y=y_interference1[:break_point])
    b_interference1_2 = estimate_coefficients(x=x[break_point:], y=y_interference1[break_point:])

    # Predicted response vector     
    y_pred_solo = b_solo[0] + b_solo[1]*x 
    y_pred_interference1_1 = b_interference1_1[0] + b_interference1_1[1]*x[:break_point]
    y_pred_interference1_2 = b_interference1_2[0] + b_interference1_2[1]*x[break_point:] 

    # Plotting the regression line 
    plt.title('Worst case execution time for solo and one interference with respect to prefetched data size (in nanoseconds) (regressed)')
    plt.xticks([*range(0, max_data_size + 1, 20)])
    plt.plot(x, y_pred_solo, label='No interference')
    plt.plot(x[:break_point], y_pred_interference1_1, label='1 interference', color='orange')
    plt.plot(x[break_point:], y_pred_interference1_2, color='orange')
    
    # Add equations on plots
    plt.text(190, 100000, 'y={:d}x + {:d}'.format(int(b_solo[1]), int(b_solo[0])), color=u'#1f77b4', fontsize=14)
    plt.text(75, 150000, 'y={:d}x + {:d}'.format(int(b_interference1_1[1]), int(b_interference1_1[0])), color='orange', fontsize=14)
    plt.text(405, 315000, 'y={:d}x + {:d}'.format(int(b_interference1_2[1]), int(b_interference1_2[0])), color='orange', fontsize=14)
    plt.xlabel('Prefetched data size')
    plt.ylabel('Execution time')
    plt.legend()
    
    return (y_pred_solo, y_pred_interference1_1, y_pred_interference1_2)


def generate_solo_interference_regressed_ratio(y_pred: tuple[float]) -> None:
    # Generate x 
    x = [*range(min_data_size, max_data_size + 1, data_size_increment)]
    
    # For all sizes get the y value
    y_solo = y_pred[0]
    y_interference1_1 = y_pred[1]
    y_interference1_2 = y_pred[2]
    y_ratio = [y_interference1_1[i] / y_solo[i] for i in range(0, break_point)]
    y_ratio += [y_interference1_2[i - break_point] / y_solo[i] for i in range(break_point, break_point + len(y_interference1_2))]
    
    # Set plot title
    plt.title('Ratio between worst case execution time of one interference and solo (regressed)')
    plt.xticks([*range(0, max_data_size + 1, 20)])
    plt.xlabel('Prefetched data size')
    plt.ylim(2.1, 3.8)
    plt.plot(x, y_ratio)


def generate_solo_interference_regressed_difference(y_pred: tuple[float]) -> None:
    # Generate x 
    x = [*range(min_data_size, max_data_size + 1, data_size_increment)]
    
    # For all sizes get the y value
    y_solo = y_pred[0]
    y_interference1_1 = y_pred[1]
    y_interference1_2 = y_pred[2]
    y_ratio = [(y_interference1_1[i] - y_solo[i]) / 1000 for i in range(0, break_point)]
    y_ratio += [(y_interference1_2[i - break_point] - y_solo[i]) / 1000 for i in range(break_point, break_point + len(y_interference1_2))]
    
    # Set plot title
    plt.title('Difference between worst case execution time of one interference and solo (in microseconds) (regressed)')
    plt.xticks([*range(0, max_data_size + 1, 20)])
    plt.plot(x, y_ratio)
    plt.xlabel('Prefetched data size')


def main():
    # Big files so modules will crash... Only get few variables
    solo_log_max_varnames = get_variables_from_big_file('max_', '../extract/bench_solo_legacy-execution-solo-24-06-03-2.py')
    interference1_log_max_varnames = get_variables_from_big_file('max_', '../extract/bench_interference1_legacy-execution-interference1-24-06-05-1.py')
    
    # Plot curves with solo and interference 
    plt.figure('Solo and interference', figsize=(16, 10))
    generate_solo_interference_curve(solo_log_max_varnames=solo_log_max_varnames,
                                     interference1_log_max_varnames=interference1_log_max_varnames)
    plt.savefig('../graphs/wcet_solo_interference.png')
    
    #Plot ratio between solo and interference 
    plt.figure('Solo and interference ratio', figsize=(16, 10))
    generate_solo_interference_ratio(solo_log_max_varnames=solo_log_max_varnames,
                                     interference1_log_max_varnames=interference1_log_max_varnames)
    plt.savefig('../graphs/wcet_solo_interference_ratio.png')
    
    plt.figure('Solo and interference difference', figsize=(16, 10))
    generate_solo_interference_difference(solo_log_max_varnames=solo_log_max_varnames,
                                          interference1_log_max_varnames=interference1_log_max_varnames)
    plt.savefig('../graphs/wcet_solo_interference_difference.png')
    
    plt.figure('Solo and interference regression', figsize=(16, 10))
    y_pred = generate_solo_interference_regressed_curve(solo_log_max_varnames=solo_log_max_varnames,
                                                        interference1_log_max_varnames=interference1_log_max_varnames)
    plt.savefig('../graphs/wcet_solo_interference_regression.png')
    
    plt.figure('Solo and interference regressed ratio', figsize=(16, 10))
    generate_solo_interference_regressed_ratio(y_pred=y_pred)
    plt.savefig('../graphs/wcet_solo_interference_regressed_ratio.png')
    
    plt.figure('Solo and interference regressed difference', figsize=(16, 10))
    generate_solo_interference_regressed_difference(y_pred=y_pred)
    plt.savefig('../graphs/wcet_solo_interference_regressed_difference.png')
    
    
        
if __name__ == '__main__':
    main()