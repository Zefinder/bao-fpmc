from typing import Any
from types import ModuleType

# Names template to generate templates
elapsed_time_array_varname_template_generator = 'elapsed_time_array_{template:s}'
min_varname_template_generator = 'min_{template:s}'
max_varname_template_generator = 'max_{template:s}'

elapsed_time_array_ns_varname_template_generator = 'elapsed_time_array_{template:s}_ns'
min_ns_varname_template_generator = 'min_{template:s}_ns'
max_ns_varname_template_generator = 'max_{template:s}_ns'


def get_module_variables(module: ModuleType) -> dict[str, Any]:
    variables = {}
    if module:
        variables = {key: value for key, value in vars(module).items() if not (key.startswith('__') or key.startswith('_'))}
    return variables


# For now only non multiline variables
def get_variables_from_big_file(variable_filter: str, path_to_file: str) -> dict[str, Any]:
    variables = {}
    
    # The file is big and is probably not ok for import, careful Spongebob
    with open(path_to_file, 'r') as file: 
        line = 'a' # Just an init value
        while len(line) != 0:
            line = file.readline()
            if variable_filter in line:
                line_split = line.split('=')
                
                variable_name = line_split[0].strip()
                # Value can have a comment (max_value = 1 #us for example)
                variable_value = line_split[1].split('#')[0].strip()
                if variable_value.isdigit():
                    variable_value = int(variable_value)
                
                variables[variable_name] = variable_value
    
    return variables