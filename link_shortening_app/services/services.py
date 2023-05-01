from abc import ABC, abstractmethod
from typing import List, Union

from link_shortening_app.models import ShortLink


class ShortLinksServiceAbc(ABC):
    @abstractmethod
    def create_short_link(self, title: str, url: str) -> ShortLink:
        """
        Get new short link instance, generate new hash, save to repository and return instance of new short link
        :param url:
        :param title:
        :return: str
        """
        raise NotImplementedError("Method not implemented!")

    @abstractmethod
    def get_all_short_links(self) -> List[ShortLink]:
        """
        Get all url records
        :return: list[]
        """
        raise NotImplementedError("Method not implemented!")

    @abstractmethod
    def get_short_link_by_hash(self, hash_str: str) -> Union[ShortLink, None]:
        """
        Getting hash of record and return record
        :param hash_str:
        :return:
        """
        raise NotImplementedError("Method not implemented!")

    @abstractmethod
    def update_short_link(self, short_link: ShortLink) -> ShortLink:
        """
        Update info (title) of record (find by hash)
        :param short_link:
        :return: ShortLink
        """
        raise NotImplementedError("Method not implemented!")

    @abstractmethod
    def delete_short_link(self, hash_str: str) -> Union[ShortLink, None]:
        """
        Delete short link from app
        :param hash_str:
        :return: Deleted short link instance
        """
        raise NotImplementedError("Method not implemented!")


class Service:
    __slots__ = ["short_service"]

    def __init__(self, short_service: ShortLinksServiceAbc):
        self.short_service: ShortLinksServiceAbc = short_service
