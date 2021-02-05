class Chapter:
    """
    A chapter of a manga.

    Attributes:
        url (str): The URL of the chapter.
        title (str): The title of the chapter.
        pages (:obj:`list` of :obj:`Page`): The list of pages of the chapter.
        isComplete (bool): Whether or not all pages of the chapter have been downloaded.
    """

    def __init__(self, url, title=None):
        self.url = url
        self.title = title
        self.pages = []
        self.isComplete = False
