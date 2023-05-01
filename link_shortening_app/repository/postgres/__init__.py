import glob
import os

from ..repository import Repository
from .short_link import ShortLinkRepo


def create_repo(db) -> Repository:
    short_link_repo = ShortLinkRepo(db_connection=db)

    repo = Repository(short_link=short_link_repo)

    return repo


def database_up(db, path_to_sql) -> None:
    with db.cursor() as cursor:
        for sql_path in glob.glob(os.path.join(path_to_sql, "*.sql")):
            with open(sql_path, "r") as sql_file:
                cursor.execute(sql_file.read())
    db.commit()


__all__ = [
    create_repo,
    database_up
]