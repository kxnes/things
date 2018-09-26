from flask import request, jsonify, abort

from .config import AUTH_TOKEN_HEADER, AUTH_TOKEN_VALUE, PER_PAGE
from .utils import check_uint_param


def token_auth_requires(func):
    def wrapper():
        token = request.headers.get(AUTH_TOKEN_HEADER)
        if token is None or token != AUTH_TOKEN_VALUE:
            abort(403)
        return func()
    return wrapper


def simple_filtering(func):
    """
    Filtering by range and message contains.
    Filter by `range()` include the right border.
    If `from_` > `to` - use standard behavior of `range()` function and return empty list.
    """
    def wrapper():
        things = func().json

        # filtering conditions
        from_ = check_uint_param(request.args.get('from'), default=0)
        to = check_uint_param(request.args.get('to'), default=len(things))
        msg = request.args.get('msg', '')

        return jsonify(list(filter(lambda x: x[0] in range(from_, to + 1) and msg in x[1], things)))
    return wrapper


def simple_sorting(func):
    """
    Sorting by only one key. If passed multiple, then sorting will be by priority (from most to least):
        `sort_id` --> `sort_msg` --> `rsort_id` --> `rsort_msg`
    """
    def wrapper():
        things = func().json

        if request.args.get('sort_id') is not None:
            return jsonify(list(sorted(things, key=lambda x: x[0])))

        if request.args.get('sort_msg') is not None:
            return jsonify(list(sorted(things, key=lambda x: x[1])))

        if request.args.get('rsort_id') is not None:
            return jsonify(list(sorted(things, key=lambda x: x[0], reverse=True)))

        if request.args.get('rsort_msg') is not None:
            return jsonify(list(sorted(things, key=lambda x: x[1], reverse=True)))

        return func()
    return wrapper


def simple_paginating(func):
    def wrapper():
        things = func().json
        total_things = len(things)
        # for cases when empty list of things or no data
        if total_things == 0:
            return jsonify({'total_items': total_things, 'paginated_things': things})

        # `-1` to compare list numeration from `0` and page numeration from `1`
        page = check_uint_param(request.args.get('page'), default=1) - 1

        start_index = page * PER_PAGE
        if start_index >= total_things:
            abort(404)

        return jsonify({'total_items': total_things, 'paginated_things': things[start_index:start_index + PER_PAGE]})
    return wrapper
