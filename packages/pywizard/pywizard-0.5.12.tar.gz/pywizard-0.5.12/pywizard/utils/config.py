import os
import sys


def read_yaml_cofig(yaml_file):
    import yaml

    path = os.path.abspath(yaml_file)
    if not os.path.exists(path):
        sys.stderr.write("\nConfig file do not exist: %s\n" % path)
        exit(1)
    with open(path, 'r') as f:
        config = yaml.load(f)
    return config
