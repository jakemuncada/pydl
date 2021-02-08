"""
Main entry for the download script.
"""

import os
import sys
import logging

from settings import Settings
from log import LogSettings
from manga import Manga

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

    # Get the settings from command line arguments
    try:
        settings = Settings(sys.argv[1:])
    except (ValueError, TypeError, AttributeError) as err:
        logger.error('%s\nUse -h or --help to display usage documentation.', err)
        logger.exception(err)
        sys.exit(1)

    # Fetch and instantiate the manga
    try:
        manga = Manga.fromUrl(settings.mainUrl)
        manga.download(settings)
        print(manga)
    except Manga.MangaError as err:
        print('Failed to fetch manga. Program will now terminate.')
        logger.exception(err)
        sys.exit(1)

    logger.info('Starting task for %s...', settings.mainUrl)


if __name__ == '__main__':
    try:
        main()
    except Exception as err:  # pylint: disable=broad-except
        logger.error('An unexpected error occurred. %s', err)
        logger.exception(err)
    finally:
        LogSettings.close()
