import yaml
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
CONFIGS_YAML_PATH =  os.path.join(current_dir, "configs.yaml")  # configs yaml path

class ConfigLoader:
    """
    A class to load and manage configuration settings from a YAML file.
    
    Attributes:
        configs (dict): A dictionary containing the configuration settings loaded from the YAML file.

    Methods:
        get(key, default=None):
            Returns the value for the given key from the configuration settings. 
            If the key is not found, returns the specified default value.
        
        __getitem__(key):
            Allows access to configuration settings using bracket notation (e.g., config[key]).
        
        __repr__():
            Returns a string representation of the ConfigLoader instance, which includes the configuration settings.
    """
    def __init__(self, yaml_file_path=CONFIGS_YAML_PATH):
        """
        Initializes the ConfigLoader by loading the configuration settings from the specified YAML file.

        Args:
            yaml_file_path (str): The path to the YAML configuration file.
        
        Raises:
            FileNotFoundError: If the specified YAML file does not exist.
        """
        self.configs = self.load_config(yaml_file_path)

    def load_config(self, yaml_file_path):
        """
        Loads configuration settings from the specified YAML file.

        Args:
            yaml_file_path (str): The path to the YAML configuration file.

        Returns:
            dict: A dictionary containing the configuration settings.

        Raises:
            FileNotFoundError: If the specified YAML file does not exist.
        """
        if not os.path.exists(yaml_file_path):
            raise FileNotFoundError(f"The file {yaml_file_path} does not exist.")
        with open(yaml_file_path, 'r') as file:
            return yaml.safe_load(file)

    def get(self, key, default=None):
        """
        Retrieves the value associated with the specified key from the configuration settings.

        Args:
            key (str): The key for which to retrieve the value.
            default (optional): The value to return if the key is not found. Defaults to None.

        Returns:
            The value associated with the specified key, or the default value if the key is not found.
        """
        return self.configs.get(key, default)

    def __getitem__(self, key):
        """
        Allows access to the configuration settings using bracket notation (e.g., config[key]).

        Args:
            key (str): The key for which to retrieve the value.

        Returns:
            The value associated with the specified key.

        Raises:
            KeyError: If the key is not found in the configuration settings.
        """
        return self.configs.get(key)

    def __repr__(self):
        """
        Returns a string representation of the ConfigLoader instance, which includes the configuration settings.

        Returns:
            str: A string representation of the ConfigLoader instance.
        """
        return repr(self.configs)