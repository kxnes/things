import pytest
import unittest

from urllib.parse import urlencode

from . import application
from .models import THINGS
from .config import AUTH_TOKEN_VALUE


client = application.test_client()
unit_test_client = unittest.TestCase()

# mocking by clear <-> extend
THINGS.clear()
THINGS.extend([[0, '0000007923'], [1, '0000001485'], [2, '0000000890'], [3, '0000006293'], [4, '0000001108']])


def auth_request(token=AUTH_TOKEN_VALUE, params=None):
    query_string = f'?{urlencode(params)}' if params is not None else ''
    return client.get(f'/api/v1.0/things/{query_string}', headers={'X-Semrush-Test': token})


class TestTokenAuthRequires:
    def test_token_auth_correct(self):
        response = auth_request(AUTH_TOKEN_VALUE)
        assert response.status_code == 200

    def test_token_auth_forbidden(self):
        response = auth_request('Invalid-Token')
        assert response.status_code == 403


class TestSimpleFiltering:
    def test_without_filtering(self):
        response = auth_request()
        unit_test_client.assertListEqual(response.get_json()['paginated_things'], THINGS)

    @pytest.mark.parametrize(('from_', 'expected'), [
        # ignore minus values
        (-1,    [[0, '0000007923'], [1, '0000001485'], [2, '0000000890'], [3, '0000006293'], [4, '0000001108']]),
        (0,     [[0, '0000007923'], [1, '0000001485'], [2, '0000000890'], [3, '0000006293'], [4, '0000001108']]),
        ('1',   [[1, '0000001485'], [2, '0000000890'], [3, '0000006293'], [4, '0000001108']]),
        # ignore none `int` values
        ('two', [[0, '0000007923'], [1, '0000001485'], [2, '0000000890'], [3, '0000006293'], [4, '0000001108']]),
        (3,     [[3, '0000006293'], [4, '0000001108']]),
        (4,     [[4, '0000001108'], ]),
        (1000,  []),
    ])
    def test_filtering_from_id_condition(self, from_, expected):
        response = auth_request(params={'from': from_})
        unit_test_client.assertListEqual(response.get_json()['paginated_things'], expected)

    @pytest.mark.parametrize(('to', 'expected'), [
        # ignore minus values
        (-1,    [[0, '0000007923'], [1, '0000001485'], [2, '0000000890'], [3, '0000006293'], [4, '0000001108']]),
        (0,     [[0, '0000007923'], [1, '0000001485'], [2, '0000000890'], [3, '0000006293'], [4, '0000001108']]),
        ('1',   [[0, '0000007923'], [1, '0000001485']]),
        # ignore invalid `int`
        ('two', [[0, '0000007923'], [1, '0000001485'], [2, '0000000890'], [3, '0000006293'], [4, '0000001108']]),
        (1000,  [[0, '0000007923'], [1, '0000001485'], [2, '0000000890'], [3, '0000006293'], [4, '0000001108']]),
    ])
    def test_filtering_to_id_condition(self, to, expected):
        response = auth_request(params={'to': to})
        unit_test_client.assertListEqual(response.get_json()['paginated_things'], expected)

    @pytest.mark.parametrize(('msg', 'expected'), [
        ('08', [[2, '0000000890'], [4, '0000001108']]),
        (1,    [[1, '0000001485'], [4, '0000001108']]),
        ('',   [[0, '0000007923'], [1, '0000001485'], [2, '0000000890'], [3, '0000006293'], [4, '0000001108']])
    ])
    def test_filtering_message_contains_condition(self, msg, expected):
        response = auth_request(params={'msg': msg})
        unit_test_client.assertListEqual(response.get_json()['paginated_things'], expected)


class TestSimpleSorting:
    @pytest.mark.parametrize(('sort_key', 'expected'), [
        ('sort_id',   [[0, '0000007923'], [1, '0000001485'], [2, '0000000890'], [3, '0000006293'], [4, '0000001108']]),
        ('sort_msg',  [[2, '0000000890'], [4, '0000001108'], [1, '0000001485'], [3, '0000006293'], [0, '0000007923']]),
        ('rsort_id',  [[4, '0000001108'], [3, '0000006293'], [2, '0000000890'], [1, '0000001485'], [0, '0000007923']]),
        ('rsort_msg', [[0, '0000007923'], [3, '0000006293'], [1, '0000001485'], [4, '0000001108'], [2, '0000000890']]),
    ])
    def test_sorting(self, sort_key, expected):
        response = auth_request(params={sort_key: None})
        unit_test_client.assertListEqual(response.get_json()['paginated_things'], expected)


class TestSimplePaginating:
    @pytest.mark.parametrize(('page', 'expected'), [
        # pagination starts from `1`, invalid case
        (0,     [[0, '0000007923'], [1, '0000001485'], [2, '0000000890'], [3, '0000006293'], [4, '0000001108']]),
        ('1',   [[0, '0000007923'], [1, '0000001485'], [2, '0000000890'], [3, '0000006293'], [4, '0000001108']]),
        # ignore invalid `int`
        ('two', [[0, '0000007923'], [1, '0000001485'], [2, '0000000890'], [3, '0000006293'], [4, '0000001108']]),
    ])
    def test_paginating(self, page, expected):
        response = auth_request(params={'page': page})
        unit_test_client.assertListEqual(response.get_json()['paginated_things'], expected)

    def test_page_not_found(self):
        response = auth_request(params={'page': 2})
        assert response.status_code == 404
