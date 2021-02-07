import os
import sys
import logging
import requests
from bs4 import BeautifulSoup

from settings import Settings
from log import LogSettings
from pydlr import PyDlr

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
    except Exception as e:
        logger.error(f'{str(e)}\nUse -h or --help to display usage documentation.')
        logger.exception(e)
        sys.exit(1)

    logger.info(f'Starting task for {settings.mainUrl}...')


if __name__ == '__main__':
    # try:
    #     main()
    # except Exception as e:
    #     logger.error(f'An unexpected error occurred. {str(e)}')
    #     logger.exception(e)
    # finally:
    #     LogSettings.close()

    LogSettings.init()
    settings = Settings(sys.argv[1:])

    try:
        items = []
        for idx in range(1, 21):
            item = {'url': f'http://www.xkcd.com/{idx}'}
            items.append(item)

        def callback(result):
            # if result.isSuccess:
            #     print(f'Downloaded {len(result.getText())} bytes from {result.url}')
            # else:
            #     print(f'Failed to download {result.url}, {result.failureReason}')
            print(f'Executing {"success" if result.isSuccess else "failure"} callback for {result.url}.')

        pydlr = PyDlr(items, 3, callback)

        pydlr.start()
        pydlr.join()

    except (SystemExit, KeyboardInterrupt):
        pydlr.kill()
        logger.info('Program stopped.')
