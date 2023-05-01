class ShortLink:
    """
    Model class
    """

    def __init__(self, id: int, title: str, url: str, hash_str: str):
        self.id = id
        self.title = title
        self.url = url
        self.hash_str = hash_str

    def to_dict(self):
        result = self.__dict__
        # Remove "id" key from dict
        del result["id"]
        return result
