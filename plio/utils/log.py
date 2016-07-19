import os
import json
import logging.config

def setup_logging(default_path='logging.json',
                  default_level='INFO',
                  env_key='LOG_CFG'):
    """
    Read a log configuration file, written in JSON

    Parameters
    ----------
    default_path : string
                   The path to the logging configuration file
    default_level : object
                    The logger level at which to report
    env_key : str
              A potential environment variable where the user defaults logs
    """

    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value

    default_level = getattr(logging, default_level.upper())
    if os.path.exists(path):
        logtype = os.path.splitext(os.path.basename(path))[1]
        with open(path, 'rt') as f:
            if logtype == '.json':
                config = json.load(f)
            elif logtype == '.yaml':
                import yaml
                config = yaml.load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
        logger = logging.getLogger()
        logger.setLevel(default_level)