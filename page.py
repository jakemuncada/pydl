"""
The page of a manga.
"""


from pydlr import PyDlr


class Page:
    """
    A page of a manga.

    Attributes:
        url (str): The URL of the chapter.
        num (int): The page number.
        isDownloaded (bool): Whether or not the page has been downloaded.
    """

    def __init__(self, url, num):
        self.url = url
        self.num = num
        self.isDownloaded = False

    ##################################################
    # REPRESENTATION
    ##################################################

    def __str__(self):
        doneStr = 'DONE' if self.isDownloaded else 'NOT DONE'
        return f'      {self.num}: {self.url} ({doneStr})'

    def toItem(self):
        """
        Create a PyDlr.Item object based on this page.

        Returns:
            :obj:`PyDlr.Item`: The PyDlr.Item object.
        """
        item = PyDlr.Item(self.url, {'page': self})
        return item
