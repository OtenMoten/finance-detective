import yaml
from typing import Dict, Any
import logging
import codecs


def load_config(file_path: str) -> Dict[str, Any]:
    """
    Load and validate the configuration from a YAML file.

    Args:
        file_path (str): Path to the YAML configuration file.

    Returns:
        Dict[str, Any]: Validated configuration dictionary.

    Raises:
        ValueError: If the configuration is invalid or missing required keys.
        yaml.YAMLError: If there's an error parsing the YAML file.
    """
    encodings = ['utf-8', 'iso-8859-1', 'windows-1252']

    for encoding in encodings:
        try:
            with codecs.open(file_path, 'r', encoding=encoding) as file:
                config = yaml.safe_load(file)

            validate_config(config)
            logging.info(f"Configuration file successfully loaded with {encoding} encoding.")
            return config
        except UnicodeDecodeError:
            logging.warning(f"Failed to decode config file with {encoding} encoding. Trying next encoding...")
        except yaml.YAMLError as e:
            logging.error(f"Error parsing YAML file: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error reading config file: {e}")
            raise

    logging.error("Failed to read the config file with all attempted encodings.")
    raise ValueError("Unable to read the config file with any of the attempted encodings.")


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate the configuration dictionary.

    Args:
        config (Dict[str, Any]): Configuration dictionary to validate.

    Raises:
        ValueError: If the configuration is invalid or missing required keys.
    """
    required_keys = ['stocks', 'start_date', 'end_date', 'report_format']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")

    if not isinstance(config['stocks'], list) or len(config['stocks']) == 0:
        raise ValueError("'stocks' must be a non-empty list")

    if config['report_format'] not in ['pdf', 'txt']:
        raise ValueError("'report_format' must be either 'pdf' or 'txt'")
