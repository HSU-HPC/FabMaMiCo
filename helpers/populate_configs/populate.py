"""Helper Script to generate couette.xml files from a jinja template and a configuration file.

This script reads a configuration file in yaml format and a jinja template file.
It generates all possible combinations of the configuration parameters and writes
the resulting files to the specified directory.

"""

import itertools
import os

import jinja2
import yaml


def generate_combinations(data):
    """
    Generate all possible combinations of the configuration parameters.
    
    Parameters
    ----------
    data : dict
        A dictionary containing the configuration parameters.
        
    Returns
    -------
    list
        A list containing all possible combinations of the configuration parameters.
    """
    for key in data.keys():
        if not isinstance(data[key], list):
            data[key] = [data[key]]
        keys, values = zip(*data.items())
    return [dict(zip(keys, v)) for v in itertools.product(*values)]


def write_file(content, dir, filename):
    """
    Write content to a file.
    If the directory does not exist, it will be created.
    
    Parameters
    ----------
    content : str
        The content to write to the file.
    dir : str
        The directory where the file will be saved.
    filename : str
        The name of the file.
        
    Returns
    -------
    None
    """
    os.makedirs(dir, exist_ok=True)
    filepath = os.path.join(dir, filename)
    with open(filepath, "w") as f:
        f.write(content)



if __name__ == "__main__":
    # Make changes to the following variables to suit your needs
    TEMPLATE_PATH = "/home/jo/repos/FabSim3/plugins/FabMaMiCo/helpers/populate_configs/jinja_templates/"
    TEMPLATE_NAME = "couette_A.xml.jinja"
    CONFIG_PATH = "/home/jo/repos/FabSim3/plugins/FabMaMiCo/helpers/populate_configs/configs/example_config3.yml"
    CONFIGS_TARGET_PATH = "/home/jo/repos/FabSim3/plugins/FabMaMiCo/config_files"
    CONFIG_NAME = "simE"
    OUTPUT_FILE = "couette.xml"

    # Setting up jinja environment
    jinja_loader = jinja2.FileSystemLoader(TEMPLATE_PATH)
    jinja_env = jinja2.Environment(loader=jinja_loader)

    # Load config file
    with open(CONFIG_PATH) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    # Generate all combinations of the configuration parameters
    combinations = generate_combinations(config)

    # Load jinja template
    template = jinja_env.get_template(TEMPLATE_NAME)
    
    if len(combinations) > 1:
        # Generate SWEEP files
        for i, combo in enumerate(combinations, 1):
            dir = os.path.join(CONFIGS_TARGET_PATH, CONFIG_NAME, "SWEEP", f"d{i}")
            write_file(
                content=template.render(combo),
                dir=dir,
                filename=OUTPUT_FILE
            )
    else:
        # Generate single file
        dir = os.path.join(CONFIGS_TARGET_PATH, CONFIG_NAME)
        write_file(
            content=template.render(combinations[0]),
            dir=dir,
            filename=OUTPUT_FILE
        )
