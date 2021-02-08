"""
The chapter of a manga.
"""

from pydlr import PyDlr
from page import Page


class Chapter:
    """
    A chapter of a manga.

    Attributes:
        url (str): The URL of the chapter.
        title (str): The title of the chapter.
        pages (:obj:`list` of :obj:`Page`): The list of pages of the chapter.
        isComplete (bool): Whether or not all pages of the chapter have been downloaded.
    """

    ##################################################
    # INITIALIZATION
    ##################################################

    def __init__(self, url, num, title=None, pages=None, isComplete=False):
        self.url = url
        self.num = num
        self.title = title
        self.pages = pages if pages is not None else []
        self.isComplete = isComplete

    ##################################################
    # SETTERS
    ##################################################

    def setTitle(self, title):
        """
        Set the title of the chapter.

        Parameters:
            title (str): The new title.
        """
        self.title = title

    def setPages(self, pages):
        """
        Set the pages of the chapter.

        Parameters:
            pages (:obj:`list` of :obj:`Page`): The new list of pages.
        """
        self.pages = pages

    def setSoup(self, soup):
        """
        Set the title and pages of the chapter based on the HTML soup.

        Parameters:
            soup (:obj:`BeautifulSoup`): The HTML data in BeautifulSoup form.
        """
        # TODO
        src = 'http:' + soup.find(id='comic').find_all('img')[0].attrs['src']
        pages = []
        for i in range(10):
            pages.append(Page(src, i))

        self.setTitle(soup.title.name)
        self.setPages(pages)

    ##################################################
    # REPRESENTATION
    ##################################################

    def __str__(self):
        result = f'   {self.url}'
        for page in self.pages:
            result += f'\n{page}'
        return result

    def toItem(self):
        """
        Create a PyDlr.Item object based on this chapter.

        Returns:
            :obj:`PyDlr.Item`: The PyDlr.Item object.
        """
        item = PyDlr.Item(self.url, {'chapter': self})
        return item
