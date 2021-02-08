"""
Provides high-level support for sending several HTTP requests.
"""

from queue import Queue
import time
import logging
import threading
import requests


logger = logging.getLogger(__name__)


class PyDlr:
    """
    Python Downloader.

    Attributes:
        items (Queue of dict): The queue of items to be downloaded.
        callback (function): The default callback function that runs
            when a request has been concluded.

    Parameters:
        items (Queue of dict): The queue of items to be downloaded.
        numThreads (int): The number of downloader threads to run.
        callback (function): The default callback function that runs
            when a request has been concluded.
    """

    ##################################################
    # ITEM KEYS
    ##################################################

    ITEM_URL = 'url'
    """The URL attribute key."""

    ITEM_CALLBACK = 'callback'
    """The callback attribute key."""

    ##################################################
    # INITIALIZATION
    ##################################################

    def __init__(self, items=None, numThreads=1, callback=None):
        self.items = Queue()
        items = items if items is not None else []
        for item in items:
            self.items.put(item)
        self.callback = callback

        self._threads = []
        # If set, the threads will terminate as soon as possible
        self._killEvent = threading.Event()
        # If set, the threads will terminate once the queue is empty
        self._endEvent = threading.Event()

        for idx in range(1, numThreads + 1):
            t = PyDlrThread(f'Thread{idx}', self.items, self.callback,
                            self._killEvent, self._endEvent)
            self._threads.append(t)

        # Logging...
        debugStr = f'Initialized PyDlr with {len(items)} items and {numThreads} threads'
        debugStr += ' and no default callback.' if callback is None else '.'
        logger.debug(debugStr)

    ##################################################
    # SETTERS
    ##################################################

    def addItems(self, items):
        """
        Add items to the download list.

        Note:
            Each item in the list should contain an attribute called `url`.
            An item could also optionally contain an attribute called `callback`,
            which runs when the download request has concluded.

        Parameters:
            items (list of dict): The list of items to add to the download list.
        """
        for item in items:
            self.items.put(item)

    def setCallback(self, callback):
        """
        Set the default callback that runs when a download request has been concluded.
        The callback function takes one parameter, which is a `PyDlrResult` object.

        Parameters:
            callback (function): The new default callback.
        """
        self.callback = callback

    ##################################################
    # CONTROLS
    ##################################################

    def start(self):
        """
        Start all the threads.
        """
        logger.info('Starting downloads with %d threads.', len(self._threads))
        for t in self._threads:
            t.start()

    def kill(self):
        """
        Stop all threads by setting/activating the kill event.
        """
        logger.info('Stopping downloads... Waiting for active downloads to finish...')
        self._killEvent.set()
        for t in self._threads:
            t.join()

    def join(self):
        """
        Wait for all downloads to be finished.
        """
        self._endEvent.set()

        while not self.items.empty():
            time.sleep(0.300)

        for t in self._threads:
            t.join()


##################################################
# PyDlrThread
##################################################

class PyDlrThread(threading.Thread):
    """
    A custom Thread for PyDlr.

    Parameters:
        name (str): The name of the thread.
        queue (Queue): The download queue.
        callback (function): The default callback function that runs when a request
            has been concluded.
        killEvent (threading.Event): An event signifying that the thread should terminate
            as soon as possible.
        endEvent (threading.Event): An event signifying that the thread should terminate
            once the queue is empty.
    """

    def __init__(self, name, queue, callback, killEvent, endEvent):
        threading.Thread.__init__(self)
        self.name = name
        self.queue = queue
        self.callback = callback
        self.killEvent = killEvent
        self.endEvent = endEvent

    def run(self):
        while not self.killEvent.is_set():
            if not self.queue.empty():
                item = self.queue.get()
                self.processItem(item)
                self.queue.task_done()
            elif self.endEvent.is_set():
                break

    def processItem(self, item):
        """
        Download the item and pass the result to the callback.

        Parameters:
            item (dict): The item to be processed.
        """

        url = item.get(PyDlr.ITEM_URL, None)
        if url is None:
            logger.error('Error: item URL not found.')
            return

        logger.debug('Downloading %s...', url)

        response = None
        result = None
        failureReason = None

        try:
            # Fetch the data.
            response = requests.get(url)
            # Raise exception if any.
            response.raise_for_status()
            # If there were no exceptions, the download was successful.
            logger.debug('Successfully downloaded %s.', url)
            # Create successful result.
            result = PyDlrResult.successfulResult(item, response)
        except requests.exceptions.HTTPError as err:
            failureReason = 'An HTTP error occurred.'
        except requests.exceptions.ProxyError as err:
            failureReason = 'A proxy error occurred.'
        except requests.exceptions.SSLError as err:
            failureReason = 'An SSL error occurred.'
        except requests.exceptions.ConnectTimeout as err:
            failureReason = 'The request timed out while trying to connect to the remote server.'
        except requests.exceptions.ReadTimeout as err:
            failureReason = 'The server did not send any data in the allotted amount of time.'
        except requests.exceptions.Timeout as err:
            failureReason = 'The request timed out.'
        except requests.exceptions.ConnectionError as err:
            failureReason = 'A Connection error occurred.'
        except requests.exceptions.URLRequired as err:
            failureReason = 'A valid URL is required to make a request.'
        except requests.exceptions.TooManyRedirects as err:
            failureReason = 'Too many redirects.'
        except requests.exceptions.MissingSchema as err:
            failureReason = 'The URL schema (e.g. http or https) is missing.'
        except requests.exceptions.InvalidSchema as err:
            failureReason = 'The URL schema is invalid.'
        except requests.exceptions.InvalidHeader as err:
            failureReason = 'The header value provided was somehow invalid.'
        except requests.exceptions.InvalidProxyURL as err:
            failureReason = 'The proxy URL provided is invalid.'
        except requests.exceptions.InvalidURL as err:
            failureReason = 'The URL provided was somehow invalid.'
        except Exception as err:  # pylint: disable=broad-except
            failureReason = 'An error occurred.'
            logger.exception(err)

        if result is None:
            logger.error('Failed to download %s... %s', url, failureReason)
            result = PyDlrResult.failedResult(item, response, failureReason)

        # Execute the callback
        callback = self.getCallback(item)
        if callback is not None:
            callback(result)
        else:
            logger.warning('There is no callback for %s', url)

    def getCallback(self, item):
        """
        Returns the callback for the item.
        If the item has an attribute called `callback`, it will be returned.
        Otherwise, the default callback will be returned.

        Parameters:
            item (dict): The item to be processed.

        Returns:
            function: The callback.
        """
        # The callback will either be the specific callback of the item
        callback = item.get(PyDlr.ITEM_CALLBACK, None)
        if callback is None:
            # Or the default success callback
            callback = self.callback
        return callback


##################################################
# PyDlrResult
##################################################

class PyDlrResult:
    """
    The result of the download request.

    Note:
        Use the class methods `successfulResult` and `failedResult` to initialize a new PyDlrResult.

    Properties:
        url (str): The URL of the item.
        item (dict): The item that was requested.
        response (obj): The requests library response. Can be None.
        isSuccess (bool): True if the result was a success. False if it was a failure.
        failureReason (str): The reason for the failure. None if the result was a success.
    """

    @classmethod
    def successfulResult(cls, item, response):
        """
        Instantiate a successful result.

        Parameters:
            item (dict): The item that was requested.
            response (obj): The requests library response. Can be None.
        """
        return cls(True, item, response)

    @classmethod
    def failedResult(cls, item, response, failureReason):
        """
        Instantiate a failed result.

        Parameters:
            item (dict): The item that was requested.
            response (obj): The requests library response. Can be None.
            failureReason (str): The reason for the failure.
        """
        return cls(False, item, response, failureReason)

    def __init__(self, isSuccess, item, response, failureReason=None):
        self.url = item[PyDlr.ITEM_URL]
        self.item = item
        self.response = response
        self.isSuccess = isSuccess
        self.failureReason = failureReason

    def getBytes(self):
        """
        Returns the response content in bytes.
        """
        if self.response is None:
            return None
        return self.response.content

    def getText(self, encoding=None):
        """
        Returns the response content as plain text.

        Parameters:
            encoding (str, optional): The encoding of the plain text.
                If set to None, the encoding is inferred internally.
        """
        if self.response is None:
            return None

        if encoding is not None:
            self.response.encoding = encoding
        return self.response.text

    def getJson(self):
        """
        Parses the response content as JSON and returns a dictionary.
        """
        if self.response is None:
            return None
        return self.response.json()
