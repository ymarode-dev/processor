# hub_logging.py
import os
import yaml
import logging
import logging.config
import time

def init_logging(env_key='LOG_CFG'):
    """
    Setup logging configuration from YAML file.
    Priority:
    1. Environment variable (LOG_CFG)
    2. Default path 'Core/logging/logging.yaml'
    """
    path = os.path.join('logger', 'logging.yaml')
    custom_path = os.getenv(env_key, None)

    if custom_path:
        path = custom_path

    if os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                
                config = yaml.safe_load(f.read())
                # 🔧 Ensure log directories exist
                for handler in config.get('handlers', {}).values():
                    if 'filename' in handler:
                        log_file = handler['filename']
                        os.makedirs(os.path.dirname(log_file), exist_ok=True)

                # Apply config
                logging.config.dictConfig(config)

                # Use UTC time for log timestamps
                logging.Formatter.converter = time.gmtime

            except Exception as e:
                print(f"Failed to load logging config: {e}")
                print("Using default logging settings.")
                logging.basicConfig(level=logging.DEBUG)
    else:
        print(f"Logging config file not found at: {path}")
        print("Using default logging settings.")
        logging.basicConfig(level=logging.DEBUG)

    logger = logging.getLogger("TestLogger")
    logger.info("Inside info log...")
    logger.debug("Inside debug log...")
    logger.error("Inside error log...")
    logger.warn("Inside warn log...")
    logger.log(9, "Inside trace log...")
    logger.log(15, "Inside response log...")
    logger.log(14, "Inside pc log...")
    logger.log(24, "Inside dbtrace log...")
    logger.log(26, "Inside schedule log...")
    logger.log(27, "Inside pytest log...")
    logger.log(28, "Inside aqi log...")