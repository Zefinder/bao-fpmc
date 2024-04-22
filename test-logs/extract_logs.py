# Imports
import os

# Constants
python_extracts = os.path.join(os.getcwd(), 'extract')


def extract(log_to_extract: list[str]) -> None:
    for log_file in log_to_extract:        
        # Open file
        file = open(log_file, 'r')
        extract_file = open(os.path.join(python_extracts, log_file[:-3] + 'py'), 'w')
        
        # Read line and write if begins with elapsed_time_array until 'Tests finished!'
        line = file.readline()
        write_enabled = False
        while 'Tests finished!' not in line:
            if not write_enabled and line.startswith('elapsed_time_array = ['):
                write_enabled = True
            
            if write_enabled:
                extract_file.write(line)
    
            line = file.readline()
        
        # Add float mean computation
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