class Manga:
    """
    A manga.

    Attributes:
        url (str): The URL of the manga.
        title (str): The title of the manga.
        chapters (:obj:`list` of :obj:`Chapter`): The list of chapters of a manga.
        isComplete (bool): Whether or not all pages of the manga have been downloaded.
    """

    def __init__(self, url, title=None):
        self.url = url
        self.title = title
        self.chapters = []
        self.isComplete = False