from typing import List, Union

import psycopg2
from psycopg2.extras import DictCursor

from link_shortening_app.models import ShortLink
from link_shortening_app.repository import ShortLinkRepoAbc


class BaseShortLinkRepoError(Exception):
    pass


class UniqueRepoError(BaseShortLinkRepoError):
    pass


class StringDataRepoError(BaseShortLinkRepoError):
    pass


class ShortLinkRepo(ShortLinkRepoAbc):
    __slots__ = ["db_connection", "table_name"]

    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.table_name = "short_link"

    def create(self, title: str, url: str, hash_str: str) -> Union[ShortLink, None]:
        try:
            with self.db_connection.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(
                    f"INSERT INTO {self.table_name} (title, url, hash_str) VALUES(%s, %s, %s) RETURNING *;",
                    (title, url, hash_str)
                )
                self.db_connection.commit()

            short_link = self.get_by_hash(hash_str)
            return short_link
        except psycopg2.errors.UniqueViolation:
            # If url already exist in db
            self.db_connection.rollback()
            raise UniqueRepoError("Duplicate key value violates")
        except psycopg2.errors.StringDataRightTruncation:
            # If url too long for db record
            self.db_connection.rollback()
            raise StringDataRepoError("Value too long for db record")

    def update(self, short_link: ShortLink):
        with self.db_connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(
                f"UPDATE {self.table_name} SET title=%s WHERE hash_str=%s RETURNING *;",
                (short_link.title, short_link.hash_str)
            )
            record = cursor.fetchone()
            self.db_connection.commit()

        if record is None:
            return None
        data = dict(record)
        updated_short_link = ShortLink(**data)
        return updated_short_link

    def delete(self, hash_str: str) -> Union[ShortLink, None]:
        with self.db_connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(f"DELETE FROM {self.table_name} WHERE hash_str=%s RETURNING *;", (hash_str,))
            record = cursor.fetchone()
            self.db_connection.commit()

        if record is None:
            return None
        data = dict(record)
        deleted_short_link = ShortLink(**data)
        return deleted_short_link

    def get_by_hash(self, hash_str: str) -> Union[ShortLink, None]:
        with self.db_connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(f"SELECT * from {self.table_name} WHERE hash_str=%s", (hash_str,))
            record = cursor.fetchone()
        if record is None:
            return None
        data = dict(record)
        short_link = ShortLink(**data)

        return short_link

    def get_all(self) -> List[ShortLink]:
        with self.db_connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(f'SELECT * from {self.table_name}')
            rows = cursor.fetchall()

            result = []
            for row in rows:
                data = dict(row)
                short_link = ShortLink(**data)
                result.append(short_link)

        return result
