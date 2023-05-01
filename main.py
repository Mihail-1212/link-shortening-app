import argparse
import atexit
import os
from configparser import ConfigParser
from distutils.util import strtobool
from typing import Dict

import psycopg2
from flask import Flask
from flask.cli import load_dotenv
from flask_cors import CORS

from link_shortening_app.repository import Repository
from link_shortening_app.repository.postgres import create_repo, database_up
from link_shortening_app.services import Service, ShortLinksService


PROJECT_ROOT = os.path.dirname(__file__)


def get_db_config(filename='database.ini', section='postgresql') -> Dict[str, str]:
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


def create_services(repository: Repository) -> Service:
    service = Service(short_service=ShortLinksService(repository=repository))
    return service


def register_views(app: Flask, services: Service) -> None:
    # Register main views
    from link_shortening_app.views import construct_blueprint
    app.register_blueprint(construct_blueprint(services))


def create_app(services: Service) -> Flask:
    # Init flask application
    app = Flask(__name__)

    CORS(app)

    # Register views and urls
    register_views(app, services)

    return app


def create_console_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Flask commands')
    parser.add_argument('--migrate', help='migrate to database', nargs='?', const='')

    return parser


def main() -> None:
    """
    Main function of application
    :return:
    """
    # Load env variables from .env file
    load_dotenv()

    # Get command line args
    parser = create_console_parser()
    args = parser.parse_args()

    # Get connection parameters
    db_params = get_db_config()

    # Create db connection
    db = psycopg2.connect(**db_params)

    # Create repository
    repository = create_repo(db)

    # Create services
    services = create_services(repository)

    # Create flask app
    app = create_app(services)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    debug_mode: bool = bool(strtobool(os.getenv("DEBUG", "False")))
    host = os.getenv("HOST")
    port = os.getenv("PORT")

    def exit_flask_app():
        # Close db connection on program quit
        db.close()

    atexit.register(exit_flask_app)

    if args.migrate is not None and strtobool(args.migrate):
        # if run app with --migrate arg => migrate to database
        database_up(db, os.path.join(PROJECT_ROOT, 'schema'))
        print("Database has been successfully updated")
        return
    # Run flask application
    app.run(host=host, port=port, debug=debug_mode)


if __name__ == "__main__":
    main()
