import sys
from pathlib import Path

# Add the root directory to PYTHONPATH
sys.path.append(str(Path(__file__).resolve().parent.parent))

import os
import logging
import logging.handlers
from dotenv import load_dotenv

load_dotenv()

# Set up papertrail

papertrail_host = os.getenv('PAPERTRAIL_HOST')
papertrail_port = int(os.getenv('PAPERTRAIL_PORT'))


if papertrail_host and papertrail_port:
    # Set up logging
    papertrail_handler = logging.handlers.SysLogHandler(address=(papertrail_host,papertrail_port))
    console_handler = logging.StreamHandler()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[papertrail_handler, console_handler]
    )

else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        filename='applog.txt'       
    )

def get_logger(name=None):
    logger = logging.getLogger(name)
    return logger
