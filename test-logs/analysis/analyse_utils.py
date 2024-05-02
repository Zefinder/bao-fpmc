from typing import Any
from types import ModuleType

def get_module_variables(module: ModuleType) -> dict[str, Any]:
    variables = {}
    if module:
        variables = {key: value for key, value in vars(module).items() if not (key.startswith('__') or key.startswith('_'))}
    return variables
