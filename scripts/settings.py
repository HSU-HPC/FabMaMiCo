import hashlib
import io
import os

import yaml

try:
    from fabsim.base.fab import *
except ImportError:
    from base.fab import *


class Settings():
    """
    MaMiCo settings class to store and manage the user settings.
    """
    def __init__(self, plugin_filepath: str, config: str):
        """
        Initialize the MaMiCo settings class.

        Returns:
            None
        """
        self.plugin_path: str = plugin_filepath
        self.config: str = config
        settings_filepath = os.path.join(env.job_config_path_local, 'settings.yml')
        if not os.path.isfile(settings_filepath):
            raise FileNotFoundError(f"Settings file '{settings_filepath}' not found.")
        with open(settings_filepath, 'r') as settings_file:
            try:
                self.settings: dict = yaml.safe_load(settings_file)
            except yaml.YAMLError as e:
                raise e

    def update(self, data: dict):
        """
        Update the settings with the given data.
        """
        self.settings.update(data)

    def get(self, key: str, default = None):
        """
        Get the value for the given key.

        Args:
            key (str): The key to get the value for.
            default: The default value to return if the key does not exist.
                (default is None)

        Returns:
            The value for the given key or the default value if the key does not exist.
        """
        return self.settings.get(key, default)

    def delete(self, key: str):
        """
        Delete the key from the settings.

        Args:
            key (str): The key to delete.
        """
        if key in self.settings:
            del self.settings[key]

    def determine_md5(self):
        """
        Determine the MD5 checksum of the settings.

        Returns:
            str: The MD5 checksum
        """
        string_stream = io.StringIO()
        yaml.dump(self.settings, string_stream, sort_keys=True, indent=2, line_break='\n')
        checksum = hashlib.md5(string_stream.getvalue().encode('utf-8')).hexdigest()
        os.makedirs(os.path.join(self.plugin_path, 'tmp', 'checksum_files'), exist_ok=True)
        with open(os.path.join(self.plugin_path, 'tmp', 'checksum_files', f'{checksum}.yml'), 'w') as f:
            f.write(string_stream.getvalue())
        rich_print(
            Panel(
                f"{checksum}",
                title=f"MD5 Checksum:",
                border_style="green",
                expand=False,
            )
        )
        return checksum

    def print(self):
        """
        Print the settings.
        """
        rich_print(
            Panel(
                yaml.dump(self.settings, sort_keys=True, indent=2, line_break='\n'),
                title=f"Settings:",
                border_style="blue",
                expand=False,
            )
        )
