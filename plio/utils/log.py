import os
import json
import logging.config

from ..examples import get_path


def setup_logging(path=get_path('logging.json'),
                  level='INFO',
                  env_key='LOG_CFG'):
    """
    Read a log configuration file, written in JSON

    Parameters
    ----------
    path : string
                   The path to the logging configuration file
    level : object
                    The logger level at which to report
    env_key : str
              A potential environment variable where the user defaults logs
    """
    value = os.getenv(env_key, None)
    if value:
        path = value

    print(level)
    level = getattr(logging, level.upper())
    print(level)
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
        logging.basicConfig(level=level)
        logger = logging.getLogger()
        logger.setLevel(level)