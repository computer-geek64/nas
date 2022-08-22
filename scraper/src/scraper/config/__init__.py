# __init__.py
import os
import yaml


YAML_EXTENSIONS = {'.yml', '.yaml'}


config = {}

for root, directories, filenames in os.walk(os.path.dirname(os.path.abspath(__file__))):
    for filename in filenames:
        if os.path.splitext(filename)[1] in YAML_EXTENSIONS:
            with open(os.path.join(root, filename), 'r') as yaml_file:
                config.update(yaml.safe_load(yaml_file))
