import sys
import logging

from log import LogSettings

# Logger
logger = logging.getLogger(__name__)


class Settings:
    """
    The settings for the script. Can be set using command line arguments.

    Parameters:
        args (:obj:`list` of :obj:`str`): The command line arguments.

    Attributes:
        mainUrl (str): The main URL.
        producerCount (int): The number of producer threads. Producer threads load the page HTML and add the 
            image URLs to the download list.
        downloaderCount (int): The number of downloader threads. Downloader threads get a URL from the download list,
            downloads it, and saves it to storage.
        isVerbose (bool): If true, verbose mode is enabled, meaning that DEBUG level messages will also be displayed
            on the console. If false, only INFO and above messages will be displayed on the console.
    """

    def __init__(self, args):

        logger.debug(f'Initializing settings with command line arguments: {" ".join(args)}')

        # Default Values
        self.mainUrl = None
        self.producerCount = '1'
        self.downloaderCount = '3'
        self.isVerbose = False

        # If -h or --help is included in the arguments, display the usage documentation
        # and exit the script.
        if '-h' in args or '--help' in args:
            Settings.help()
            sys.exit()

        if len(args) < 1:
            raise AttributeError('URL not found.')

        self.mainUrl = args[0]

        idx = 1
        while idx < len(args):
            arg = args[idx]

            if arg == '-h' or arg == '--help':
                self.isHelp = True
                break

            elif arg == '-p' or arg == '--producer':
                val = args[idx + 1] if idx + 1 else None
                self.producerCount = val
                idx += 2

            elif arg == '-d' or arg == '--downloader':
                val = args[idx + 1] if idx + 1 else None
                self.downloaderCount = val
                idx += 2

            elif arg == '-v' or arg == '--verbose':
                self.isVerbose = True
                LogSettings.enableVerbose()
                idx += 1

            else:
                raise AttributeError(f'The argument "{arg}" is not a valid setting.')

        self._validate()

        # TODO: Print the values of the Settings

    def _validate(self):
        """
        Try to convert each setting to its type while checking its validity.
        Raises an error if the setting is invalid.
        """

        # Main URL
        if self.mainUrl is None:
            raise AttributeError('URL not found.')

        # Producer Count
        if not self.producerCount.isnumeric():
            raise TypeError('Producer count must be a positive integer from 1 to 5 (inclusive).')
        else:
            self.producerCount = int(self.producerCount)
            if self.producerCount < 1 or self.producerCount > 5:
                raise ValueError(
                    'Producer count must be a positive integer from 1 to 5 (inclusive).')

        # Downloader Count
        if not self.downloaderCount.isnumeric():
            raise TypeError(
                'Producer count must be a positive integer from 1 to 12 (inclusive).')
        else:
            self.downloaderCount = int(self.downloaderCount)
            if self.downloaderCount < 1 or self.downloaderCount > 12:
                raise ValueError(
                    'Downloader count must be a positive integer from 1 to 12 (inclusive).')

    @staticmethod
    def help():
        """
        Print the help documentation.
        """

        s = []
        s.append('')
        s.append('Description: pydl is a python script that crawls a manhwa and downloads')
        s.append('             its chapters to read offline.')
        s.append('')
        s.append('Author: Jake Randolph Muncada')
        s.append('')
        s.append('USAGE: python3 pydl.py <url> [args]')
        s.append('where <url> is the URL of the page to crawl. *Required')
        s.append('')
        s.append('Args:')
        s.append('   -d|--downloader <number>   Sets the number of downloader threads. This is the number of')
        s.append('                              concurrent downloads. Must be a positive integer from 1 to 12.')
        s.append('                              Defaults to 3 if not set.')
        s.append('   -p|--producer <number>     Sets the number of producer threads. Producer threads load the')
        s.append('                              chapter HTML and adds the image URLs to the download list.')
        s.append('                              Must be a positive integer from 1 to 5. Defaults to 1 if not set.')
        s.append('   -v|--verbose               Turn on verbose mode, which allows debug log messages')
        s.append('                              to be displayed on the console.')

        logger.debug('Display help documentation.')
        print('\n'.join(s))
