import hashlib
from typing import List, Union

from link_shortening_app.models import ShortLink
from link_shortening_app.repository import Repository
from link_shortening_app.repository.postgres.short_link import UniqueRepoError
from .services import ShortLinksServiceAbc


class BaseShortLinkError(Exception):
    pass


class UniqueShortLinkError(BaseShortLinkError):
    pass


class ShortLinksService(ShortLinksServiceAbc):
    __slots__ = ["repository"]

    def __init__(self, repository: Repository):
        self.repository = repository

    def get_all_short_links(self) -> List[ShortLink]:
        short_links: List[ShortLink] = self.repository.short_link.get_all()
        return short_links

    def get_short_link_by_hash(self, hash_str: str) -> Union[ShortLink, None]:
        short_link = self.repository.short_link.get_by_hash(hash_str)
        return short_link

    def update_short_link(self, short_link: ShortLink) -> ShortLink:
        updated_short_link = self.repository.short_link.update(short_link)
        return updated_short_link

    def create_short_link(self, title: str, url: str) -> ShortLink:
        # Generate hash for link
        hash_str = short_str_enc(url)
        try:
            short_link = self.repository.short_link.create(title=title, url=url, hash_str=hash_str)
        except UniqueRepoError:
            raise UniqueShortLinkError("Url already exist in db!")
        return short_link

    def delete_short_link(self, hash_str: str) -> Union[ShortLink, None]:
        deleted_short_link = self.repository.short_link.delete(hash_str)
        return deleted_short_link


enc_table_64 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def short_str_enc(s, char_length: int = 8, enc_table: str = enc_table_64) -> str:
    """
    Geneate string hash with given length, using specified encoding table.
    https://ivan-georgiev-19530.medium.com/generate-short-url-from-string-in-python-ac94e1e957ae
    """

    if char_length > 128:
        raise ValueError("char_length {} exceeds 128".format(char_length))
    hash_object = hashlib.sha512(s.encode())
    hash_hex = hash_object.hexdigest()
    hash_enc = int_to_enc(int(hash_hex, 16), enc_table)
    return hash_enc[0:char_length]


def int_to_enc(n, enc_table):
    """
    Encode integer into string, using digit encoding table.
    :param n:
    :param enc_table:
    :return:
    """
    if n == 0:
        return enc_table[0]
    base = len(enc_table)
    digits = ""
    while n:
        digits += enc_table[int(n % base)]
        n //= base
    return digits[::-1]