import os
import sys
import logging
import requests
from bs4 import BeautifulSoup


from settings import Settings
from log import LogSettings

# Logger
logger = logging.getLogger(__name__)


def main():
    """
    The main function.
    """

    # Initialize the logger
    LogSettings.init()

    # Deactivate the proxy if using localhost (for testing)
    os.environ['NO_PROXY'] = '127.0.0.1'

    try:
        settings = Settings(sys.argv[1:])
        logger.info(f'Starting task for {settings.mainUrl}...')
    except Exception as e:
        logger.error(f'{str(e)}\nUse -h or --help to display usage documentation.')
        logger.exception(e)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(f'An unexpected error occurred. {str(e)}')
        logger.exception(e)
    finally:
        LogSettings.close()
