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
