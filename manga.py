"""
The model for a Manga.
"""

from queue import Queue
from bs4 import BeautifulSoup

from chapter import Chapter
from pydlr import PyDlr


class Manga:
    """
    A manga.

    Attributes:
        url (str): The URL of the manga.
        title (str): The title of the manga.
        chapters (:obj:`list` of :obj:`Chapter`): The list of chapters of a manga.
        isComplete (bool): Whether or not all pages of the manga have been downloaded.
    """

    ##################################################
    # INITIALIZATION
    ##################################################

    def __init__(self, url, title, chapters, isComplete=False):
        self.url = url
        self.title = title
        self.chapters = chapters
        self.isComplete = isComplete
        self._chapterDownloader = None
        self._pageDownloader = None

    ##################################################
    # DOWNLOAD
    ##################################################

    def download(self, settings):
        """
        Download the manga.
        """

        def chapterDownloaded(result):
            """
            The callback for when a chapter has been downloaded (either successfully or not).

            Parameters:
                result (:obj:`PyDlr.Result`): The result of the download request.
            """
            if result.isSuccess:
                num = result.item.payload['chapter'].num
                soup = BeautifulSoup(result.getText(), 'html.parser')
                chapter = self.chapters[num]
                chapter.setSoup(soup)
                self._pageDownloader.addItems([page.toItem() for page in chapter.pages])

        chapterItems = []
        for chapter in self.chapters:
            item = PyDlr.Item(chapter.url, {'chapter': chapter})
            chapterItems.append(item)

        self._chapterDownloader = PyDlr(chapterItems, 1, chapterDownloaded)
        self._pageDownloader = PyDlr()

        self._chapterDownloader.start()
        # self._pageDownloader.start()

        self._chapterDownloader.wait()

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def fromUrl(cls, url):
        """
        Intiantiate a Manga from a URL.

        Parameters:
            url (str): The URL of the manga.
        """

        # Fetch the page data
        response, failureReason = PyDlr.get(url)

        # Raise an exception if the fetch failed
        if failureReason is not None:
            raise Manga.MangaError(failureReason)

        # Parse the HTML into its soup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Get the title and the chapter URLs
        title = Manga.parseTitle(soup)
        chapters = Manga.parseChapters(soup)

        return cls(url, title, chapters)

    ##################################################
    # STATIC METHODS
    ##################################################

    @staticmethod
    def parseTitle(soup):
        """
        Parse the HTML soup and get the title.

        Parameters:
            soup (:obj:`BeautifulSoup`): The HTML data in BeautifulSoup form.

        Returns:
            str: The manga title.
        """
        # TODO
        return 'Sample Manga Title'

    @staticmethod
    def parseChapters(soup):
        """
        Parse the HTML and get the list of all chapters.

        Parameters:
            soup (:obj:`BeautifulSoup`): The HTML data in BeautifulSoup form.

        Returns:
            :obj:`list` of :obj:`Chapter`: The list of chapters in the manga.
        """
        # TODO
        chapters = []
        for idx in range(101, 126):
            url = f'https://xkcd.com/{idx}/'
            chapters.append(Chapter(url, idx - 101))
        return chapters

    ##################################################
    # REPRESENTATION
    ##################################################

    def __str__(self):
        result = f'{self.title}, {len(self.chapters)} chapters ({self.url})'
        for chapter in self.chapters:
            result += f'\n{str(chapter)}'
        return result

    ##################################################
    # MANGA ERROR
    ##################################################

    class MangaError(Exception):
        """
        Error related to Manga.
        """
