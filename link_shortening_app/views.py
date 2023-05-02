import json

from http import HTTPStatus
from typing import Any

import validators as validators
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

from link_shortening_app.models import ShortLink
from link_shortening_app.services import Service
from link_shortening_app.services.short_link_service import UniqueShortLinkError


def construct_blueprint(services: Service):
    """
    Idea from https://stackoverflow.com/a/28641093
    :param services:
    :return:
    """
    # Create "group" of urls instance
    bp = Blueprint(name='main', import_name=__name__, url_prefix='/v1/short-links')

    @bp.route('/getAllShortLinks', methods=['GET'])
    @cross_origin()
    def get_all_short_links() -> Any:
        """
        Return list of ALL short links records
        :return: [{hash, title, date_create, date_update},..]

        Responses:
        200 - success
        """
        short_links = services.short_service.get_all_short_links()

        serialized_short_links = [o.to_dict() for o in short_links]

        return jsonify(serialized_short_links)

    @bp.route('/generateShortLinkFromUrl', methods=['POST'])
    @cross_origin()
    def generate_short_link_from_url() -> Any:
        """
        Get full url address and title, generate new hash for this address, save to repository and return to user
        :return: new short link instance

        Responses:
        - 400 - request have no title key or url key
        - 409 - url already exist in db
        - 403 - validation error
        - 200 - success
        """
        data = request.get_json()
        if "url" not in data or "title" not in data:
            return "\"Url\" key or \"Title\" key must be in request body", HTTPStatus.BAD_REQUEST

        url = data["url"]
        title = data["title"]

        # Validate data
        if len(title) >= 64 or not validators.url(url):
            return f"Validation error: title must be less 64 symbols, url must be valid", HTTPStatus.FORBIDDEN

        try:
            new_short_link = services.short_service.create_short_link(url=url, title=title)
        except UniqueShortLinkError:
            return f"Url address already exist in database", HTTPStatus.CONFLICT

        return jsonify(new_short_link.to_dict()), HTTPStatus.OK

    @bp.route('/changeShortLinkInfo', methods=['PUT'])
    @cross_origin()
    def change_short_link_info():
        """
        Change record info (title only), getting hash
        :return: Updated short link instance

        Responses:
        - 400 - request have no title key or hash key +
        - 404 - record with hash was not found +
        - 403 - validation error +
        - 200 - success
        """
        data = request.get_json()
        if "hash" not in data or "title" not in data:
            return "\"Url\" key or \"Title\" key must be in request body", HTTPStatus.BAD_REQUEST

        title = data["title"]
        hash_str = data["hash"]

        # Validate data
        if len(title) >= 64:
            return f"Validation error: title must be less 64 symbols", HTTPStatus.FORBIDDEN

        short_link: ShortLink = services.short_service.get_short_link_by_hash(hash_str)

        if short_link is None:
            return f"Link by hash \"{hash_str}\" was not found!", HTTPStatus.NOT_FOUND

        short_link.title = title

        updated_short_link: ShortLink = services.short_service.update_short_link(short_link)

        return jsonify(updated_short_link.to_dict()), HTTPStatus.OK

    @bp.route('/deleteShortLink', methods=['DELETE'])
    @cross_origin()
    def delete_short_link():
        """
        Remove record from application, getting hash
        :return:

        Responses:
        - 400 - request have no hash key
        - 404 - record with hash was not found
        - 200 - success
        """
        data = request.get_json()
        if "hash" not in data:
            return "\"Hash\" key must be in request body", HTTPStatus.BAD_REQUEST
        hash_str = data["hash"]

        deleted_short_link = services.short_service.delete_short_link(hash_str)

        if deleted_short_link is None:
            return f"Link by hash \"{hash_str}\" was not found!", HTTPStatus.NOT_FOUND

        return "Record was deleted success!", HTTPStatus.OK

    @bp.route('/getShortLinkByHash', methods=['POST'])
    @cross_origin()
    def get_short_link_by_hash():
        """
        Return full url by hash
        body must contain "hash" key
        :return: str, error

        Responses:
        - 400 - request have no hash key
        - 404 - record with hash was not found
        - 200 - success
        """
        data = request.get_json()
        
        if "hash" not in data:
            return "\"Hash\" key must be in request body", HTTPStatus.BAD_REQUEST
        hash_str = data["hash"]

        short_link: ShortLink = services.short_service.get_short_link_by_hash(hash_str)

        if short_link is None:
            return f"Link by hash \"{hash_str}\" was not found!", HTTPStatus.NOT_FOUND
        return jsonify(short_link.to_dict()), HTTPStatus.OK

    return bp
