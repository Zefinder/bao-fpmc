# Imports
import os

# Constants
python_extracts = os.path.join(os.getcwd(), 'extract')
benchmarks_start_string = '# Benchmark start'
benchmarks_end_string = '# Benchmark end'

def extract(log_to_extract: list[str]) -> None:
    for log_file in log_to_extract:
        print('Extracting', log_file, '...')
        
        # Open file
        file = open(log_file, 'r')
        extract_file = open(os.path.join(python_extracts, log_file[:-3] + 'py'), 'w')
        
        # Extracts until the benchmark's end string or 'Tests finished!' (backward compatibility)
        line = file.readline()
        write_enabled = False
        while benchmarks_end_string not in line and 'Tests finished!' not in line:
            # If end of file, break
            if len(line) == 0:
                break
            
            # If yet not write and either benchmark start or array declaration (backward compatibility), we can write
            if not write_enabled and (benchmarks_start_string in line or 'elapsed_time_array' in line) :
                write_enabled = True
            
            if write_enabled:
                extract_file.write(line)
    
            line = file.readline()
        
        # Add float mean computation if write enabled
        if write_enabled:
            extract_file.write('average = sum(elapsed_time_array) / len(elapsed_time_array)\n')
            
        # Close files 
        file.close()
        extract_file.close()
        

def main() -> None:
    # Get log files name
    log_files = [file for file in os.listdir(os.getcwd()) if os.path.isfile(os.path.join(os.getcwd(), file)) and file.endswith('.log')]
    
    # Create directory if do not exist
    if not os.path.exists(python_extracts):
        os.mkdir(python_extracts)
    
    # Get only that are not extracted
    log_to_extract = [file for file in log_files if not os.path.exists(os.path.join(python_extracts, file[:-3] + 'py'))]

    # For those who do not exist extract
    extract(log_to_extract)


if __name__ == '__main__':
    main()