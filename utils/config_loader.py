import yaml
import os
import logging
import logging.config
import configparser

_DEFAULT_VACCINE_SCHEDULE_PATH = os.path.join('config', 'vaccine_schedule.yaml')
_DEFAULT_APP_CONFIG_PATH = 'appconfig.ini'


def load_vaccine_schedule(config_path: str = None) -> dict:
    """Load vaccine schedule and labels from a YAML config file.

    Args:
        config_path: Path to the YAML file. Defaults to config/vaccine_schedule.yaml
                     relative to the current working directory.

    Returns:
        Parsed YAML as a dict with 'vaccine_schedule' and 'labels' keys.

    Raises:
        FileNotFoundError: If the YAML file does not exist at the resolved path.
        yaml.YAMLError: If the file content is not valid YAML.
    """
    path = config_path if config_path is not None else _DEFAULT_VACCINE_SCHEDULE_PATH
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Vaccine schedule config not found: {os.path.abspath(path)}")
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_app_config(config_path: str = None) -> dict:
    """Load [app] section from an INI config file as a plain dict.

    Args:
        config_path: Path to the INI file. Defaults to appconfig.ini in the
                     current working directory.

    Returns:
        Dict of key/value pairs from the [app] section.

    Raises:
        RuntimeError: If the [app] section is missing from the config file.
    """
    path = config_path if config_path is not None else _DEFAULT_APP_CONFIG_PATH
    config = configparser.ConfigParser()
    config.read(path)
    if not config.has_section('app'):
        raise RuntimeError(
            f"Config file '{path}' is missing the [app] section"
        )
    return dict(config.items('app'))


def get_logger(log_file_path: str) -> logging.Logger:
    """Initialise and return the file_logger from a logging config file.

    Args:
        log_file_path: Path to the logging INI config file.

    Returns:
        The configured 'file_logger' Logger instance.
    """
    logging.config.fileConfig(log_file_path, disable_existing_loggers=False)
    return logging.getLogger("file_logger")
