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
