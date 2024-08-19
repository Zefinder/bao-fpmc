# Imports
import os
import importlib
from typing import Any
from types import ModuleType

# Constants
generators_directory = './results/generator/'
generators_module = 'results.generator.'


def main():
    # Scan all files in generator directory that are _generator.py
    list_files = [f for f in os.listdir(generators_directory) if os.path.isfile(os.path.join(generators_directory, f)) and f.endswith('_generator.py')]

    # For each generator, import the module and generate using the generate() function
    for file in list_files:
        generator = importlib.import_module(generators_module + file[:-3])
        generator.generate()


if __name__ == '__main__':
    main()
