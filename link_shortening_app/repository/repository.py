from abc import ABC, abstractmethod
from typing import List, Union

from link_shortening_app.models import ShortLink


class ShortLinkRepoAbc(ABC):
    @abstractmethod
    def create(self, title: str, url: str, hash_str: str) -> Union[ShortLink, None]:
        raise NotImplementedError("Method not implemented!")

    @abstractmethod
    def update(self, short_link: ShortLink) -> ShortLink:
        raise NotImplementedError("Method not implemented!")

    @abstractmethod
    def delete(self, hash_str: str) -> Union[ShortLink, None]:
        raise NotImplementedError("Method not implemented!")

    @abstractmethod
    def get_by_hash(self, hash_str: str) -> Union[ShortLink, None]:
        raise NotImplementedError("Method not implemented!")

    @abstractmethod
    def get_all(self) -> List[ShortLink]:
        raise NotImplementedError("Method not implemented!")


class Repository:
    __slots__ = ["short_link"]

    def __init__(self, short_link: ShortLinkRepoAbc):
        self.short_link = short_link
